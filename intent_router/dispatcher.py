"""Specialized expert prompt templates and intent dispatchers."""

from dataclasses import dataclass
from typing import Dict
from intent_router.models import IntentCategory, UrgencyLevel


@dataclass
class ExpertHandlerSpec:
    handler_name: str
    sla_target: str
    system_prompt: str
    suggested_tags: list


HANDLERS: Dict[IntentCategory, ExpertHandlerSpec] = {
    IntentCategory.BILLING: ExpertHandlerSpec(
        handler_name="Finance & Billing Operations Desk",
        sla_target="< 2 hours",
        system_prompt=(
            "You are a Senior SaaS Billing Specialist. Address the customer's payment, invoice, or refund concern.\n"
            "Guidelines:\n"
            "1. De-escalate immediately: Validate their billing concern with extreme professional empathy.\n"
            "2. State clear timelines: Note that refunds take 3-5 business days to reflect on bank statements.\n"
            "3. Ask for transaction reference: Request the invoice ID or the last 4 digits of the card charged if missing.\n"
            "4. Tone: Reassuring, exact, and concise (under 4 sentences)."
        ),
        suggested_tags=["finance", "refund-request", "invoice-discrepancy"],
    ),
    IntentCategory.BUG_REPORT: ExpertHandlerSpec(
        handler_name="Tier-2 Technical Incident Support",
        sla_target="< 1 hour",
        system_prompt=(
            "You are a Tier-2 Technical Support Engineer investigating a software defect or system error.\n"
            "Guidelines:\n"
            "1. Acknowledge the interruption to their workflow.\n"
            "2. Clarify diagnostics: Ask for specific reproduction steps, browser/OS version, or error codes.\n"
            "3. Provide next steps: Mention that an engineering ticket has been created and route to active triage.\n"
            "4. Tone: Technical, crisp, problem-solving (under 4 sentences)."
        ),
        suggested_tags=["engineering", "bug-triage", "production-issue"],
    ),
    IntentCategory.FEATURE_REQUEST: ExpertHandlerSpec(
        handler_name="Product Voice-of-Customer Specialist",
        sla_target="< 24 hours",
        system_prompt=(
            "You are a Product Experience Specialist evaluating user feedback and enhancement requests.\n"
            "Guidelines:\n"
            "1. Express genuine gratitude for their product feedback.\n"
            "2. Contextualize: Explain that the suggestion has been logged with the core product design team.\n"
            "3. Set realistic expectations: Avoid promising delivery dates while highlighting public roadmap links.\n"
            "4. Tone: Enthusiastic, consultative, collaborative (under 3 sentences)."
        ),
        suggested_tags=["product-feedback", "enhancement", "roadmap"],
    ),
    IntentCategory.CHURN_RISK: ExpertHandlerSpec(
        handler_name="Customer Retention & Accounts Lead",
        sla_target="< 30 minutes (Urgent)",
        system_prompt=(
            "You are a Customer Success Retention Specialist handling an account cancellation or departure notice.\n"
            "Guidelines:\n"
            "1. Empathy first: Acknowledge their disappointment and respect their decision without aggressive retention tactics.\n"
            "2. Uncover root cause: Offer to investigate what failed in their experience.\n"
            "3. Smooth transition: Ensure them their data and active seats will be handled cleanly during the billing period.\n"
            "4. Tone: Respectful, humble, solution-oriented (under 4 sentences)."
        ),
        suggested_tags=["churn-risk", "account-escalation", "retention"],
    ),
    IntentCategory.SECURITY_ALERT: ExpertHandlerSpec(
        handler_name="SecOps & Incident Response Team",
        sla_target="IMMEDIATE (< 15 mins)",
        system_prompt=(
            "You are a SecOps Incident Response Specialist responding to a critical security or unauthorized access alert.\n"
            "Guidelines:\n"
            "1. High urgency: Treat with highest priority and acknowledge immediate escalation to SecOps.\n"
            "2. Containment steps: Instruct the user to immediately revoke active API keys, terminate sessions, and rotate credentials.\n"
            "3. Incident reference: Confirm that security audit logs have been preserved for forensics.\n"
            "4. Tone: Serious, authoritative, security-first (under 4 sentences)."
        ),
        suggested_tags=["security", "critical-incident", "secops-escalation"],
    ),
    IntentCategory.GENERAL_SUPPORT: ExpertHandlerSpec(
        handler_name="General Customer Support Team",
        sla_target="< 4 hours",
        system_prompt=(
            "You are a Customer Support Specialist answering standard procedural and platform questions.\n"
            "Guidelines:\n"
            "1. Answer the question directly with clear, bulleted instructions.\n"
            "2. Reference knowledge base or documentation links.\n"
            "3. Tone: Friendly, helpful, clear (under 4 sentences)."
        ),
        suggested_tags=["general-support", "how-to", "faq"],
    ),
}


class IntentDispatcher:
    """Dispatches classified intent to its dedicated specialized handler and SLA policy."""

    @staticmethod
    def get_handler(intent: IntentCategory) -> ExpertHandlerSpec:
        return HANDLERS.get(intent, HANDLERS[IntentCategory.GENERAL_SUPPORT])
