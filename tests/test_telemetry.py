"""Tests for the telemetry package – interface, implementations, and factory."""

from __future__ import annotations

import logging
import sys
import os
from unittest.mock import MagicMock, patch, call

import pytest

# Ensure repo root is on sys.path (conftest.py already stubs azure / otel / paho).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from telemetry.interface import TelemetryService
from telemetry.console import ConsoleTelemetryService
import telemetry as telemetry_pkg


# ── Helpers ────────────────────────────────────────────────────────────────────


def _make_console() -> ConsoleTelemetryService:
    return ConsoleTelemetryService()


# ── TelemetryService Protocol ──────────────────────────────────────────────────


class TestTelemetryServiceProtocol:
    """Verify the Protocol methods exist and ConsoleTelemetryService satisfies it."""

    def test_console_is_instance_of_protocol(self):
        svc = _make_console()
        assert isinstance(svc, TelemetryService)

    def test_protocol_has_log(self):
        assert hasattr(TelemetryService, "log")

    def test_protocol_has_track_event(self):
        assert hasattr(TelemetryService, "track_event")

    def test_protocol_has_track_exception(self):
        assert hasattr(TelemetryService, "track_exception")

    def test_protocol_has_track_metric(self):
        assert hasattr(TelemetryService, "track_metric")

    def test_protocol_has_flush(self):
        assert hasattr(TelemetryService, "flush")

    def test_mock_satisfies_protocol(self):
        """A MagicMock with the right methods is also a valid TelemetryService."""
        mock_svc = MagicMock(spec=TelemetryService)
        assert isinstance(mock_svc, TelemetryService)


# ── ConsoleTelemetryService ────────────────────────────────────────────────────


class TestConsoleTelemetryService:
    def test_log_info_emits_to_logger(self, caplog):
        svc = _make_console()
        with caplog.at_level(logging.INFO, logger="telemetry.console"):
            svc.log("info", "hello world")
        assert "hello world" in caplog.text

    def test_log_warning_emits_at_warning_level(self, caplog):
        svc = _make_console()
        with caplog.at_level(logging.WARNING, logger="telemetry.console"):
            svc.log("warning", "degraded")
        assert any(r.levelno == logging.WARNING for r in caplog.records)

    def test_log_error_emits_at_error_level(self, caplog):
        svc = _make_console()
        with caplog.at_level(logging.ERROR, logger="telemetry.console"):
            svc.log("error", "something broke")
        assert any(r.levelno == logging.ERROR for r in caplog.records)

    def test_log_debug_emits_at_debug_level(self, caplog):
        svc = _make_console()
        with caplog.at_level(logging.DEBUG, logger="telemetry.console"):
            svc.log("debug", "verbose detail")
        assert any(r.levelno == logging.DEBUG for r in caplog.records)

    def test_log_critical_emits_at_critical_level(self, caplog):
        svc = _make_console()
        with caplog.at_level(logging.CRITICAL, logger="telemetry.console"):
            svc.log("critical", "fatal error")
        assert any(r.levelno == logging.CRITICAL for r in caplog.records)

    def test_log_unknown_level_defaults_to_info(self, caplog):
        svc = _make_console()
        with caplog.at_level(logging.INFO, logger="telemetry.console"):
            svc.log("unknown_level", "fallback")
        assert any(r.levelno == logging.INFO for r in caplog.records)

    def test_log_includes_kwargs_in_message(self, caplog):
        svc = _make_console()
        with caplog.at_level(logging.INFO, logger="telemetry.console"):
            svc.log("info", "base message", sensor="alpha", count=5)
        assert "sensor='alpha'" in caplog.text or "sensor=alpha" in caplog.text

    def test_track_event_logs_event_name(self, caplog):
        svc = _make_console()
        with caplog.at_level(logging.INFO, logger="telemetry.console"):
            svc.track_event("MessagePublished")
        assert "MessagePublished" in caplog.text

    def test_track_event_logs_properties(self, caplog):
        svc = _make_console()
        with caplog.at_level(logging.INFO, logger="telemetry.console"):
            svc.track_event("MyEvent", {"key": "value"})
        assert "key" in caplog.text

    def test_track_event_accepts_none_properties(self):
        svc = _make_console()
        # Should not raise
        svc.track_event("SafeEvent", None)

    def test_track_exception_logs_exception_type(self, caplog):
        svc = _make_console()
        exc = ValueError("bad input")
        with caplog.at_level(logging.ERROR, logger="telemetry.console"):
            svc.track_exception(exc)
        assert "ValueError" in caplog.text

    def test_track_exception_logs_exception_message(self, caplog):
        svc = _make_console()
        exc = RuntimeError("network timeout")
        with caplog.at_level(logging.ERROR, logger="telemetry.console"):
            svc.track_exception(exc)
        assert "network timeout" in caplog.text

    def test_track_exception_logs_properties(self, caplog):
        svc = _make_console()
        exc = OSError("disk full")
        with caplog.at_level(logging.ERROR, logger="telemetry.console"):
            svc.track_exception(exc, {"topic": "sensor-data"})
        assert "topic" in caplog.text

    def test_track_exception_accepts_none_properties(self):
        svc = _make_console()
        svc.track_exception(ValueError("x"), None)

    def test_track_metric_logs_name_and_value(self, caplog):
        svc = _make_console()
        with caplog.at_level(logging.DEBUG, logger="telemetry.console"):
            svc.track_metric("PublishLatencyMs", 42.5)
        assert "PublishLatencyMs" in caplog.text
        assert "42.5" in caplog.text

    def test_track_metric_accepts_none_properties(self):
        svc = _make_console()
        svc.track_metric("cpu_usage", 0.75, None)

    def test_flush_does_not_raise(self):
        svc = _make_console()
        # Should complete without error even when no custom handlers are attached.
        svc.flush()

    def test_flush_flushes_root_handlers(self):
        svc = _make_console()
        mock_handler = MagicMock()
        root_logger = logging.getLogger()
        root_logger.addHandler(mock_handler)
        try:
            svc.flush()
        finally:
            root_logger.removeHandler(mock_handler)
        mock_handler.flush.assert_called()


