"""End-to-end multi-prompt triage router pipeline."""

import time
import random
from typing import Optional
from intent_router.models import (
    ClassificationResult,
    RoutedResponse,
    TriageReport,
    UrgencyLevel,
    SentimentType,
)
from intent_router.classifier import IntentClassifier
from intent_router.dispatcher import IntentDispatcher
from intent_router.providers import BaseLLM, get_llm_provider


class TriageRouter:
    """Classifies incoming customer requests and routes them to specialized prompt handlers."""

    def __init__(
        self,
        classifier: Optional[IntentClassifier] = None,
        llm: Optional[BaseLLM] = None,
    ):
        self.classifier = classifier or IntentClassifier()
        self.llm = llm or get_llm_provider()

    def _generate_ticket_id(self) -> str:
        return f"TICK-{random.randint(1000, 9999)}"

    def triage(self, customer_message: str) -> TriageReport:
        """Execute full classification, dispatch routing, and response generation."""
        start_time = time.time()
        ticket_id = self._generate_ticket_id()

        # 1. Classify Intent, Sentiment, and Urgency
        classification = self.classifier.classify(customer_message)

        # 2. Retrieve Specialized Expert Prompt Spec
        handler_spec = IntentDispatcher.get_handler(classification.primary_intent)

        # 3. Determine Human Escalation Flag
        escalation_required = (
            classification.urgency in (UrgencyLevel.CRITICAL, UrgencyLevel.HIGH)
            or classification.sentiment in (SentimentType.HOSTILE, SentimentType.FRUSTRATED)
        )

        # 4. Generate Expert Response
        response_text = self.llm.generate(
            system_prompt=handler_spec.system_prompt,
            user_message=customer_message,
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 1)

        routed_response = RoutedResponse(
            ticket_id=ticket_id,
            intent=classification.primary_intent,
            handler_name=handler_spec.handler_name,
            response_text=response_text,
            escalation_required=escalation_required,
            sla_target=handler_spec.sla_target,
            latency_ms=elapsed_ms,
        )

        return TriageReport(
            ticket_id=ticket_id,
            customer_message=customer_message,
            classification=classification,
            routed_response=routed_response,
            suggested_tags=handler_spec.suggested_tags,
        )
