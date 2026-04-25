"""Automated tests for app.py – Synthetic Sensor Simulator."""

from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

# app.py lives at the repo root; conftest.py has already stubbed azure imports.
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app  # noqa: E402


# ── CircuitBreaker ─────────────────────────────────────────────────────────────


class TestCircuitBreaker:
    def _make_cb(self) -> app.CircuitBreaker:
        return app.CircuitBreaker()

    def test_initial_state_is_closed(self):
        cb = self._make_cb()
        assert cb.state == app.CircuitBreaker.CLOSED

    def test_initial_health_is_green(self):
        cb = self._make_cb()
        assert cb.health_status == "green"

    def test_is_open_false_initially(self):
        cb = self._make_cb()
        assert not cb.is_open

    def test_one_error_gives_half_open(self):
        cb = self._make_cb()
        cb.record_error("first error")
        assert cb.state == app.CircuitBreaker.HALF_OPEN

    def test_five_errors_stays_half_open(self):
        cb = self._make_cb()
        for i in range(5):
            cb.record_error(f"error {i}")
        assert cb.state == app.CircuitBreaker.HALF_OPEN

    def test_six_errors_gives_open(self):
        cb = self._make_cb()
        for i in range(6):
            cb.record_error(f"error {i}")
        assert cb.state == app.CircuitBreaker.OPEN

    def test_is_open_true_when_open(self):
        cb = self._make_cb()
        for i in range(6):
            cb.record_error(f"error {i}")
        assert cb.is_open

    def test_health_yellow_when_half_open(self):
        cb = self._make_cb()
        cb.record_error("degraded")
        assert cb.health_status == "yellow"

    def test_health_red_when_open(self):
        cb = self._make_cb()
        for i in range(6):
            cb.record_error(f"error {i}")
        assert cb.health_status == "red"

    def test_last_error_message_stored(self):
        cb = self._make_cb()
        cb.record_error("something went wrong")
        assert cb.last_error_message == "something went wrong"

    def test_last_error_message_updated_on_subsequent_errors(self):
        cb = self._make_cb()
        cb.record_error("first")
        cb.record_error("second")
        assert cb.last_error_message == "second"

    def test_record_success_does_not_change_state(self):
        cb = self._make_cb()
        cb.record_error("err")
        cb.record_success()
        assert cb.state == app.CircuitBreaker.HALF_OPEN

    def test_errors_purged_after_window(self):
        """Errors outside the sliding window should not count."""
        cb = self._make_cb()
        # Inject an error timestamp far in the past.
        past = time.monotonic() - (app._ERROR_WINDOW_SECONDS + 1)
        cb._error_times.append(past)
        # State should still be CLOSED because the old error is outside the window.
        assert cb.state == app.CircuitBreaker.CLOSED

    def test_circuit_recovers_when_window_clears(self):
        cb = self._make_cb()
        # Simulate 6 errors that are all just outside the window.
        past = time.monotonic() - (app._ERROR_WINDOW_SECONDS + 1)
        for _ in range(6):
            cb._error_times.append(past)
        assert cb.state == app.CircuitBreaker.CLOSED
        assert not cb.is_open


# ── load_config ────────────────────────────────────────────────────────────────


class TestLoadConfig:
    _VALID_CONFIG = {
        "sensor_name": "test-sensor",
        "message_interval": 5,
        "message_topic": "sensor-data",
        "health_interval": 30,
        "health_topic": "sensor-health",
        "run_continuous": True,
        "service_bus_namespace": "test.servicebus.windows.net",
    }

    def _write_config(self, tmp_path: Path, data: dict) -> Path:
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps(data))
        return cfg_file

    def test_valid_config_loads_all_keys(self, tmp_path):
        cfg_file = self._write_config(tmp_path, self._VALID_CONFIG)
        cfg = app.load_config(cfg_file)
        assert cfg == self._VALID_CONFIG

    def test_missing_required_key_raises_value_error(self, tmp_path):
        incomplete = {k: v for k, v in self._VALID_CONFIG.items() if k != "sensor_name"}
        cfg_file = self._write_config(tmp_path, incomplete)
        with pytest.raises(ValueError, match="sensor_name"):
            app.load_config(cfg_file)

    def test_all_required_keys_reported_when_missing(self, tmp_path):
        cfg_file = self._write_config(tmp_path, {})
        with pytest.raises(ValueError) as exc_info:
            app.load_config(cfg_file)
        msg = str(exc_info.value)
        assert "sensor_name" in msg
        assert "message_interval" in msg
        assert "service_bus_namespace" in msg

    def test_extra_keys_are_preserved(self, tmp_path):
        data = {**self._VALID_CONFIG, "extra_field": "extra_value"}
        cfg_file = self._write_config(tmp_path, data)
        cfg = app.load_config(cfg_file)
        assert cfg["extra_field"] == "extra_value"

    def test_invalid_json_raises(self, tmp_path):
        bad_file = tmp_path / "config.json"
        bad_file.write_text("not valid json {{{")
        with pytest.raises(json.JSONDecodeError):
            app.load_config(bad_file)