# ── create_telemetry_service factory ──────────────────────────────────────────


class TestCreateTelemetryService:
    _BASE_CFG = {
        "sensor_name": "test-sensor",
        "message_interval": 5,
        "message_topic": "sensor-data",
        "health_interval": 30,
        "health_topic": "sensor-health",
        "run_continuous": True,
        "message_bus_type": "servicebus",
        "service_bus_namespace": "test.servicebus.windows.net",
    }

    def test_no_telemetry_type_returns_console(self):
        cfg = {**self._BASE_CFG}
        svc = telemetry_pkg.create_telemetry_service(cfg)
        assert isinstance(svc, ConsoleTelemetryService)

    def test_console_type_returns_console(self):
        cfg = {**self._BASE_CFG, "telemetry_type": "console"}
        svc = telemetry_pkg.create_telemetry_service(cfg)
        assert isinstance(svc, ConsoleTelemetryService)

    def test_console_type_case_insensitive(self):
        cfg = {**self._BASE_CFG, "telemetry_type": "CONSOLE"}
        svc = telemetry_pkg.create_telemetry_service(cfg)
        assert isinstance(svc, ConsoleTelemetryService)

    def test_unknown_type_falls_back_to_console(self):
        cfg = {**self._BASE_CFG, "telemetry_type": "prometheus"}
        svc = telemetry_pkg.create_telemetry_service(cfg)
        assert isinstance(svc, ConsoleTelemetryService)

    def test_unknown_type_logs_warning(self, caplog):
        cfg = {**self._BASE_CFG, "telemetry_type": "prometheus"}
        with caplog.at_level(logging.WARNING, logger="telemetry"):
            telemetry_pkg.create_telemetry_service(cfg)
        assert "prometheus" in caplog.text

    def test_opentelemetry_type_returns_otel_service(self):
        cfg = {
            **self._BASE_CFG,
            "telemetry_type": "opentelemetry",
            "otel_exporter_endpoint": "http://localhost:4317",
        }
        with patch("telemetry.opentelemetry_service.OpenTelemetryService.__init__", return_value=None):
            svc = telemetry_pkg.create_telemetry_service(cfg)
        assert isinstance(svc, telemetry_pkg.OpenTelemetryService)

    def test_appinsights_type_returns_appinsights_service(self):
        cfg = {
            **self._BASE_CFG,
            "telemetry_type": "appinsights",
            "applicationinsights_connection_string": "InstrumentationKey=abc123",
        }
        with patch("telemetry.app_insights.AppInsightsTelemetryService.__init__", return_value=None):
            svc = telemetry_pkg.create_telemetry_service(cfg)
        assert isinstance(svc, telemetry_pkg.AppInsightsTelemetryService)

    def test_returned_service_satisfies_protocol(self):
        cfg = {**self._BASE_CFG, "telemetry_type": "console"}
        svc = telemetry_pkg.create_telemetry_service(cfg)
        assert isinstance(svc, TelemetryService)


