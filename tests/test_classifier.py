"""Unit tests for intent classification, sentiment analysis, and urgency scoring."""

import pytest
from intent_router.classifier import IntentClassifier
from intent_router.models import IntentCategory, UrgencyLevel, SentimentType


@pytest.fixture
def classifier():
    return IntentClassifier()


def test_classify_billing_refund(classifier):
    text = "I was double charged $99 on my credit card! I need an immediate refund for this invoice."
    res = classifier.classify(text)

    assert res.primary_intent == IntentCategory.BILLING
    assert res.urgency in (UrgencyLevel.HIGH, UrgencyLevel.MEDIUM)
    assert len(res.detected_keywords) >= 1


def test_classify_critical_bug_outage(classifier):
    text = "Our production server crashed and is throwing 500 internal server errors during checkout!"
    res = classifier.classify(text)

    assert res.primary_intent == IntentCategory.BUG_REPORT
    assert res.urgency == UrgencyLevel.CRITICAL


def test_classify_security_incident(classifier):
    text = "We discovered an unauthorized login from an unknown IP address. Potential account breach."
    res = classifier.classify(text)

    assert res.primary_intent == IntentCategory.SECURITY_ALERT
    assert res.urgency == UrgencyLevel.CRITICAL


def test_classify_churn_risk(classifier):
    text = "Your platform is a waste of money. Cancel my subscription immediately, we are leaving."
    res = classifier.classify(text)

    assert res.primary_intent == IntentCategory.CHURN_RISK
    assert res.sentiment == SentimentType.FRUSTRATED


def test_classify_feature_request(classifier):
    text = "We love your product! Would be great if you could add a new feature for dark mode and export to csv."
    res = classifier.classify(text)

    assert res.primary_intent == IntentCategory.FEATURE_REQUEST
    assert res.urgency == UrgencyLevel.LOW
    assert res.sentiment == SentimentType.POSITIVE


def test_classify_general_support(classifier):
    text = "Where can I find the getting started tutorials and onboarding instructions?"
    res = classifier.classify(text)

    assert res.primary_intent == IntentCategory.GENERAL_SUPPORT
    assert res.urgency == UrgencyLevel.LOW
