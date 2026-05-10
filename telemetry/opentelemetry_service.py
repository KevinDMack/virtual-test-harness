"""
OpenTelemetryService – generic OpenTelemetry SDK backend with an OTLP exporter.

This implementation is suitable for any OpenTelemetry-compatible collector such
as Jaeger, Grafana Tempo, or a vendor-neutral OTel Collector.

Configuration keys (in ``config.json``):
  ``otel_exporter_endpoint`` (str) – OTLP gRPC endpoint, e.g.
      ``"http://otel-collector:4317"``.  Defaults to ``"http://localhost:4317"``.
  ``otel_service_name`` (str, optional) – ``service.name`` resource attribute.
      Defaults to the ``sensor_name`` value.
"""

from __future__ import annotations

import logging
import traceback
from typing import Any

log = logging.getLogger(__name__)


class OpenTelemetryService:
    """
    Telemetry backend that emits logs, events, exceptions, and metrics via the
    OpenTelemetry SDK, exporting to an OTLP gRPC endpoint.
    """

    def __init__(self, cfg: dict[str, Any]) -> None:
        endpoint: str = cfg.get("otel_exporter_endpoint", "http://localhost:4317")
        service_name: str = cfg.get("otel_service_name") or cfg.get(
            "sensor_name", "virtual-test-harness"
        )

        # ── OTel SDK imports ─────────────────────────────────────────────────
        from opentelemetry import metrics, trace
        from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
            OTLPLogExporter,
        )
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
            OTLPMetricExporter,
        )
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk._logs import LoggerProvider
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": service_name})

        # ── Tracing ──────────────────────────────────────────────────────────
        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
        )
        trace.set_tracer_provider(tracer_provider)
        self._tracer = trace.get_tracer(service_name)
        self._tracer_provider = tracer_provider

        # ── Metrics ──────────────────────────────────────────────────────────
        reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=endpoint))
        meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(meter_provider)
        self._meter = metrics.get_meter(service_name)
        self._meter_provider = meter_provider
        self._metric_gauges: dict[str, Any] = {}

        # ── Logs ─────────────────────────────────────────────────────────────
        logger_provider = LoggerProvider(resource=resource)
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(OTLPLogExporter(endpoint=endpoint))
        )
        self._otel_logger = logger_provider.get_logger(service_name)
        self._logger_provider = logger_provider

        log.info(
            "OpenTelemetryService initialised: service=%s endpoint=%s",
            service_name,
            endpoint,
        )

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _severity_number(self, level: str) -> int:
        """Map a level string to an OTel SeverityNumber integer."""
        from opentelemetry.sdk._logs.export import SeverityNumber  # type: ignore[attr-defined]

        mapping = {
            "debug": SeverityNumber.DEBUG,
            "info": SeverityNumber.INFO,
            "warning": SeverityNumber.WARN,
            "error": SeverityNumber.ERROR,
            "critical": SeverityNumber.FATAL,
        }
        return mapping.get(level.lower(), SeverityNumber.INFO)

    # ── Public interface ──────────────────────────────────────────────────────

    def log(self, level: str, message: str, **kwargs: Any) -> None:
        """Emit a structured log record via the OTel Logs SDK."""
        from opentelemetry.sdk._logs import LogRecord  # type: ignore[attr-defined]
        from opentelemetry._logs import SeverityNumber  # type: ignore[attr-defined]

        severity_map = {
            "debug": SeverityNumber.DEBUG,
            "info": SeverityNumber.INFO,
            "warning": SeverityNumber.WARN,
            "error": SeverityNumber.ERROR,
            "critical": SeverityNumber.FATAL,
        }
        severity = severity_map.get(level.lower(), SeverityNumber.INFO)

        body = message
        if kwargs:
            body = f"{message}  " + "  ".join(f"{k}={v!r}" for k, v in kwargs.items())

        self._otel_logger.emit(
            LogRecord(
                body=body,
                severity_number=severity,
                severity_text=level.upper(),
                attributes=kwargs or None,
            )
        )
        # Mirror to standard logging so local consoles still see output.
        _python_level = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }.get(level.lower(), logging.INFO)
        log.log(_python_level, message, **{} if not kwargs else {})

    def track_event(self, name: str, properties: dict[str, Any] | None = None) -> None:
        """Record a named event as an OTel span with the given properties."""
        props = properties or {}
        with self._tracer.start_as_current_span(name) as span:
            for k, v in props.items():
                span.set_attribute(k, str(v))

    def track_exception(
        self, exc: BaseException, properties: dict[str, Any] | None = None
    ) -> None:
        """Record an exception on the current or a new span."""
        from opentelemetry import trace

        props = properties or {}
        with self._tracer.start_as_current_span("exception") as span:
            span.record_exception(exc, attributes={k: str(v) for k, v in props.items()})
            span.set_status(trace.StatusCode.ERROR, str(exc))
        # Also log the traceback to standard logging.
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        log.error("EXCEPTION %s: %s\n%s", type(exc).__name__, exc, tb)

    def track_metric(
        self,
        name: str,
        value: float,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """Record a measurement via an OTel counter/histogram."""
        props = properties or {}
        # Re-use or create an UpDownCounter per metric name.
        if name not in self._metric_gauges:
            self._metric_gauges[name] = self._meter.create_histogram(
                name=name,
                description=f"Metric: {name}",
            )
        self._metric_gauges[name].record(value, attributes=props)

    def flush(self) -> None:
        """Force-export all pending telemetry."""
        self._tracer_provider.force_flush()
        self._meter_provider.force_flush()
        self._logger_provider.force_flush()
