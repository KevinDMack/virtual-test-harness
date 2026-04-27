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