# ── load_inbox ─────────────────────────────────────────────────────────────────


class TestLoadInbox:
    def test_loads_list_json(self, tmp_path):
        payloads = [{"type": "temp", "value": 72.4}, {"type": "hum", "value": 58.1}]
        (tmp_path / "messages.json").write_text(json.dumps(payloads))
        result = app.load_inbox(tmp_path)
        assert result == payloads

    def test_loads_dict_json_wrapped_in_list(self, tmp_path):
        payload = {"type": "temp", "value": 72.4}
        (tmp_path / "messages.json").write_text(json.dumps(payload))
        result = app.load_inbox(tmp_path)
        assert result == [payload]

    def test_loads_multiple_files_sorted(self, tmp_path):
        (tmp_path / "a_messages.json").write_text(json.dumps([{"order": 1}]))
        (tmp_path / "b_messages.json").write_text(json.dumps([{"order": 2}]))
        result = app.load_inbox(tmp_path)
        assert result == [{"order": 1}, {"order": 2}]

    def test_empty_directory_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="No JSON files found"):
            app.load_inbox(tmp_path)

    def test_returns_flat_list_from_multiple_files(self, tmp_path):
        (tmp_path / "file1.json").write_text(json.dumps([{"x": 1}, {"x": 2}]))
        (tmp_path / "file2.json").write_text(json.dumps([{"x": 3}]))
        result = app.load_inbox(tmp_path)
        assert len(result) == 3
        assert result[2] == {"x": 3}


# ── build_sensor_message ───────────────────────────────────────────────────────


class TestBuildSensorMessage:
    def test_required_keys_present(self):
        msg = app.build_sensor_message("sensor-1", {"value": 42})
        assert set(msg.keys()) == {"sensor_name", "date_time", "correlation_id", "content"}

    def test_sensor_name_matches(self):
        msg = app.build_sensor_message("my-sensor", {"value": 1})
        assert msg["sensor_name"] == "my-sensor"

    def test_content_matches_input(self):
        content = {"reading_type": "temperature", "value": 21.5}
        msg = app.build_sensor_message("s1", content)
        assert msg["content"] == content

    def test_correlation_id_is_valid_uuid(self):
        msg = app.build_sensor_message("s1", {})
        # Should not raise
        parsed = uuid.UUID(msg["correlation_id"])
        assert str(parsed) == msg["correlation_id"]

    def test_each_call_has_unique_correlation_id(self):
        ids = {app.build_sensor_message("s1", {})["correlation_id"] for _ in range(10)}
        assert len(ids) == 10

    def test_date_time_is_utc_iso_format(self):
        msg = app.build_sensor_message("s1", {})
        # Should end with UTC offset indicator
        assert "+00:00" in msg["date_time"] or msg["date_time"].endswith("Z")


# ── build_health_message ───────────────────────────────────────────────────────


class TestBuildHealthMessage:
    def test_required_keys_present(self):
        cb = app.CircuitBreaker()
        msg = app.build_health_message("sensor-1", cb)
        assert set(msg.keys()) == {"sensor_name", "date_time", "status", "last_error_message"}

    def test_sensor_name_matches(self):
        cb = app.CircuitBreaker()
        msg = app.build_health_message("my-sensor", cb)
        assert msg["sensor_name"] == "my-sensor"

    def test_status_green_when_closed(self):
        cb = app.CircuitBreaker()
        msg = app.build_health_message("s1", cb)
        assert msg["status"] == "green"

    def test_status_yellow_when_half_open(self):
        cb = app.CircuitBreaker()
        cb.record_error("degraded")
        msg = app.build_health_message("s1", cb)
        assert msg["status"] == "yellow"

    def test_status_red_when_open(self):
        cb = app.CircuitBreaker()
        for i in range(6):
            cb.record_error(f"err {i}")
        msg = app.build_health_message("s1", cb)
        assert msg["status"] == "red"

    def test_last_error_message_reflected(self):
        cb = app.CircuitBreaker()
        cb.record_error("connection timeout")
        msg = app.build_health_message("s1", cb)
        assert msg["last_error_message"] == "connection timeout"

    def test_last_error_message_empty_when_no_errors(self):
        cb = app.CircuitBreaker()
        msg = app.build_health_message("s1", cb)
        assert msg["last_error_message"] == ""