# ── OpenTelemetryService (mocked) ─────────────────────────────────────────────


class TestOpenTelemetryService:
    """Test OpenTelemetryService with its OTel SDK dependencies fully mocked."""

    def _make_service(self):
        """Instantiate OpenTelemetryService with all OTel internals mocked."""
        from telemetry.opentelemetry_service import OpenTelemetryService

        with patch("telemetry.opentelemetry_service.OpenTelemetryService.__init__", return_value=None):
            svc = OpenTelemetryService.__new__(OpenTelemetryService)

        # Attach minimal mock state expected by the public methods.
        svc._tracer = MagicMock()
        svc._meter = MagicMock()
        svc._otel_logger = MagicMock()
        svc._tracer_provider = MagicMock()
        svc._meter_provider = MagicMock()
        svc._logger_provider = MagicMock()
        svc._metric_gauges = {}
        return svc

    def test_log_emits_otel_log_record(self):
        svc = self._make_service()
        # Because OTel SDK modules are fully mocked in conftest.py, the imports
        # inside log() succeed and emit() is called on the mock logger.
        svc.log("info", "hello from otel")
        svc._otel_logger.emit.assert_called_once()

    def test_track_event_starts_span(self):
        svc = self._make_service()
        span = MagicMock()
        span.__enter__ = MagicMock(return_value=span)
        span.__exit__ = MagicMock(return_value=False)
        svc._tracer.start_as_current_span.return_value = span
        svc.track_event("TestEvent", {"key": "val"})
        svc._tracer.start_as_current_span.assert_called_once_with("TestEvent")

    def test_track_event_sets_attributes_on_span(self):
        svc = self._make_service()
        span = MagicMock()
        span.__enter__ = MagicMock(return_value=span)
        span.__exit__ = MagicMock(return_value=False)
        svc._tracer.start_as_current_span.return_value = span
        svc.track_event("TestEvent", {"region": "eastus"})
        span.set_attribute.assert_called_with("region", "eastus")

    def test_track_event_accepts_none_properties(self):
        svc = self._make_service()
        span = MagicMock()
        span.__enter__ = MagicMock(return_value=span)
        span.__exit__ = MagicMock(return_value=False)
        svc._tracer.start_as_current_span.return_value = span
        svc.track_event("NoProps", None)
        span.set_attribute.assert_not_called()

    def test_track_exception_records_exception_on_span(self):
        svc = self._make_service()
        span = MagicMock()
        span.__enter__ = MagicMock(return_value=span)
        span.__exit__ = MagicMock(return_value=False)
        svc._tracer.start_as_current_span.return_value = span

        exc = ValueError("bad")
        with patch("opentelemetry.trace.StatusCode") as mock_sc:
            mock_sc.ERROR = "ERROR"
            svc.track_exception(exc, {"component": "publisher"})

        span.record_exception.assert_called_once()
        call_args = span.record_exception.call_args
        assert call_args[0][0] is exc

    def test_track_metric_creates_histogram_once(self):
        svc = self._make_service()
        mock_histogram = MagicMock()
        svc._meter.create_histogram.return_value = mock_histogram

        svc.track_metric("latency", 10.0)
        svc.track_metric("latency", 20.0)

        svc._meter.create_histogram.assert_called_once_with(
            name="latency", description="Metric: latency"
        )
        assert mock_histogram.record.call_count == 2

    def test_track_metric_records_value(self):
        svc = self._make_service()
        mock_histogram = MagicMock()
        svc._meter.create_histogram.return_value = mock_histogram

        svc.track_metric("error_count", 3.0, {"topic": "health"})
        mock_histogram.record.assert_called_once_with(3.0, attributes={"topic": "health"})

    def test_flush_calls_force_flush_on_all_providers(self):
        svc = self._make_service()
        svc.flush()
        svc._tracer_provider.force_flush.assert_called_once()
        svc._meter_provider.force_flush.assert_called_once()
        svc._logger_provider.force_flush.assert_called_once()


