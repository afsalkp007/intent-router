"""Unit tests for IntentRouter Pydantic schemas."""

import pytest
from intent_router.models import (
    IntentCategory,
    UrgencyLevel,
    SentimentType,
    ClassificationResult,
    RoutedResponse,
    TriageReport,
)


def test_classification_result_validation():
    res = ClassificationResult(
        primary_intent=IntentCategory.BILLING,
        confidence=0.92,
        urgency=UrgencyLevel.HIGH,
        sentiment=SentimentType.FRUSTRATED,
        detected_keywords=["refund", "invoice"],
        reasoning="Matched billing keywords.",
    )
    assert res.primary_intent == IntentCategory.BILLING
    assert res.confidence == 0.92
    assert res.urgency == UrgencyLevel.HIGH


def test_triage_report_structure():
    cls = ClassificationResult(
        primary_intent=IntentCategory.FEATURE_REQUEST,
        confidence=0.88,
        urgency=UrgencyLevel.LOW,
        sentiment=SentimentType.POSITIVE,
        reasoning="Feature suggestion.",
    )
    routed = RoutedResponse(
        ticket_id="TICK-101",
        intent=IntentCategory.FEATURE_REQUEST,
        handler_name="Product Voice-of-Customer",
        response_text="Thank you for your feedback!",
        sla_target="< 24 hours",
    )
    report = TriageReport(
        ticket_id="TICK-101",
        customer_message="Please add dark mode.",
        classification=cls,
        routed_response=routed,
        suggested_tags=["feature", "dark-mode"],
    )
    assert report.ticket_id == "TICK-101"
    assert report.routed_response.escalation_required is False
