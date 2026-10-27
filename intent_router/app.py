"""Interactive Streamlit Intent Triage & Routing Dashboard for IntentRouter."""

import os
import json
import warnings
from typing import Dict

warnings.filterwarnings("ignore")

import streamlit as st

from intent_router.router import TriageRouter
from intent_router.providers import get_llm_provider
from intent_router.models import IntentCategory, UrgencyLevel, SentimentType

# Streamlit Page Config
st.set_page_config(
    page_title="IntentRouter | Multi-Prompt Triage & Intent Classifier",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .badge-critical {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 700;
    }
    .badge-high {
        background-color: #FFEDD5;
        color: #9A3412;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 700;
    }
    .badge-medium {
        background-color: #FEF9C3;
        color: #854D0E;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 700;
    }
    .badge-low {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">🚦 IntentRouter: Multi-Prompt Triage & Intent Classifier</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Zero-shot intent classification, sentiment & urgency scoring, and specialized expert prompt dispatching.</div>',
    unsafe_allow_html=True,
)

# Sidebar Configuration
st.sidebar.header("⚙️ Router Settings")

provider_choice = st.sidebar.selectbox(
    "LLM Provider",
    options=["gemini", "mock"],
    index=0 if os.getenv("GEMINI_API_KEY") and not os.getenv("GEMINI_API_KEY").startswith("your_") else 1,
    help="Select 'gemini' for live Gemini API calls or 'mock' for zero-cost simulated inference.",
)

st.sidebar.divider()
st.sidebar.subheader("📋 Sample Ticket Scenarios")

PRESETS: Dict[str, str] = {
    "💳 Billing: Overcharge & Refund Demand": (
        "I was double charged $199 on my corporate credit card this morning for an invoice I already paid! "
        "Fix this refund immediately or I am reporting fraud to our bank."
    ),
    "🚨 Technical Bug: Production Outage During Demo": (
        "CRITICAL: Your entire checkout API is throwing 500 internal server errors while our CEO is on stage "
        "pitching a live demo to investors! System is completely broken, what is happening?"
    ),
    "✨ Feature Request: Dark Mode & CSV Export": (
        "We absolutely love your analytics platform! Would be great if you could add support for Dark Mode "
        "and automated scheduled CSV exports for our weekly leadership sync."
    ),
    "💔 Churn Risk: Threatening Cancellation & Competitor": (
        "Cancel my subscription right now. Your platform has been a total waste of money and our team is "
        "canceling our 40 seats and switching to your competitor by Friday."
    ),
    "🛡️ Security Alert: Unauthorized Unknown IP Access": (
        "URGENT: Our audit log detected an unauthorized login to our admin dashboard from an unknown IP address "
        "in another country. Potential breach or compromised credential."
    ),
    "❓ General Support: Adding Team Members": (
        "Hello, could you point me to the documentation on how to add new team members and assign role-based permissions?"
    ),
}

selected_preset = st.sidebar.selectbox("Load Preset Inquiry", list(PRESETS.keys()))
default_text = PRESETS[selected_preset]

# Main Input
st.subheader("📩 Incoming Customer Ticket / Inquiry")
customer_query = st.text_area(
    "Customer Message:",
    value=default_text,
    height=110,
    help="Type any inquiry, bug report, feature request, or cancellation demand.",
)

if st.button("🚦 Classify, Triage & Route Ticket", type="primary", use_container_width=True):
    llm = get_llm_provider(provider_name=provider_choice)
    router = TriageRouter(llm=llm)

    with st.spinner("Analyzing intent, detecting sentiment, scoring urgency, and dispatching to expert prompt..."):
        report = router.triage(customer_query)
        st.session_state["report"] = report

if "report" in st.session_state:
    report = st.session_state["report"]
    cls = report.classification
    resp = report.routed_response

    st.markdown("---")
    st.subheader(f"📊 Triage Verdict: Ticket #{report.ticket_id}")

    # Top KPI Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Primary Intent", cls.primary_intent.value)
    with m2:
        st.metric("Confidence", f"{cls.confidence * 100:.0f}%")
    with m3:
        st.metric("Urgency Level", cls.urgency.value)
    with m4:
        st.metric("Sentiment", cls.sentiment.value)
    with m5:
        st.metric("Target SLA", resp.sla_target)

    # Escalation Alert Banner
    if resp.escalation_required:
        st.error(
            f"⚠️ **HIGH-PRIORITY ESCALATION REQUIRED** | Assigned Desk: **{resp.handler_name}** | "
            f"Target SLA: **{resp.sla_target}**"
        )
    else:
        st.success(f"✅ **AUTOMATED ROUTING** | Assigned Desk: **{resp.handler_name}** | Target SLA: **{resp.sla_target}**")

    # Routing Tabs
    tab_resp, tab_details, tab_json = st.tabs([
        "💬 Specialized Expert Response",
        "🧭 Classification & Keyword Telemetry",
        "📜 CRM Triage JSON Payload",
    ])

    with tab_resp:
        st.markdown(f"#### Generated by: `{resp.handler_name}`")
        st.info(resp.response_text)
        st.caption(f"⚡ Processing Latency: {resp.latency_ms} ms | Timestamp: {resp.routed_at}")

        if report.suggested_tags:
            st.markdown("**Suggested Ticket Tags:**")
            tag_badges = " ".join([f"`#{tag}`" for tag in report.suggested_tags])
            st.markdown(tag_badges)

    with tab_details:
        st.markdown("#### Classifier Telemetry & Decision Path")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.write(f"- **Primary Category:** `{cls.primary_intent.value}`")
            st.write(f"- **Secondary Category:** `{cls.secondary_intent.value if cls.secondary_intent else 'None'}`")
            st.write(f"- **Customer Sentiment:** `{cls.sentiment.value}`")
            st.write(f"- **Assessed Urgency:** `{cls.urgency.value}`")
        with col_c2:
            st.write(f"- **Assigned Handler:** `{resp.handler_name}`")
            st.write(f"- **Detected Keywords:** `{', '.join(cls.detected_keywords) if cls.detected_keywords else 'None'}`")
            st.write(f"- **Decision Rationale:** *{cls.reasoning}*")

    with tab_json:
        st.markdown("#### CRM / Helpdesk API Payload (Zendesk / Linear / Jira)")
        triage_json = report.model_dump_json(indent=2)
        st.code(triage_json, language="json")
        st.download_button(
            label="💾 Download Triage Ticket JSON",
            data=triage_json.encode("utf-8"),
            file_name=f"ticket_{report.ticket_id}.json",
            mime="application/json",
            use_container_width=True,
        )
