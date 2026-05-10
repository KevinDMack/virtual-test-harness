"""
Synthetic Sensor Simulator for the tactical-edge-demo.

Reads JSON payloads from an inbox directory, publishes them as sensor messages
to a configurable message bus on a configurable interval, and periodically
publishes health messages to a separate topic.

Supported message bus types (set ``message_bus_type`` in config.json):
  servicebus – Azure Service Bus (default).  Requires ``service_bus_namespace``.
  mqtt       – MQTT broker via paho-mqtt.    Requires ``mqtt_broker_host`` and
               ``mqtt_broker_port``.

A circuit-breaker guards all publish operations:
  CLOSED    – normal operation; fewer than 5 errors in the last 10 minutes.
  HALF-OPEN – 1-5 errors in the last 10 minutes; still publishing but degraded.
  OPEN      – circuit is tripped (more than 5 errors in the last 10 minutes);
              publishing is suspended until the error window clears (i.e. all
              error timestamps become older than 10 minutes).

Health status mapping:
  green  – CLOSED with zero recent errors.
  yellow – HALF-OPEN (1-5 errors in the last 10 minutes).
  red    – OPEN circuit (more than 5 errors in the last 10 minutes); service is offline.
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import os
import threading
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import paho.mqtt.client as mqtt

from telemetry import TelemetryService, create_telemetry_service
from telemetry.console import ConsoleTelemetryService

# ── Paths ──────────────────────────────────────────────────────────────────────

BASE_DIR = Path(os.getenv("APP_BASE_DIR", "/app"))
CONFIG_PATH = Path(os.getenv("CONFIG_PATH", str(BASE_DIR / "config" / "config.json")))
INBOX_DIR = Path(os.getenv("INBOX_DIR", str(BASE_DIR / "inbox")))
LOG_DIR = Path(os.getenv("LOG_DIR", "/logs"))

# ── Logging ────────────────────────────────────────────────────────────────────

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
_LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

logging.basicConfig(
    level=logging.INFO,
    format=_LOG_FORMAT,
    datefmt=_LOG_DATE_FORMAT,
)

# File handler – write rotating logs to LOG_DIR/app.log so that Arc and
# monitoring services (e.g. Azure Monitor, Fluent Bit) can scrape them from
# the mounted /logs volume.
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    _file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB per file
        backupCount=5,
    )
    _file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATE_FORMAT))
    logging.getLogger().addHandler(_file_handler)
except OSError as _log_err:
    logging.getLogger().warning(
        "Could not set up file logging to %s: %s – logging to console only.", LOG_DIR, _log_err
    )

log = logging.getLogger(__name__)

# ── Circuit-breaker constants ──────────────────────────────────────────────────

_ERROR_WINDOW_SECONDS = 600  # 10 minutes
_YELLOW_THRESHOLD = 1        # ≥1 errors → yellow / HALF-OPEN
_RED_THRESHOLD = 5           # >5 errors → red / OPEN


# ── Circuit Breaker ────────────────────────────────────────────────────────────


class CircuitBreaker:
    """Three-state circuit breaker: CLOSED → HALF-OPEN → OPEN."""

    CLOSED = "CLOSED"
    HALF_OPEN = "HALF-OPEN"
    OPEN = "OPEN"

    def __init__(self, telemetry: TelemetryService | None = None) -> None:
        self._lock = threading.Lock()
        # Sliding window: timestamps (float) of recent errors.
        self._error_times: deque[float] = deque()
        self.last_error_message: str = ""
        self._telemetry: TelemetryService = telemetry or ConsoleTelemetryService()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _purge_old_errors(self) -> None:
        """Remove error timestamps outside the sliding window."""
        cutoff = time.monotonic() - _ERROR_WINDOW_SECONDS
        while self._error_times and self._error_times[0] < cutoff:
            self._error_times.popleft()

    def _recent_error_count(self) -> int:
        self._purge_old_errors()
        return len(self._error_times)

    # ── Public API ────────────────────────────────────────────────────────────

    def record_error(self, message: str) -> None:
        """Record a failure and update the last error message."""
        with self._lock:
            self._error_times.append(time.monotonic())
            self.last_error_message = message
            count = self._recent_error_count()
        self._telemetry.log(
            "warning",
            "Circuit breaker error recorded (%d in window): %s" % (count, message),
        )
        self._telemetry.track_metric("circuit_breaker.error_count", count)

    def record_success(self) -> None:
        """A successful operation – no state change, but logged for clarity."""
        pass  # Success does not drain the error window; time does.

    @property
    def state(self) -> str:
        with self._lock:
            count = self._recent_error_count()
        if count > _RED_THRESHOLD:
            return self.OPEN
        if count >= _YELLOW_THRESHOLD:
            return self.HALF_OPEN
        return self.CLOSED

    @property
    def is_open(self) -> bool:
        return self.state == self.OPEN

    @property
    def health_status(self) -> str:
        """Map circuit state to a human-readable colour code."""
        state = self.state
        if state == self.OPEN:
            return "red"
        if state == self.HALF_OPEN:
            return "yellow"
        return "green"


# ── Message publisher protocol ─────────────────────────────────────────────────


@runtime_checkable
class MessagePublisher(Protocol):
    """Common interface for all message-bus back-ends."""

    def publish(self, topic: str, body: str) -> None:
        """Send *body* (a JSON string) to *topic*."""
        ...

    def close(self) -> None:
        """Release any underlying connections / resources."""
        ...


# ── Azure Service Bus publisher ────────────────────────────────────────────────


class ServiceBusPublisher:
    """Publish JSON messages to Azure Service Bus topics."""

    def __init__(self, namespace: str, telemetry: TelemetryService | None = None) -> None:
        credential = DefaultAzureCredential()
        self._client = ServiceBusClient(
            fully_qualified_namespace=namespace,
            credential=credential,
            logging_enable=False,
        )
        self._telemetry: TelemetryService = telemetry or ConsoleTelemetryService()
        self._telemetry.log("info", "ServiceBusPublisher initialised for namespace: %s" % namespace)

    def publish(self, topic: str, body: str) -> None:
        with self._client.get_topic_sender(topic_name=topic) as sender:
            sender.send_messages(ServiceBusMessage(body, content_type="application/json"))
        self._telemetry.log("debug", "ServiceBus: published to topic '%s'" % topic)

    def close(self) -> None:
        self._client.close()


# ── MQTT publisher ─────────────────────────────────────────────────────────────


class MQTTPublisher:
    """Publish JSON messages to an MQTT broker using paho-mqtt."""

    def __init__(self, cfg: dict, telemetry: TelemetryService | None = None) -> None:
        client_id: str = cfg.get("mqtt_client_id") or cfg.get("sensor_name", "")
        self._qos: int = int(cfg.get("mqtt_qos", 1))
        self._telemetry: TelemetryService = telemetry or ConsoleTelemetryService()

        self._client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
        )

        username: str = cfg.get("mqtt_username", "")
        password: str = cfg.get("mqtt_password", "")
        if username:
            self._client.username_pw_set(username, password if password else None)

        if cfg.get("mqtt_use_tls", False):
            self._client.tls_set()

        host: str = cfg["mqtt_broker_host"]
        port: int = int(cfg["mqtt_broker_port"])
        self._client.connect(host, port)
        self._client.loop_start()
        self._telemetry.log("info", "MQTTPublisher connected to %s:%d" % (host, port))

    def publish(self, topic: str, body: str) -> None:
        result = self._client.publish(topic, body, qos=self._qos)
        result.wait_for_publish()
        self._telemetry.log("debug", "MQTT: published to topic '%s'" % topic)

    def close(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()


# ── Publisher factory ──────────────────────────────────────────────────────────


def create_publisher(cfg: dict, telemetry: TelemetryService | None = None) -> MessagePublisher:
    """Instantiate the correct :class:`MessagePublisher` from *cfg*."""
    bus_type: str = cfg.get("message_bus_type", "servicebus").lower()
    if bus_type == "servicebus":
        return ServiceBusPublisher(cfg["service_bus_namespace"], telemetry=telemetry)
    if bus_type == "mqtt":
        return MQTTPublisher(cfg, telemetry=telemetry)
    raise ValueError(f"Unknown message_bus_type: '{bus_type}'. Must be 'servicebus' or 'mqtt'.")


# ── Config loading ─────────────────────────────────────────────────────────────


def load_config(path: Path) -> dict[str, Any]:
    log.info("Loading config from %s", path)
    with path.open() as fh:
        cfg = json.load(fh)
    # Keys required regardless of bus type.
    always_required = [
        "sensor_name",
        "message_interval",
        "message_topic",
        "health_interval",
        "health_topic",
        "run_continuous",
        "message_bus_type",
    ]
    # Keys required only for a specific bus type.
    bus_specific_required: dict[str, list[str]] = {
        "servicebus": ["service_bus_namespace"],
        "mqtt": ["mqtt_broker_host", "mqtt_broker_port"],
    }

    missing = [k for k in always_required if k not in cfg]

    bus_type: str = cfg.get("message_bus_type", "").lower()
    extra_required = bus_specific_required.get(bus_type, [])
    missing += [k for k in extra_required if k not in cfg]

    if missing:
        raise ValueError(f"Config is missing required keys: {missing}")
    return cfg


# ── Inbox loading ──────────────────────────────────────────────────────────────


def load_inbox(directory: Path) -> list[dict]:
    """Load all JSON files from the inbox directory into a flat list."""
    payloads: list[dict] = []
    json_files = sorted(directory.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in inbox: {directory}")
    for file in json_files:
        log.info("Loading inbox file: %s", file)
        with file.open() as fh:
            data = json.load(fh)
        if isinstance(data, list):
            payloads.extend(data)
        else:
            payloads.append(data)
    log.info("Loaded %d message payloads from inbox", len(payloads))
    return payloads


# ── Message builders ───────────────────────────────────────────────────────────


def build_sensor_message(sensor_name: str, content: dict) -> dict:
    return {
        "sensor_name": sensor_name,
        "date_time": datetime.now(timezone.utc).isoformat(),
        "correlation_id": str(uuid.uuid4()),
        "content": content,
    }


def build_health_message(sensor_name: str, cb: CircuitBreaker) -> dict:
    return {
        "sensor_name": sensor_name,
        "date_time": datetime.now(timezone.utc).isoformat(),
        "status": cb.health_status,
        "last_error_message": cb.last_error_message,
    }


# ── Publisher helpers ──────────────────────────────────────────────────────────


def send_to_topic(
    publisher: MessagePublisher,
    topic: str,
    payload: dict,
    cb: CircuitBreaker,
    telemetry: TelemetryService | None = None,
) -> None:
    """Publish a single JSON message to a topic via the active publisher."""
    _telemetry: TelemetryService = telemetry or ConsoleTelemetryService()
    body = json.dumps(payload)
    try:
        publisher.publish(topic, body)
        cb.record_success()
        _telemetry.log("debug", "Published to topic '%s': %s" % (topic, body))
        _telemetry.track_event("MessagePublished", {"topic": topic})
    except Exception as exc:  # noqa: BLE001
        cb.record_error(str(exc))
        _telemetry.log("error", "Failed to publish to topic '%s': %s" % (topic, exc))
        _telemetry.track_exception(exc, {"topic": topic})
        raise


# ── Health publisher thread ────────────────────────────────────────────────────


def health_loop(
    publisher: MessagePublisher,
    cfg: dict,
    cb: CircuitBreaker,
    stop_event: threading.Event,
    telemetry: TelemetryService | None = None,
) -> None:
    _telemetry: TelemetryService = telemetry or ConsoleTelemetryService()
    sensor_name: str = cfg["sensor_name"]
    health_topic: str = cfg["health_topic"]
    interval: float = float(cfg["health_interval"])

    while not stop_event.is_set():
        msg = build_health_message(sensor_name, cb)
        _telemetry.log(
            "info",
            "Health [%s] status=%s errors=%s" % (
                sensor_name,
                msg["status"],
                repr(msg["last_error_message"]) if msg["last_error_message"] else "(none)",
            ),
        )
        _telemetry.track_event(
            "HealthPublished",
            {"sensor_name": sensor_name, "status": msg["status"]},
        )
        try:
            send_to_topic(publisher, health_topic, msg, cb, telemetry=_telemetry)
        except Exception:  # noqa: BLE001
            # Error already recorded by send_to_topic; continue publishing health.
            pass
        stop_event.wait(interval)


# ── Sensor publisher (main loop) ───────────────────────────────────────────────


def sensor_loop(
    publisher: MessagePublisher,
    cfg: dict,
    payloads: list[dict],
    cb: CircuitBreaker,
    stop_event: threading.Event,
    telemetry: TelemetryService | None = None,
) -> None:
    _telemetry: TelemetryService = telemetry or ConsoleTelemetryService()
    sensor_name: str = cfg["sensor_name"]
    message_topic: str = cfg["message_topic"]
    interval: float = float(cfg["message_interval"])
    run_continuous: bool = bool(cfg["run_continuous"])

    index = 0
    total = len(payloads)

    while not stop_event.is_set():
        if index >= total:
            if run_continuous:
                _telemetry.log("info", "Inbox exhausted – restarting from the beginning.")
                index = 0
            else:
                _telemetry.log("info", "Inbox exhausted and run_continuous=false – stopping sensor loop.")
                break

        if cb.is_open:
            _telemetry.log(
                "warning",
                "Circuit breaker is OPEN – skipping message send. Waiting %s s." % interval,
            )
            stop_event.wait(interval)
            continue

        content = payloads[index]
        index += 1

        msg = build_sensor_message(sensor_name, content)
        _telemetry.log(
            "info",
            "Sending sensor message %d/%d correlation_id=%s" % (index, total, msg["correlation_id"]),
        )
        _telemetry.track_event(
            "SensorMessageSent",
            {"sensor_name": sensor_name, "index": index, "correlation_id": msg["correlation_id"]},
        )
        try:
            send_to_topic(publisher, message_topic, msg, cb, telemetry=_telemetry)
        except Exception:  # noqa: BLE001
            # Error already recorded; back off slightly but continue.
            pass

        stop_event.wait(interval)


# ── Entry point ────────────────────────────────────────────────────────────────


def main() -> None:
    cfg = load_config(CONFIG_PATH)
    payloads = load_inbox(INBOX_DIR)

    telemetry = create_telemetry_service(cfg)

    bus_type: str = cfg.get("message_bus_type", "servicebus")
    telemetry.log(
        "info",
        "Starting sensor simulator: sensor=%s message_bus_type=%s" % (cfg["sensor_name"], bus_type),
    )

    publisher = create_publisher(cfg, telemetry=telemetry)

    cb = CircuitBreaker(telemetry=telemetry)
    stop_event = threading.Event()

    health_thread = threading.Thread(
        target=health_loop,
        args=(publisher, cfg, cb, stop_event),
        kwargs={"telemetry": telemetry},
        name="health-publisher",
        daemon=True,
    )
    health_thread.start()

    try:
        sensor_loop(publisher, cfg, payloads, cb, stop_event, telemetry=telemetry)
    except KeyboardInterrupt:
        telemetry.log("info", "Interrupted – shutting down.")
    finally:
        stop_event.set()
        health_thread.join(timeout=5)
        publisher.close()
        telemetry.flush()
        telemetry.log("info", "Shutdown complete.")


if __name__ == "__main__":
    main()
