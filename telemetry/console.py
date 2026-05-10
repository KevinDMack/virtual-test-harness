"""
ConsoleTelemetryService – wraps the standard Python :mod:`logging` module.

This implementation is the default/fallback backend.  It requires no extra
dependencies and preserves the pre-existing logging behaviour of the application.
"""

from __future__ import annotations

import logging
import traceback
from typing import Any

log = logging.getLogger(__name__)

# Map our level strings to Python logging levels.
_LEVEL_MAP: dict[str, int] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


class ConsoleTelemetryService:
    """Telemetry backend that writes to the standard Python logging system."""

    def log(self, level: str, message: str, **kwargs: Any) -> None:
        """Emit a log entry at *level* with optional structured extras."""
        numeric_level = _LEVEL_MAP.get(level.lower(), logging.INFO)
        extra_str = "  ".join(f"{k}={v!r}" for k, v in kwargs.items())
        full_message = f"{message}  {extra_str}".rstrip() if extra_str else message
        log.log(numeric_level, full_message)

    def track_event(self, name: str, properties: dict[str, Any] | None = None) -> None:
        """Log a custom event as an INFO entry."""
        props = properties or {}
        prop_str = "  ".join(f"{k}={v!r}" for k, v in props.items())
        log.info("EVENT %s  %s", name, prop_str)

    def track_exception(
        self, exc: BaseException, properties: dict[str, Any] | None = None
    ) -> None:
        """Log an exception as an ERROR entry, including the traceback."""
        props = properties or {}
        prop_str = "  ".join(f"{k}={v!r}" for k, v in props.items())
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        log.error("EXCEPTION %s: %s  %s\n%s", type(exc).__name__, exc, prop_str, tb)

    def track_metric(
        self,
        name: str,
        value: float,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """Log a metric measurement as a DEBUG entry."""
        props = properties or {}
        prop_str = "  ".join(f"{k}={v!r}" for k, v in props.items())
        log.debug("METRIC %s=%s  %s", name, value, prop_str)

    def flush(self) -> None:
        """Flush all logging handlers attached to the root logger."""
        for handler in logging.getLogger().handlers:
            handler.flush()
