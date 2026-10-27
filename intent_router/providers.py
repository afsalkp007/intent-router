"""LLM Providers for specialized prompt execution with zero-crash mock fallback."""

import os
import time
import logging
import warnings
from abc import ABC, abstractmethod
from typing import Optional

warnings.filterwarnings("ignore")

import requests
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
load_dotenv()
logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """Abstract interface for executing prompts on an LLM."""

    @abstractmethod
    def generate(self, system_prompt: str, user_message: str) -> str:
        pass


class GeminiProvider(BaseLLM):
    """Google Gemini 2.5 Flash execution provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

    def generate(self, system_prompt: str, user_message: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"System Instructions:\n{system_prompt}\n\nCustomer Inquiry:\n{user_message}"}
                    ]
                }
            ],
            "generationConfig": {"temperature": 0.2},
        }

        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini API request failed ({resp.status_code}): {resp.text}")

        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()


class MockProvider(BaseLLM):
    """Context-aware mock provider simulating tailored expert responses."""

    def generate(self, system_prompt: str, user_message: str) -> str:
        time.sleep(0.05)  # Simulate fast local processing
        s_lower = system_prompt.lower()

        if "billing specialist" in s_lower or "finance" in s_lower:
            return (
                "I sincerely apologize for the unexpected charge on your account. I have located your billing profile "
                "and initiated an immediate refund, which will reflect in 3-5 business days. Please reply with your invoice "
                "number or the last 4 digits of the card if you need confirmation sent to an alternate email."
            )
        elif "tier-2 technical" in s_lower or "defect" in s_lower:
            return (
                "Thank you for reporting this error; I understand how disruptive this issue is to your current workflow. "
                "I have created an escalated incident ticket with our engineering team. Could you share your browser version "
                "and the exact URL where the error occurred so we can isolate the root cause?"
            )
        elif "product experience" in s_lower or "feedback" in s_lower:
            return (
                "Thank you so much for this thoughtful enhancement suggestion! I have officially logged this feedback with our "
                "core product design team for our upcoming quarterly roadmap review. We continuously prioritize features directly "
                "from customer requests like yours."
            )
        elif "retention" in s_lower or "cancellation" in s_lower:
            return (
                "I am truly sorry to hear that your experience did not meet expectations, and I completely respect your decision. "
                "Your subscription cancellation has been scheduled so no further charges occur. If you have a moment, I would "
                "deeply appreciate knowing what key capability or support was missing during your time with us."
            )
        elif "secops" in s_lower or "incident response" in s_lower:
            return (
                "EMERGENCY ACTION: We have escalated this incident directly to our SecOps on-call team. "
                "Please immediately revoke active API tokens, terminate all browser sessions from your account security panel, "
                "and reset your credentials. Our security lead will reach out via your primary email within 15 minutes."
            )
        else:
            return (
                "Thank you for contacting customer support. To accomplish this, navigate to your account dashboard settings "
                "and consult our official setup guide at docs.example.com. Please feel free to reply if you need further clarification."
            )


def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLM:
    """Factory function for LLM provider."""
    active = (provider_name or os.getenv("LLM_PROVIDER", "gemini")).lower()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    if active == "gemini" and gemini_key and not gemini_key.startswith("your_"):
        try:
            return GeminiProvider(api_key=gemini_key)
        except Exception as e:
            logger.warning("Failed to initialize GeminiProvider: %s. Using MockProvider.", e)
            return MockProvider()

    return MockProvider()
