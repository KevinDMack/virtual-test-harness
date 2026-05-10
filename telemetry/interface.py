"""
TelemetryService protocol – the single interface all telemetry implementations must satisfy.

Any class that provides all five methods below is a valid :class:`TelemetryService`.
The protocol is ``runtime_checkable`` so ``isinstance`` can be used where helpful.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class TelemetryService(Protocol):
    """Common interface for all telemetry back-ends."""

    def log(self, level: str, message: str, **kwargs: Any) -> None:
        """
        Emit a structured log entry.

        :param level: Severity string – one of ``"debug"``, ``"info"``,
                      ``"warning"``, ``"error"``, ``"critical"``.
        :param message: Human-readable log message.
        :param kwargs: Additional structured key/value pairs to attach to the entry.
        """
        ...

    def track_event(self, name: str, properties: dict[str, Any] | None = None) -> None:
        """
        Record a named custom event with optional property bag.

        :param name: Event name (e.g. ``"MessagePublished"``).
        :param properties: Arbitrary key/value metadata to include.
        """
        ...

    def track_exception(
        self, exc: BaseException, properties: dict[str, Any] | None = None
    ) -> None:
        """
        Capture an exception with optional context.

        :param exc: The exception instance to record.
        :param properties: Arbitrary key/value metadata to include.
        """
        ...

    def track_metric(
        self,
        name: str,
        value: float,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """
        Record a numeric measurement.

        :param name: Metric name (e.g. ``"PublishLatencyMs"``).
        :param value: Numeric value of the measurement.
        :param properties: Arbitrary key/value dimensions to include.
        """
        ...

    def flush(self) -> None:
        """Force-export any buffered telemetry. Call on application shutdown."""
        ...
