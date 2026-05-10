"""Pytest configuration – mock Azure SDK and paho-mqtt modules before app.py is imported."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Stub out Azure SDK packages so app.py can be imported without the real SDKs
# installed in the test environment.  The stubs are plain MagicMocks; the tests
# that exercise Service Bus behaviour supply more specific mocks via patch().
# ---------------------------------------------------------------------------

_azure = MagicMock()
_azure_identity = MagicMock()
_azure_servicebus = MagicMock()

sys.modules.setdefault("azure", _azure)
sys.modules.setdefault("azure.identity", _azure_identity)
sys.modules.setdefault("azure.servicebus", _azure_servicebus)

# ---------------------------------------------------------------------------
# Stub out paho-mqtt so app.py can be imported without the real package.
# Tests that exercise MQTT behaviour supply more specific mocks via patch().
# ---------------------------------------------------------------------------

_paho = MagicMock()
_paho_mqtt = MagicMock()
_paho_mqtt_client = MagicMock()

# Expose CallbackAPIVersion as a real-enough enum-like attribute.
_paho_mqtt_client.CallbackAPIVersion = MagicMock()
_paho_mqtt_client.CallbackAPIVersion.VERSION2 = "VERSION2"

sys.modules.setdefault("paho", _paho)
sys.modules.setdefault("paho.mqtt", _paho_mqtt)
sys.modules.setdefault("paho.mqtt.client", _paho_mqtt_client)

# ---------------------------------------------------------------------------
# Stub out OpenTelemetry packages so telemetry modules can be imported without
# the real SDK installed.  Tests that exercise OTel behaviour supply more
# specific mocks via patch().
# ---------------------------------------------------------------------------

_otel_api = MagicMock()
_otel_sdk = MagicMock()
_otel_trace = MagicMock()
_otel_metrics = MagicMock()
_otel_logs = MagicMock()
_otel_sdk_trace = MagicMock()
_otel_sdk_metrics = MagicMock()
_otel_sdk_logs = MagicMock()
_otel_sdk_logs_export = MagicMock()
_otel_sdk_resources = MagicMock()
_otel_sdk_trace_export = MagicMock()
_otel_sdk_metrics_export = MagicMock()
_otel_exporter_otlp = MagicMock()
_otel_exporter_otlp_proto = MagicMock()
_otel_exporter_otlp_proto_grpc = MagicMock()
_otel_exporter_otlp_proto_grpc_trace = MagicMock()
_otel_exporter_otlp_proto_grpc_metric = MagicMock()
_otel_exporter_otlp_proto_grpc_log = MagicMock()

# SeverityNumber must be a real-enough object for isinstance / attribute access.
_severity_number = MagicMock()
for _attr in ("DEBUG", "INFO", "WARN", "ERROR", "FATAL"):
    setattr(_severity_number, _attr, _attr)
_otel_sdk_logs_export.SeverityNumber = _severity_number
_otel_logs.SeverityNumber = _severity_number

for mod_name, mock_obj in [
    ("opentelemetry", _otel_api),
    ("opentelemetry.trace", _otel_trace),
    ("opentelemetry.metrics", _otel_metrics),
    ("opentelemetry._logs", _otel_logs),
    ("opentelemetry.sdk", _otel_sdk),
    ("opentelemetry.sdk.trace", _otel_sdk_trace),
    ("opentelemetry.sdk.trace.export", _otel_sdk_trace_export),
    ("opentelemetry.sdk.metrics", _otel_sdk_metrics),
    ("opentelemetry.sdk.metrics.export", _otel_sdk_metrics_export),
    ("opentelemetry.sdk._logs", _otel_sdk_logs),
    ("opentelemetry.sdk._logs.export", _otel_sdk_logs_export),
    ("opentelemetry.sdk.resources", _otel_sdk_resources),
    ("opentelemetry.exporter", _otel_exporter_otlp),
    ("opentelemetry.exporter.otlp", _otel_exporter_otlp_proto),
    ("opentelemetry.exporter.otlp.proto", _otel_exporter_otlp_proto),
    ("opentelemetry.exporter.otlp.proto.grpc", _otel_exporter_otlp_proto_grpc),
    ("opentelemetry.exporter.otlp.proto.grpc.trace_exporter", _otel_exporter_otlp_proto_grpc_trace),
    ("opentelemetry.exporter.otlp.proto.grpc.metric_exporter", _otel_exporter_otlp_proto_grpc_metric),
    ("opentelemetry.exporter.otlp.proto.grpc._log_exporter", _otel_exporter_otlp_proto_grpc_log),
]:
    sys.modules.setdefault(mod_name, mock_obj)

# ---------------------------------------------------------------------------
# Stub out azure-monitor-opentelemetry so app_insights.py can be imported
# without the real package installed.
# ---------------------------------------------------------------------------

_azure_monitor = MagicMock()
_azure_monitor_opentelemetry = MagicMock()

sys.modules.setdefault("azure.monitor", _azure_monitor)
sys.modules.setdefault("azure.monitor.opentelemetry", _azure_monitor_opentelemetry)
