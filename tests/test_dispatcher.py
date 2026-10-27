"""Unit tests for specialized expert prompt handler specifications."""

import pytest
from intent_router.dispatcher import IntentDispatcher, HANDLERS
from intent_router.models import IntentCategory


def test_dispatcher_retrieves_all_intents():
    for intent in IntentCategory:
        handler = IntentDispatcher.get_handler(intent)
        assert handler is not None
        assert handler.handler_name is not None
        assert handler.sla_target is not None
        assert len(handler.system_prompt) > 20
        assert len(handler.suggested_tags) >= 1


def test_security_handler_sla_immediate():
    sec_handler = IntentDispatcher.get_handler(IntentCategory.SECURITY_ALERT)
    assert "IMMEDIATE" in sec_handler.sla_target
    assert "SecOps" in sec_handler.handler_name
