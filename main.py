"""
Command-line interface for the Digital Financial Literacy AI Agent.

Usage:
    python main.py

Environment variables required:
    WATSONX_API_KEY      — IBM Cloud API key
    WATSONX_PROJECT_ID   — watsonx.ai project ID

Optional:
    WATSONX_URL          — watsonx.ai service URL (default: us-south Dallas)
"""

from __future__ import annotations

import os
import sys
import textwrap

from dotenv import load_dotenv

from financial_literacy_agent import FinancialLiteracyAgent

# Load .env file if present
load_dotenv()

BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║       💰  FinLit AI — Digital Financial Literacy Agent  💰       ║
║          Powered by IBM Granite 4H Small on watsonx.ai           ║
╚══════════════════════════════════════════════════════════════════╝

Type your question and press Enter. Commands:
  /help    — show example questions
  /clear   — start a new conversation
  /quit    — exit
"""

HELP_TEXT = """
Example questions you can ask:
──────────────────────────────
  • "If I invest $5,000 at 7% for 20 years, how much will I have?"
  • "What is my monthly payment on a $250,000 mortgage at 6.5% for 30 years?"
  • "I earn $4,500/month. My rent is $1,200, groceries $400, utilities $150,
     subscriptions $80, dining $300. Am I on track with the 50/30/20 rule?"
  • "Explain compound interest in simple terms."
  • "I'm 30 years old with $15,000 saved. If I contribute $400/month and
     expect 8% returns, what will I have at 65?"
  • "What is an emergency fund and how big should mine be?"
  • "Help me understand diversification."
──────────────────────────────
"""


def print_wrapped(text: str, width: int = 80) -> None:
    """Print text with line wrapping, preserving paragraph breaks."""
    paragraphs = text.split("\n")
    for para in paragraphs:
        if para.strip():
            print(textwrap.fill(para.strip(), width=width))
        else:
            print()


def main() -> None:
    print(BANNER)

    print("Connecting to watsonx.ai … ", end="", flush=True)
    try:
        agent = FinancialLiteracyAgent()   # credentials resolved from config.py / env
        print("✓ Ready!\n")
    except Exception as exc:
        print(f"\nFailed to initialise agent: {exc}")
        sys.exit(1)

    history: list = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/quit", "/exit", "quit", "exit"):
            print("Goodbye! Keep learning and keep saving 💪")
            break

        if user_input.lower() == "/help":
            print(HELP_TEXT)
            continue

        if user_input.lower() == "/clear":
            history = []
            print("─── Conversation cleared. Starting fresh. ───\n")
            continue

        print("\nFinLit AI: ", end="", flush=True)
        try:
            reply, history = agent.chat(user_input, history=history)
            print()
            print_wrapped(reply)
            print()
        except Exception as exc:  # noqa: BLE001
            print(f"\n[Error] {exc}\n")


if __name__ == "__main__":
    main()
