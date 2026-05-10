"""
telemetry – OpenTelemetry-based observability for the virtual test harness.

Public API
----------
``TelemetryService``
    Protocol (interface) that all backend implementations satisfy.

``ConsoleTelemetryService``
    Default backend – wraps the standard Python :mod:`logging` module.
    Zero extra dependencies.

``OpenTelemetryService``
    Generic OTel SDK backend that exports via OTLP gRPC to any compatible
    collector (Jaeger, Grafana Tempo, OTel Collector, …).

``AppInsightsTelemetryService``
    Azure Monitor / Application Insights backend using the official
    ``azure-monitor-opentelemetry`` distribution.

``create_telemetry_service(cfg)``
    Factory function – reads ``telemetry_type`` from *cfg* and returns
    the appropriate :class:`TelemetryService` implementation.

Selecting a backend
-------------------
Set ``telemetry_type`` in ``config.json``:

``"console"`` (default)
    No extra dependencies; logs to stdout/file via Python logging.

``"opentelemetry"``
    Requires ``opentelemetry-sdk`` and ``opentelemetry-exporter-otlp-proto-grpc``.
    Also requires ``otel_exporter_endpoint`` in config.

``"appinsights"``
    Requires ``azure-monitor-opentelemetry``.
    Also requires ``applicationinsights_connection_string`` in config.
"""

from __future__ import annotations

import logging
from typing import Any

from .app_insights import AppInsightsTelemetryService
from .console import ConsoleTelemetryService
from .interface import TelemetryService
from .opentelemetry_service import OpenTelemetryService

__all__ = [
    "TelemetryService",
    "ConsoleTelemetryService",
    "OpenTelemetryService",
    "AppInsightsTelemetryService",
    "create_telemetry_service",
]

log = logging.getLogger(__name__)


def create_telemetry_service(cfg: dict[str, Any]) -> TelemetryService:
    """
    Instantiate and return the :class:`TelemetryService` specified in *cfg*.

    The selection key is ``telemetry_type`` (case-insensitive).  Recognised
    values:

    * ``"console"`` – :class:`ConsoleTelemetryService` (default / fallback).
    * ``"opentelemetry"`` – :class:`OpenTelemetryService`.
    * ``"appinsights"`` – :class:`AppInsightsTelemetryService`.

    Any unrecognised value falls back to :class:`ConsoleTelemetryService` with
    a warning.

    :param cfg: Application configuration dictionary (as loaded by
                ``app.load_config``).
    :returns: A fully initialised :class:`TelemetryService` implementation.
    """
    telemetry_type: str = cfg.get("telemetry_type", "console").lower()

    if telemetry_type == "opentelemetry":
        log.info("Telemetry backend: OpenTelemetry (OTLP)")
        return OpenTelemetryService(cfg)

    if telemetry_type == "appinsights":
        log.info("Telemetry backend: Azure Application Insights")
        return AppInsightsTelemetryService(cfg)

    if telemetry_type != "console":
        log.warning(
            "Unknown telemetry_type %r – falling back to 'console'.", telemetry_type
        )

    log.info("Telemetry backend: console (standard logging)")
    return ConsoleTelemetryService()