# ── send_to_topic ──────────────────────────────────────────────────────────────


class TestSendToTopic:
    def _make_client(self):
        """Return a mock ServiceBusClient with a working context-manager sender."""
        sender = MagicMock()
        sender.__enter__ = MagicMock(return_value=sender)
        sender.__exit__ = MagicMock(return_value=False)
        client = MagicMock()
        client.get_topic_sender.return_value = sender
        return client, sender

    def test_success_calls_send_messages(self):
        client, sender = self._make_client()
        cb = app.CircuitBreaker()
        app.send_to_topic(client, "my-topic", {"key": "val"}, cb)
        sender.send_messages.assert_called_once()

    def test_success_passes_correct_topic(self):
        client, _ = self._make_client()
        cb = app.CircuitBreaker()
        app.send_to_topic(client, "target-topic", {}, cb)
        client.get_topic_sender.assert_called_once_with(topic_name="target-topic")

    def test_success_records_cb_success(self):
        client, _ = self._make_client()
        cb = MagicMock(spec=app.CircuitBreaker)
        app.send_to_topic(client, "topic", {}, cb)
        cb.record_success.assert_called_once()

    def test_failure_records_cb_error(self):
        client = MagicMock()
        client.get_topic_sender.side_effect = RuntimeError("network error")
        cb = app.CircuitBreaker()
        with pytest.raises(RuntimeError):
            app.send_to_topic(client, "topic", {}, cb)
        assert cb.last_error_message == "network error"

    def test_failure_raises_exception(self):
        client = MagicMock()
        client.get_topic_sender.side_effect = RuntimeError("timeout")
        cb = app.CircuitBreaker()
        with pytest.raises(RuntimeError, match="timeout"):
            app.send_to_topic(client, "topic", {}, cb)

    def test_message_body_is_json(self):
        """The ServiceBusMessage should receive a JSON-serialised string body."""
        client, sender = self._make_client()
        cb = app.CircuitBreaker()
        payload = {"reading_type": "temperature", "value": 72.4}

        with patch("app.ServiceBusMessage") as mock_msg_cls:
            app.send_to_topic(client, "topic", payload, cb)
            args, kwargs = mock_msg_cls.call_args
            body = args[0]
            assert json.loads(body) == payload
            assert kwargs.get("content_type") == "application/json"


# ── sensor_loop ────────────────────────────────────────────────────────────────