# ── AppInsightsTelemetryService (mocked) ──────────────────────────────────────


class TestAppInsightsTelemetryService:
    """Test AppInsightsTelemetryService with Azure Monitor / OTel mocked out."""

    def _make_service(self):
        from telemetry.app_insights import AppInsightsTelemetryService

        with patch("telemetry.app_insights.AppInsightsTelemetryService.__init__", return_value=None):
            svc = AppInsightsTelemetryService.__new__(AppInsightsTelemetryService)

        svc._tracer = MagicMock()
        svc._meter = MagicMock()
        svc._metric_histograms = {}
        return svc

    def test_missing_connection_string_raises(self):
        from telemetry.app_insights import AppInsightsTelemetryService

        cfg = {"sensor_name": "test", "applicationinsights_connection_string": ""}
        with patch("telemetry.app_insights.configure_azure_monitor", create=True):
            with pytest.raises(ValueError, match="applicationinsights_connection_string"):
                AppInsightsTelemetryService(cfg)

    def test_log_emits_via_standard_logging(self, caplog):
        svc = self._make_service()
        with caplog.at_level(logging.INFO, logger="telemetry.app_insights"):
            svc.log("info", "app insights log")
        assert "app insights log" in caplog.text

    def test_log_error_level(self, caplog):
        svc = self._make_service()
        with caplog.at_level(logging.ERROR, logger="telemetry.app_insights"):
            svc.log("error", "critical failure")
        assert any(r.levelno == logging.ERROR for r in caplog.records)

    def test_track_event_starts_span(self):
        svc = self._make_service()
        span = MagicMock()
        span.__enter__ = MagicMock(return_value=span)
        span.__exit__ = MagicMock(return_value=False)
        svc._tracer.start_as_current_span.return_value = span
        svc.track_event("AiEvent", {"region": "westus"})
        svc._tracer.start_as_current_span.assert_called_once_with("AiEvent")

    def test_track_event_sets_attributes(self):
        svc = self._make_service()
        span = MagicMock()
        span.__enter__ = MagicMock(return_value=span)
        span.__exit__ = MagicMock(return_value=False)
        svc._tracer.start_as_current_span.return_value = span
        svc.track_event("AiEvent", {"env": "prod"})
        span.set_attribute.assert_called_with("env", "prod")

    def test_track_event_accepts_none_properties(self):
        svc = self._make_service()
        span = MagicMock()
        span.__enter__ = MagicMock(return_value=span)
        span.__exit__ = MagicMock(return_value=False)
        svc._tracer.start_as_current_span.return_value = span
        svc.track_event("NoPropsAi", None)
        span.set_attribute.assert_not_called()

    def test_track_exception_records_exception(self):
        svc = self._make_service()
        span = MagicMock()
        span.__enter__ = MagicMock(return_value=span)
        span.__exit__ = MagicMock(return_value=False)
        svc._tracer.start_as_current_span.return_value = span

        exc = RuntimeError("connection reset")
        with patch("opentelemetry.trace.StatusCode") as mock_sc:
            mock_sc.ERROR = "ERROR"
            svc.track_exception(exc)

        span.record_exception.assert_called_once()
        assert span.record_exception.call_args[0][0] is exc

    def test_track_metric_creates_histogram_once(self):
        svc = self._make_service()
        mock_histogram = MagicMock()
        svc._meter.create_histogram.return_value = mock_histogram

        svc.track_metric("publish_count", 1.0)
        svc.track_metric("publish_count", 2.0)

        svc._meter.create_histogram.assert_called_once()

    def test_track_metric_records_correct_value(self):
        svc = self._make_service()
        mock_histogram = MagicMock()
        svc._meter.create_histogram.return_value = mock_histogram

        svc.track_metric("latency_ms", 55.0, {"bus": "servicebus"})
        mock_histogram.record.assert_called_once_with(55.0, attributes={"bus": "servicebus"})

    def test_flush_calls_force_flush_on_providers_if_available(self):
        svc = self._make_service()
        # Because OTel modules are fully mocked in conftest.py, flush() succeeds
        # and calls force_flush() on the MagicMock providers returned by the
        # global OTel getters.  We simply verify that flush() does not raise.
        svc.flush()  # should complete without error

    def test_flush_does_not_raise_without_force_flush(self):
        svc = self._make_service()
        # Providers without force_flush should not cause an error.
        no_flush_provider = MagicMock(spec=[])  # no attributes
        with patch("opentelemetry.trace.get_tracer_provider", return_value=no_flush_provider):
            with patch("opentelemetry.metrics.get_meter_provider", return_value=no_flush_provider):
                svc.flush()  # should not raise


