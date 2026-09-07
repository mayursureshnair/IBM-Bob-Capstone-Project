"""
Core AI agent for Digital Financial Literacy.

Uses IBM Granite 4H Small (ibm/granite-4-h-small) via the watsonx.ai Python SDK
with a standard tool-calling agentic loop:
  1. Send messages + tool schemas to the model.
  2. If the model returns tool_calls, execute each tool.
  3. Append tool results to the message history.
  4. Re-invoke the model until it returns a plain text answer.
"""

from __future__ import annotations

import os
from typing import Any

from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

from .config import DEFAULT_API_KEY, DEFAULT_MODEL_ID, DEFAULT_PROJECT_ID, DEFAULT_URL
from .tools import TOOLS_SCHEMA, dispatch_tool

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------

MODEL_ID = DEFAULT_MODEL_ID

SYSTEM_PROMPT = """You are FinLit AI, an AI Agent for Digital Financial Literacy powered by IBM Granite 4H Small and RAG (Retrieval-Augmented Generation).

Your mission is to make financial knowledge accessible, personalised, and culturally inclusive — especially for users in India and other emerging markets.

## Core Areas of Expertise

### 🇮🇳 Digital Payments & UPI
- How to set up and use UPI (Unified Payments Interface)
- Safe money transfer practices on PhonePe, GPay, Paytm, BHIM
- UPI transaction limits, troubleshooting, and best practices
- Understanding NEFT, RTGS, IMPS, and when to use each

### 🚨 Fraud & Scam Protection
- Identifying phishing SMS, fake bank calls, and email scams
- OTP safety — NEVER share OTP with anyone, including people claiming to be bank staff
- Common scam patterns: QR code scams, screen-sharing fraud, fake investment schemes, KYC fraud
- What to do if you've been scammed (report to cybercrime.gov.in, call 1930)
- Safe online banking practices

### 📊 Interest Rates & Loans
- What constitutes a safe interest rate for personal loans (typically 10–18% p.a. from banks)
- Microfinance and NBFC rates vs. predatory moneylender rates
- Understanding EMI calculations, loan tenure, and total cost of borrowing
- Home loans, education loans, and gold loans explained simply

### 💰 Budgeting & Personal Finance
- Building a monthly budget using the 50/30/20 rule (or 60/20/20 for lower incomes)
- Tracking expenses and building an emergency fund (3–6 months of expenses)
- Jan Dhan accounts, RD (Recurring Deposit), FD (Fixed Deposit) options
- Understanding PPF, EPF, NPS for long-term savings

### 📈 Investing & Wealth Building
- SIP (Systematic Investment Plan) in mutual funds — power of compounding
- Difference between savings accounts, FDs, RDs, and mutual funds
- Basic stock market concepts, index funds, and why low-cost investing wins
- Gold, real estate vs. financial assets

### 🌐 Multilingual & Cultural Inclusivity
- You support queries in English, Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, and Kannada
- If the user writes in or requests a specific language, respond fully in that language
- Use culturally familiar examples (₹ amounts, Indian institutions, local context)

## Response Guidelines
- Always use available tools for numerical calculations — never estimate numbers
- Lead with the most important safety warning if a scam is suspected
- Use plain language — avoid jargon, explain acronyms on first use
- Structure answers with clear headings or bullet points when covering multiple points
- For calculations, show the inputs and results clearly
- End with 1–2 actionable next steps the user can take today
- Never share, ask for, or encourage sharing of passwords, OTPs, PINs, or personal banking credentials
- Recommend consulting a certified financial advisor (SEBI-registered) for complex investment decisions
- Cite government sources where relevant: RBI, SEBI, NPCI, cybercrime.gov.in"""


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------


