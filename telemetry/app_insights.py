"""
AppInsightsTelemetryService – Azure Monitor / Application Insights backend.

This implementation uses the ``azure-monitor-opentelemetry`` package, which is
Microsoft's official OpenTelemetry distribution for Azure Monitor.  It auto-
configures tracing, metrics, and logging exporters from a single connection
string.

Configuration keys (in ``config.json``):
  ``applicationinsights_connection_string`` (str, **required**) – App Insights
      connection string, e.g. ``"InstrumentationKey=...;IngestionEndpoint=..."``.
  ``otel_service_name`` (str, optional) – ``service.name`` resource attribute.
      Defaults to the ``sensor_name`` value.
"""

from __future__ import annotations

import logging
import traceback
from typing import Any

log = logging.getLogger(__name__)


class AppInsightsTelemetryService:
    """
    Telemetry backend that sends logs, traces, exceptions, and metrics to
    Azure Application Insights via the OpenTelemetry SDK.
    """

    def __init__(self, cfg: dict[str, Any]) -> None:
        connection_string: str = cfg.get("applicationinsights_connection_string", "")
        if not connection_string:
            raise ValueError(
                "Config key 'applicationinsights_connection_string' is required for "
                "telemetry_type='appinsights'."
            )

        service_name: str = cfg.get("otel_service_name") or cfg.get(
            "sensor_name", "virtual-test-harness"
        )

        # ── Configure Azure Monitor OpenTelemetry distro ─────────────────────
        from azure.monitor.opentelemetry import configure_azure_monitor
        from opentelemetry import metrics, trace
        from opentelemetry.sdk.resources import Resource

        resource = Resource.create({"service.name": service_name})

        configure_azure_monitor(
            connection_string=connection_string,
            resource=resource,
        )

        self._tracer = trace.get_tracer(service_name)
        self._meter = metrics.get_meter(service_name)
        self._metric_histograms: dict[str, Any] = {}

        log.info(
            "AppInsightsTelemetryService initialised: service=%s", service_name
        )

    # ── Public interface ──────────────────────────────────────────────────────

    def log(self, level: str, message: str, **kwargs: Any) -> None:
        """
        Emit a structured log entry.

        Azure Monitor picks up log records through the OTel log bridge that
        ``configure_azure_monitor`` installs on the root Python logger.  We
        therefore route through standard ``logging`` – the bridge forwards them
        to App Insights automatically.
        """
        _level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        numeric_level = _level_map.get(level.lower(), logging.INFO)
        extra_str = "  ".join(f"{k}={v!r}" for k, v in kwargs.items())
        full_message = f"{message}  {extra_str}".rstrip() if extra_str else message
        log.log(numeric_level, full_message)

    def track_event(self, name: str, properties: dict[str, Any] | None = None) -> None:
        """Record a named custom event as an OTel span (appears as a dependency/event in App Insights)."""
        props = properties or {}
        with self._tracer.start_as_current_span(name) as span:
            for k, v in props.items():
                span.set_attribute(k, str(v))

    def track_exception(
        self, exc: BaseException, properties: dict[str, Any] | None = None
    ) -> None:
        """Record an exception on the current or a new span (appears as an exception in App Insights)."""
        from opentelemetry import trace

        props = properties or {}
        with self._tracer.start_as_current_span("exception") as span:
            span.record_exception(exc, attributes={k: str(v) for k, v in props.items()})
            span.set_status(trace.StatusCode.ERROR, str(exc))
        # Mirror to standard logging (also forwarded to App Insights by the log bridge).
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        log.error("EXCEPTION %s: %s\n%s", type(exc).__name__, exc, tb)

    def track_metric(
        self,
        name: str,
        value: float,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """Record a measurement (appears as a custom metric in App Insights)."""
        props = properties or {}
        if name not in self._metric_histograms:
            self._metric_histograms[name] = self._meter.create_histogram(
                name=name,
                description=f"Metric: {name}",
            )
        self._metric_histograms[name].record(value, attributes=props)

    def flush(self) -> None:
        """
        Force-export all buffered telemetry.

        ``configure_azure_monitor`` registers its own tracer/meter providers; we
        flush them via the OTel global providers.
        """
        from opentelemetry import metrics, trace

        tracer_provider = trace.get_tracer_provider()
        meter_provider = metrics.get_meter_provider()

        if hasattr(tracer_provider, "force_flush"):
            tracer_provider.force_flush()
        if hasattr(meter_provider, "force_flush"):
            meter_provider.force_flush()