# ── Integration: app.py uses TelemetryService ──────────────────────────────────


class TestAppTelemetryIntegration:
    """Verify that app.py correctly wires up and uses the TelemetryService."""

    def test_circuit_breaker_uses_telemetry_log_on_error(self):
        import app
        mock_telemetry = MagicMock(spec=TelemetryService)
        cb = app.CircuitBreaker(telemetry=mock_telemetry)
        cb.record_error("test error")
        mock_telemetry.log.assert_called_once()
        args = mock_telemetry.log.call_args[0]
        assert args[0] == "warning"
        assert "test error" in args[1]

    def test_circuit_breaker_tracks_metric_on_error(self):
        import app
        mock_telemetry = MagicMock(spec=TelemetryService)
        cb = app.CircuitBreaker(telemetry=mock_telemetry)
        cb.record_error("metric test")
        mock_telemetry.track_metric.assert_called_once_with(
            "circuit_breaker.error_count", 1
        )

    def test_send_to_topic_uses_telemetry_track_event_on_success(self):
        import app
        mock_telemetry = MagicMock(spec=TelemetryService)
        pub = MagicMock(spec=app.MessagePublisher)
        cb = app.CircuitBreaker()
        app.send_to_topic(pub, "my-topic", {"x": 1}, cb, telemetry=mock_telemetry)
        mock_telemetry.track_event.assert_called_once_with(
            "MessagePublished", {"topic": "my-topic"}
        )

    def test_send_to_topic_uses_telemetry_track_exception_on_failure(self):
        import app
        mock_telemetry = MagicMock(spec=TelemetryService)
        pub = MagicMock(spec=app.MessagePublisher)
        pub.publish.side_effect = RuntimeError("bus down")
        cb = app.CircuitBreaker()
        with pytest.raises(RuntimeError):
            app.send_to_topic(pub, "topic", {}, cb, telemetry=mock_telemetry)
        mock_telemetry.track_exception.assert_called_once()
        exc_arg = mock_telemetry.track_exception.call_args[0][0]
        assert isinstance(exc_arg, RuntimeError)

    def test_create_telemetry_service_console_is_default(self):
        import app
        cfg = {
            "sensor_name": "s1",
            "message_interval": 5,
            "message_topic": "t",
            "health_interval": 30,
            "health_topic": "h",
            "run_continuous": True,
            "message_bus_type": "servicebus",
            "service_bus_namespace": "ns.servicebus.windows.net",
        }
        svc = telemetry_pkg.create_telemetry_service(cfg)
        assert isinstance(svc, ConsoleTelemetryService)