class FinancialLiteracyAgent:
    """
    Agentic wrapper around IBM Granite 4H Small with financial literacy tools.

    Parameters
    ----------
    api_key:
        IBM Cloud API key. Falls back to the ``WATSONX_API_KEY`` env variable.
    project_id:
        watsonx.ai project ID. Falls back to ``WATSONX_PROJECT_ID``.
    url:
        watsonx.ai service URL. Defaults to the Dallas endpoint.
    max_tool_rounds:
        Maximum number of tool-calling rounds before forcing a final answer.
    """

    def __init__(
        self,
        api_key: str | None = None,
        project_id: str | None = None,
        url: str | None = None,
        max_tool_rounds: int = 5,
    ) -> None:
        # Resolution order: argument → env var → config.py default
        resolved_api_key = api_key or os.environ.get("WATSONX_API_KEY") or DEFAULT_API_KEY
        resolved_project_id = project_id or os.environ.get("WATSONX_PROJECT_ID") or DEFAULT_PROJECT_ID
        resolved_url = url or os.environ.get("WATSONX_URL") or DEFAULT_URL

        if not resolved_api_key:
            raise ValueError(
                "IBM Cloud API key is required. "
                "Set WATSONX_API_KEY or pass api_key=... to FinancialLiteracyAgent()."
            )
        if not resolved_project_id:
            raise ValueError(
                "watsonx.ai project ID is required. "
                "Set WATSONX_PROJECT_ID or pass project_id=... to FinancialLiteracyAgent()."
            )

        credentials = Credentials(url=resolved_url, api_key=resolved_api_key)
        client = APIClient(credentials=credentials, project_id=resolved_project_id)

        self.model = ModelInference(
            model_id=MODEL_ID,
            api_client=client,
        )
        self.max_tool_rounds = max_tool_rounds

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def chat(
        self,
        user_message: str,
        history: list[dict[str, Any]] | None = None,
        verbose: bool = False,
    ) -> tuple[str, list[dict[str, Any]]]:
        """
        Send a message to the agent and return the assistant reply.

        Parameters
        ----------
        user_message:
            The user's input text.
        history:
            Existing conversation history (list of OpenAI-style message dicts).
            Pass ``None`` to start a new conversation.
        verbose:
            If True, print tool call details to stdout.

        Returns
        -------
        (reply, updated_history)
            ``reply`` is the agent's final plain-text response.
            ``updated_history`` is the full message list including this turn.
        """
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        for round_idx in range(self.max_tool_rounds):
            response = self.model.chat(
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
            )

            choice = response["choices"][0]
            assistant_message: dict[str, Any] = choice["message"]
            finish_reason: str = choice["finish_reason"]

            # Always record the assistant turn
            messages.append(assistant_message)

            if finish_reason == "tool_calls":
                tool_calls: list[dict[str, Any]] = assistant_message.get("tool_calls", [])
                if verbose:
                    print(f"\n[Round {round_idx + 1}] Tool calls: {[tc['function']['name'] for tc in tool_calls]}")

                # Execute every requested tool and append results
                for tc in tool_calls:
                    tool_name = tc["function"]["name"]
                    tool_args = tc["function"]["arguments"]
                    tool_result = dispatch_tool(tool_name, tool_args)

                    if verbose:
                        print(f"  → {tool_name}({tool_args}) = {tool_result[:120]}...")

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": tool_result,
                        }
                    )
                # Loop back to let the model compose a final answer
                continue

            # finish_reason == "stop" (or anything other than "tool_calls")
            reply: str = assistant_message.get("content", "")

            # Return history without the leading system message for cleaner storage
            conversation_history = [m for m in messages if m["role"] != "system"]
            return reply, conversation_history

        # Fallback: ask for a plain answer after exhausting tool rounds
        messages.append(
            {
                "role": "user",
                "content": "Please provide your final answer based on the tool results above.",
            }
        )
        response = self.model.chat(messages=messages)
        reply = response["choices"][0]["message"].get("content", "")
        conversation_history = [m for m in messages if m["role"] != "system"]
        return reply, conversation_history