class TestSensorLoop:
    _BASE_CFG = {
        "sensor_name": "test-sensor",
        "message_topic": "sensor-data",
        "message_interval": 0,
        "run_continuous": False,
    }

    def _stop_after(self, n: int) -> MagicMock:
        """stop_event.is_set() returns False for n calls, then True."""
        stop = MagicMock()
        stop.is_set.side_effect = [False] * n + [True]
        return stop

    def test_sends_all_payloads_once(self):
        payloads = [{"i": 0}, {"i": 1}, {"i": 2}]
        client = MagicMock()
        cb = app.CircuitBreaker()
        stop = self._stop_after(10)

        with patch("app.send_to_topic") as mock_send:
            app.sensor_loop(client, self._BASE_CFG, payloads, cb, stop)

        assert mock_send.call_count == 3

    def test_stops_when_not_continuous_after_exhaust(self):
        payloads = [{"i": 0}]
        client = MagicMock()
        cb = app.CircuitBreaker()
        stop = self._stop_after(10)

        with patch("app.send_to_topic") as mock_send:
            app.sensor_loop(client, self._BASE_CFG, payloads, cb, stop)

        # Should send exactly one message then exit (run_continuous=False)
        assert mock_send.call_count == 1

    def test_restarts_when_run_continuous(self):
        payloads = [{"i": 0}]
        cfg = {**self._BASE_CFG, "run_continuous": True}
        client = MagicMock()
        cb = app.CircuitBreaker()
        # Allow exactly 3 loop iterations before stopping
        stop = self._stop_after(3)

        with patch("app.send_to_topic") as mock_send:
            app.sensor_loop(client, cfg, payloads, cb, stop)

        # Each iteration should send the single payload (cycles 3 times)
        assert mock_send.call_count == 3

    def test_skips_send_when_circuit_open(self):
        payloads = [{"i": 0}]
        cfg = {**self._BASE_CFG, "run_continuous": True}
        client = MagicMock()
        cb = app.CircuitBreaker()
        # Trip the circuit breaker
        for i in range(6):
            cb.record_error(f"err {i}")

        stop = self._stop_after(3)

        with patch("app.send_to_topic") as mock_send:
            app.sensor_loop(client, cfg, payloads, cb, stop)

        mock_send.assert_not_called()

    def test_continues_after_send_failure(self):
        payloads = [{"i": 0}, {"i": 1}]
        client = MagicMock()
        cb = app.CircuitBreaker()
        stop = self._stop_after(10)

        with patch("app.send_to_topic", side_effect=RuntimeError("transient")) as mock_send:
            # Should not raise; errors are swallowed in sensor_loop
            app.sensor_loop(client, self._BASE_CFG, payloads, cb, stop)

        assert mock_send.call_count == 2

    def test_sends_payloads_in_order(self):
        payloads = [{"order": i} for i in range(3)]
        client = MagicMock()
        cb = app.CircuitBreaker()
        stop = self._stop_after(10)
        sent_contents = []

        def capture_send(c, topic, payload, circuit_breaker):
            sent_contents.append(payload["content"])

        with patch("app.send_to_topic", side_effect=capture_send):
            with patch("app.build_sensor_message", side_effect=lambda name, content: {"sensor_name": name, "content": content, "date_time": "", "correlation_id": ""}):
                app.sensor_loop(client, self._BASE_CFG, payloads, cb, stop)

        assert sent_contents == payloads


# ── health_loop ────────────────────────────────────────────────────────────────


class TestHealthLoop:
    _BASE_CFG = {
        "sensor_name": "test-sensor",
        "health_topic": "sensor-health",
        "health_interval": 0,
    }

    def _stop_after(self, n: int) -> MagicMock:
        stop = MagicMock()
        stop.is_set.side_effect = [False] * n + [True]
        return stop

    def test_sends_health_messages(self):
        client = MagicMock()
        cb = app.CircuitBreaker()
        stop = self._stop_after(3)

        with patch("app.send_to_topic") as mock_send:
            app.health_loop(client, self._BASE_CFG, cb, stop)

        assert mock_send.call_count == 3

    def test_continues_on_send_failure(self):
        client = MagicMock()
        cb = app.CircuitBreaker()
        stop = self._stop_after(3)

        with patch("app.send_to_topic", side_effect=RuntimeError("bus down")) as mock_send:
            # Should not raise
            app.health_loop(client, self._BASE_CFG, cb, stop)

        assert mock_send.call_count == 3

    def test_health_message_uses_correct_topic(self):
        client = MagicMock()
        cb = app.CircuitBreaker()
        stop = self._stop_after(1)

        with patch("app.send_to_topic") as mock_send:
            app.health_loop(client, self._BASE_CFG, cb, stop)

        _, topic_arg, _, _ = mock_send.call_args[0]
        assert topic_arg == "sensor-health"

    def test_health_message_contains_sensor_name(self):
        client = MagicMock()
        cb = app.CircuitBreaker()
        stop = self._stop_after(1)

        with patch("app.send_to_topic") as mock_send:
            app.health_loop(client, self._BASE_CFG, cb, stop)

        _, _, payload, _ = mock_send.call_args[0]
        assert payload["sensor_name"] == "test-sensor"

    def test_stops_when_event_set(self):
        client = MagicMock()
        cb = app.CircuitBreaker()
        stop = threading.Event()
        stop.set()  # Already set → loop should not execute

        with patch("app.send_to_topic") as mock_send:
            app.health_loop(client, self._BASE_CFG, cb, stop)

        mock_send.assert_not_called()
