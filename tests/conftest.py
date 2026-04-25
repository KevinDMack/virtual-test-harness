"""Pytest configuration – mock Azure SDK modules before app.py is imported."""

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
