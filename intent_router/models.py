"""Pydantic schemas for intent categories, urgency scores, and routing reports."""

from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class IntentCategory(str, Enum):
    BILLING = "BILLING"
    BUG_REPORT = "BUG_REPORT"
    FEATURE_REQUEST = "FEATURE_REQUEST"
    CHURN_RISK = "CHURN_RISK"
    SECURITY_ALERT = "SECURITY_ALERT"
    GENERAL_SUPPORT = "GENERAL_SUPPORT"


class UrgencyLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SentimentType(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    FRUSTRATED = "FRUSTRATED"
    HOSTILE = "HOSTILE"


class ClassificationResult(BaseModel):
    """Zero-shot classification verdict with sentiment and urgency telemetry."""
    primary_intent: IntentCategory
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    secondary_intent: Optional[IntentCategory] = None
    urgency: UrgencyLevel
    sentiment: SentimentType
    detected_keywords: List[str] = Field(default_factory=list)
    reasoning: str = Field(..., description="Explanation for classification verdict")


class RoutedResponse(BaseModel):
    """The generated output from the specialized prompt handler."""
    ticket_id: str
    intent: IntentCategory
    handler_name: str
    response_text: str
    escalation_required: bool = False
    sla_target: str = Field(default="< 4 hours", description="Target SLA resolution window")
    routed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    latency_ms: float = 0.0


class TriageReport(BaseModel):
    """Consolidated end-to-end ticket triage report."""
    ticket_id: str
    customer_message: str
    classification: ClassificationResult
    routed_response: RoutedResponse
    suggested_tags: List[str] = Field(default_factory=list)
