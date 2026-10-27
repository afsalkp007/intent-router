"""Unit tests for the end-to-end TriageRouter pipeline."""

import pytest
from intent_router.router import TriageRouter
from intent_router.providers import MockProvider
from intent_router.models import IntentCategory, UrgencyLevel


@pytest.fixture
def router():
    return TriageRouter(llm=MockProvider())


def test_router_billing_flow(router):
    report = router.triage("I was double charged $199 on my credit card and need a refund!")

    assert report.ticket_id.startswith("TICK-")
    assert report.classification.primary_intent == IntentCategory.BILLING
    assert "Billing" in report.routed_response.handler_name
    assert report.routed_response.response_text is not None
    assert report.routed_response.latency_ms > 0


def test_router_escalates_critical_incident(router):
    report = router.triage("Security breach! Unauthorized login from unknown IP address detected.")

    assert report.classification.primary_intent == IntentCategory.SECURITY_ALERT
    assert report.classification.urgency == UrgencyLevel.CRITICAL
    assert report.routed_response.escalation_required is True
    assert "SecOps" in report.routed_response.handler_name


def test_router_low_urgency_feature(router):
    report = router.triage("Could you add a feature request for Dark Mode and export to CSV?")

    assert report.classification.primary_intent == IntentCategory.FEATURE_REQUEST
    assert report.classification.urgency == UrgencyLevel.LOW
    assert report.routed_response.escalation_required is False
    assert "Product" in report.routed_response.handler_name
