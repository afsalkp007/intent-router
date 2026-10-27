"""Intent classification, sentiment analysis, and urgency scoring engine."""

import re
from typing import List, Tuple, Optional
from intent_router.models import (
    IntentCategory,
    UrgencyLevel,
    SentimentType,
    ClassificationResult,
)


class IntentClassifier:
    """Classifies user inquiries into discrete intent categories with sentiment and urgency telemetry."""

    INTENT_KEYWORDS = {
        IntentCategory.SECURITY_ALERT: [
            "breach", "unauthorized", "hacked", "compromised", "unknown ip",
            "suspicious login", "vulnerability", "leak", "security incident", "stolen",
            "security alert", "credential",
        ],
        IntentCategory.CHURN_RISK: [
            "cancel my subscription", "canceling", "cancel account", "switching to",
            "moving to", "waste of money", "useless", "close my account", "leaving your platform",
            "unsubscribe", "cancel it", "cancel", "leave",
        ],
        IntentCategory.BILLING: [
            "refund", "double charge", "charged", "invoice", "billing",
            "credit card", "receipt", "overbilled", "payment failed", "stripe fee",
            "overcharge", "charges", "payment",
        ],
        IntentCategory.BUG_REPORT: [
            "crash", "500", "502", "503", "504", "server error", "internal server error",
            "bad gateway", "broken", "bug", "fails to load", "stack trace", "infinite loop",
            "blank screen", "corrupted", "not working", "outage", "system down", "exception",
        ],
        IntentCategory.FEATURE_REQUEST: [
            "feature request", "would be great if", "can you add", "roadmap",
            "dark mode", "export to csv", "integration with", "support for", "wishlist",
            "new feature", "enhancement",
        ],
    }

    HOSTILE_TRIGGERS = ["fraud", "scam", "lawsuit", "report to amex", "attorney", "unacceptable", "furious"]
    FRUSTRATED_TRIGGERS = ["ridiculous", "waste of time", "broken again", "terrible", "disappointed", "annoying", "angry"]
    POSITIVE_TRIGGERS = ["love your product", "great work", "awesome", "thank you", "kudos", "appreciate"]

    def classify(self, text: str) -> ClassificationResult:
        """Classify incoming customer message into structured intent, sentiment, and urgency."""
        clean_text = text.lower().strip()

        # 1. Match Intent
        detected_keywords: List[str] = []
        intent_scores = {intent: 0 for intent in IntentCategory}

        for intent, keywords in self.INTENT_KEYWORDS.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", clean_text) or kw in clean_text:
                    intent_scores[intent] += 1
                    detected_keywords.append(kw)

        # Sort intents by score
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        primary_intent, top_score = sorted_intents[0]

        if top_score == 0:
            primary_intent = IntentCategory.GENERAL_SUPPORT
            confidence = 0.85
            reasoning = "Query matches standard general support / informational guidance."
            secondary_intent = None
        else:
            # Calculate confidence score
            confidence = min(0.98, round(0.70 + (top_score * 0.10), 2))
            secondary_intent = sorted_intents[1][0] if sorted_intents[1][1] > 0 else None
            reasoning = f"Matched keywords {detected_keywords} indicating {primary_intent.value} intent."

        # 2. Determine Sentiment
        if any(w in clean_text for w in self.HOSTILE_TRIGGERS):
            sentiment = SentimentType.HOSTILE
        elif any(w in clean_text for w in self.FRUSTRATED_TRIGGERS):
            sentiment = SentimentType.FRUSTRATED
        elif any(w in clean_text for w in self.POSITIVE_TRIGGERS):
            sentiment = SentimentType.POSITIVE
        else:
            sentiment = SentimentType.NEUTRAL

        # 3. Determine Urgency Level
        if primary_intent == IntentCategory.SECURITY_ALERT:
            urgency = UrgencyLevel.CRITICAL
        elif primary_intent == IntentCategory.CHURN_RISK or sentiment == SentimentType.HOSTILE:
            urgency = UrgencyLevel.CRITICAL if "all seats" in clean_text or "cancel" in clean_text else UrgencyLevel.HIGH
        elif primary_intent == IntentCategory.BUG_REPORT and any(w in clean_text for w in ["outage", "ceo", "demo", "production", "crash"]):
            urgency = UrgencyLevel.CRITICAL
        elif primary_intent in (IntentCategory.BILLING, IntentCategory.BUG_REPORT):
            urgency = UrgencyLevel.HIGH if sentiment in (SentimentType.FRUSTRATED, SentimentType.HOSTILE) else UrgencyLevel.MEDIUM
        elif primary_intent == IntentCategory.FEATURE_REQUEST:
            urgency = UrgencyLevel.LOW
        else:
            urgency = UrgencyLevel.MEDIUM if sentiment == SentimentType.FRUSTRATED else UrgencyLevel.LOW

        return ClassificationResult(
            primary_intent=primary_intent,
            confidence=confidence,
            secondary_intent=secondary_intent,
            urgency=urgency,
            sentiment=sentiment,
            detected_keywords=detected_keywords,
            reasoning=reasoning,
        )
