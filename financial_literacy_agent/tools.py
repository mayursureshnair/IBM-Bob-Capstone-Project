"""
Financial literacy tools used by the AI agent.
Each tool is a plain Python function with a corresponding JSON schema definition
that is passed to the Granite 4H Small model via the chat API.
"""

from __future__ import annotations

import json
import math
from typing import Any


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


def calculate_compound_interest(
    principal: float,
    annual_rate_percent: float,
    years: int,
    compounds_per_year: int = 12,
) -> dict[str, Any]:
    """Calculate compound interest and return a breakdown."""
    r = annual_rate_percent / 100
    n = compounds_per_year
    t = years
    final_amount = principal * math.pow(1 + r / n, n * t)
    interest_earned = final_amount - principal
    return {
        "principal": round(principal, 2),
        "annual_rate_percent": annual_rate_percent,
        "years": years,
        "compounds_per_year": compounds_per_year,
        "final_amount": round(final_amount, 2),
        "interest_earned": round(interest_earned, 2),
        "growth_factor": round(final_amount / principal, 4),
    }


def calculate_loan_payment(
    principal: float,
    annual_rate_percent: float,
    term_months: int,
) -> dict[str, Any]:
    """Calculate monthly payment for a fixed-rate loan."""
    r = annual_rate_percent / 100 / 12
    n = term_months
    if r == 0:
        monthly_payment = principal / n
    else:
        monthly_payment = principal * (r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)
    total_paid = monthly_payment * n
    total_interest = total_paid - principal
    return {
        "principal": round(principal, 2),
        "annual_rate_percent": annual_rate_percent,
        "term_months": term_months,
        "monthly_payment": round(monthly_payment, 2),
        "total_paid": round(total_paid, 2),
        "total_interest_paid": round(total_interest, 2),
    }


def calculate_budget(
    monthly_income: float,
    expenses: dict[str, float],
) -> dict[str, Any]:
    """Analyse a monthly budget using the 50/30/20 rule as a benchmark."""
    total_expenses = sum(expenses.values())
    savings = monthly_income - total_expenses
    savings_rate = (savings / monthly_income * 100) if monthly_income > 0 else 0

    # 50/30/20 guideline amounts
    needs_target = monthly_income * 0.50
    wants_target = monthly_income * 0.30
    savings_target = monthly_income * 0.20

    return {
        "monthly_income": round(monthly_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_savings": round(savings, 2),
        "savings_rate_percent": round(savings_rate, 1),
        "expense_breakdown": {k: round(v, 2) for k, v in expenses.items()},
        "benchmark_50_30_20": {
            "needs_50pct_target": round(needs_target, 2),
            "wants_30pct_target": round(wants_target, 2),
            "savings_20pct_target": round(savings_target, 2),
        },
        "is_saving_enough": savings >= savings_target,
    }


def explain_financial_concept(concept: str) -> dict[str, Any]:
    """
    Return a structured plain-language explanation for a financial concept.
    The agent itself will generate rich prose, but this tool provides
    a concise definition + key facts stub so the model can ground its answer.
    """
    concepts: dict[str, dict[str, Any]] = {
        "compound interest": {
            "definition": "Interest calculated on both the initial principal and the accumulated interest.",
            "key_points": [
                "Often called 'the eighth wonder of the world'.",
                "Time is the most powerful variable — start early.",
                "Frequency of compounding matters (daily > monthly > annually).",
            ],
            "formula": "A = P(1 + r/n)^(nt)",
        },
        "emergency fund": {
            "definition": "Liquid savings set aside exclusively for unexpected expenses or income loss.",
            "key_points": [
                "Recommended size: 3–6 months of living expenses.",
                "Keep in a high-yield savings account, not investments.",
                "Replenish immediately after use.",
            ],
        },
        "diversification": {
            "definition": "Spreading investments across different assets to reduce risk.",
            "key_points": [
                "Don't put all eggs in one basket.",
                "Across asset classes: stocks, bonds, real estate.",
                "Within asset classes: sectors, geographies.",
            ],
        },
        "inflation": {
            "definition": "The rate at which the general level of prices rises, eroding purchasing power.",
            "key_points": [
                "2% annual inflation is the central-bank target in many countries.",
                "Cash loses real value over time; invest to stay ahead.",
                "CPI (Consumer Price Index) is the common measure.",
            ],
        },
        "debt-to-income ratio": {
            "definition": "Monthly debt payments divided by gross monthly income, expressed as a percentage.",
            "key_points": [
                "Lenders typically want DTI < 36%.",
                "High DTI limits borrowing ability.",
                "Formula: (total monthly debt / gross monthly income) × 100.",
            ],
        },
        "index fund": {
            "definition": "A passive investment fund that tracks a market index (e.g. S&P 500).",
            "key_points": [
                "Low cost compared to actively managed funds.",
                "Broad diversification in one instrument.",
                "Historically outperforms most active managers long-term.",
            ],
        },
    }

    key = concept.lower().strip()
    if key in concepts:
        return {"concept": concept, **concepts[key]}

    # Fallback — the model will still answer from its training
    return {
        "concept": concept,
        "definition": f"No pre-loaded definition for '{concept}'. "
        "Answer using general financial knowledge.",
        "key_points": [],
    }


def calculate_retirement_savings(
    current_age: int,
    retirement_age: int,
    current_savings: float,
    monthly_contribution: float,
    expected_annual_return_percent: float,
) -> dict[str, Any]:
    """Project retirement savings using monthly compounding."""
    months = (retirement_age - current_age) * 12
    r = expected_annual_return_percent / 100 / 12

    # Future value of current savings
    fv_current = current_savings * math.pow(1 + r, months)

    # Future value of monthly contributions (annuity)
    if r == 0:
        fv_contributions = monthly_contribution * months
    else:
        fv_contributions = monthly_contribution * ((math.pow(1 + r, months) - 1) / r)

    total_at_retirement = fv_current + fv_contributions
    total_contributed = current_savings + monthly_contribution * months
    total_growth = total_at_retirement - total_contributed

    return {
        "current_age": current_age,
        "retirement_age": retirement_age,
        "years_to_retirement": retirement_age - current_age,
        "current_savings": round(current_savings, 2),
        "monthly_contribution": round(monthly_contribution, 2),
        "expected_annual_return_percent": expected_annual_return_percent,
        "projected_balance_at_retirement": round(total_at_retirement, 2),
        "total_amount_contributed": round(total_contributed, 2),
        "total_investment_growth": round(total_growth, 2),
    }


def get_upi_guidance(query_type: str) -> dict[str, Any]:
    """
    Return structured guidance on UPI (Unified Payments Interface) usage.
    query_type options: 'how_to_send', 'safety_tips', 'limits', 'troubleshoot', 'apps', 'general'
    """
    guidance: dict[str, Any] = {
        "how_to_send": {
            "topic": "How to Send Money via UPI",
            "steps": [
                "1. Open any UPI app (PhonePe, Google Pay, Paytm, BHIM).",
                "2. Tap 'Send Money' or 'Pay'.",
                "3. Enter the recipient's UPI ID (e.g. name@upi) OR scan their QR code.",
                "4. Enter the amount and an optional note.",
                "5. Review details carefully — double-check the name that appears.",
                "6. Enter your 4- or 6-digit UPI PIN to authorise.",
                "7. You'll get an instant confirmation SMS and in-app notification.",
            ],
            "important": "Never enter your UPI PIN when RECEIVING money — you only need it to SEND.",
            "source": "NPCI (National Payments Corporation of India)",
        },
        "safety_tips": {
            "topic": "UPI Safety Tips",
            "dos": [
                "Verify the recipient's name before confirming any payment.",
                "Use UPI only on official bank or NPCI-approved apps.",
                "Enable app lock / biometric authentication on your UPI app.",
                "Check your transaction history regularly.",
                "Use UPI Lite for small amounts (up to ₹500) for extra convenience.",
            ],
            "donts": [
                "Never share your UPI PIN with anyone — not even bank staff.",
                "Never click on UPI payment links sent via SMS/WhatsApp from strangers.",
                "Never scan a QR code sent by someone claiming to 'send' you money.",
                "Never enter your PIN on a screen-share call.",
            ],
            "emergency": "If you suspect fraud, call your bank immediately and file a complaint at cybercrime.gov.in or call 1930.",
        },
        "limits": {
            "topic": "UPI Transaction Limits",
            "per_transaction_limit": "₹1,00,000 (₹1 lakh) per transaction for most banks",
            "daily_limit": "Varies by bank — typically ₹1 lakh to ₹5 lakh per day",
            "upi_lite_limit": "₹500 per transaction, ₹2,000 wallet balance",
            "higher_limits": "Some categories like healthcare and education allow up to ₹5 lakh",
            "note": "Limits are set by your bank and may differ. Check with your bank for exact limits.",
        },
        "apps": {
            "topic": "Popular UPI Apps in India",
            "apps": [
                {"name": "BHIM", "by": "NPCI (Government)", "note": "Official government UPI app, most trusted"},
                {"name": "PhonePe", "by": "Walmart/PhonePe", "note": "Largest UPI app by volume"},
                {"name": "Google Pay (GPay)", "by": "Google", "note": "Simple interface, good for beginners"},
                {"name": "Paytm", "by": "Paytm", "note": "Also offers wallet, insurance, investments"},
                {"name": "Amazon Pay", "by": "Amazon", "note": "Integrated with Amazon shopping"},
            ],
            "tip": "All these apps use the same UPI network — money sent from any app arrives instantly.",
        },
        "troubleshoot": {
            "topic": "UPI Troubleshooting",
            "common_issues": [
                {"issue": "Transaction pending/failed", "fix": "Wait 24–48 hours; if deducted, it auto-reverses. Contact bank if not resolved."},
                {"issue": "Wrong UPI PIN", "fix": "You have limited attempts; reset via bank app using debit card details."},
                {"issue": "UPI ID not found", "fix": "Double-check spelling. Ask recipient to share their exact UPI ID from their app."},
                {"issue": "Daily limit exceeded", "fix": "Wait until midnight or use net banking for large transfers."},
            ],
            "helplines": {"NPCI": "1800-120-1740", "Cyber Crime": "1930"},
        },
    }
    key = query_type.lower().strip()
    result = guidance.get(key, guidance["safety_tips"])
    result["query_type"] = query_type
    return result


def assess_scam_risk(scenario: str) -> dict[str, Any]:
    """
    Assess whether a described financial scenario is likely a scam.
    Provides risk level, red flags, and recommended actions.
    """
    scenario_lower = scenario.lower()

    red_flags_found = []
    risk_score = 0

    patterns = [
        (["otp", "one time password", "verification code"], "Asking for OTP — NEVER share this", 40),
        (["qr code", "scan", "receive money", "collect money"], "QR code scam pattern — scanning QR codes SENDS money, never receives it", 35),
        (["screen share", "anydesk", "teamviewer", "remote"], "Remote access / screen-sharing scam — fraudsters can steal banking credentials", 40),
        (["kyc", "kyc update", "kyc expiry", "kyc verify"], "Fake KYC update scam — banks do not call to collect KYC via phone", 35),
        (["prize", "lottery", "won", "winner", "congratulations"], "Lottery/prize scam — too good to be true", 30),
        (["double", "guaranteed return", "risk free", "1000% profit"], "Guaranteed high-return investment scam", 35),
        (["impersonate", "rbi officer", "police", "cyber crime officer", "ed officer"], "Authority impersonation scam", 40),
        (["link", "click", "verify account", "suspended", "blocked"], "Phishing link / account suspension scam", 30),
        (["advance fee", "process fee", "tax fee", "custom duty"], "Advance fee fraud", 30),
        (["pin", "password", "cvv"], "Asking for PIN/password/CVV — no legitimate entity does this", 45),
    ]

    for keywords, flag, score in patterns:
        if any(k in scenario_lower for k in keywords):
            red_flags_found.append(flag)
            risk_score += score

    risk_score = min(risk_score, 100)
    if risk_score >= 60:
        risk_level = "🔴 HIGH RISK — Very likely a scam"
    elif risk_score >= 30:
        risk_level = "🟠 MEDIUM RISK — Suspicious, proceed with extreme caution"
    else:
        risk_level = "🟡 LOW RISK — Some caution advised"

    return {
        "scenario_summary": scenario[:200],
        "risk_level": risk_level,
        "risk_score": risk_score,
        "red_flags_detected": red_flags_found if red_flags_found else ["No specific red flags matched — use general caution"],
        "recommended_actions": [
            "Do NOT share any OTP, PIN, password, or banking credentials.",
            "Hang up / stop communication with the suspicious party immediately.",
            "Contact your bank's official helpline (number on the back of your card).",
            "Report to: cybercrime.gov.in or call 1930 (National Cyber Crime Helpline).",
            "Block the number/account that contacted you.",
        ],
        "reminder": "Legitimate banks, RBI, SEBI, and police will NEVER ask for your OTP, PIN, or password.",
    }


def get_loan_interest_info(loan_type: str) -> dict[str, Any]:
    """
    Return information about typical and safe interest rates for different loan types in India.
    loan_type options: 'personal', 'home', 'education', 'gold', 'vehicle', 'microfinance', 'credit_card'
    """
    loan_data: dict[str, Any] = {
        "personal": {
            "loan_type": "Personal Loan",
            "safe_rate_range": "10% – 18% p.a.",
            "typical_bank_rate": "10.5% – 15% p.a.",
            "nbfc_rate": "14% – 24% p.a.",
            "red_flag_rate": "Above 30% p.a. — likely predatory",
            "lenders": ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "Bajaj Finserv"],
            "tips": [
                "Compare total cost (APR), not just advertised rate.",
                "Watch out for processing fees (0.5–3% of loan amount).",
                "Prepayment penalties can add cost — check the fine print.",
                "Avoid loans from unregulated apps — they may charge 40–100% p.a.",
            ],
            "rbi_guideline": "RBI mandates lenders to disclose Annualised Percentage Rate (APR). Always ask for it.",
        },
        "home": {
            "loan_type": "Home Loan",
            "safe_rate_range": "8.5% – 9.5% p.a. (floating)",
            "typical_bank_rate": "8.5% – 9.25% p.a.",
            "red_flag_rate": "Above 12% p.a. for home loans is unusual — shop around",
            "tips": [
                "Floating rates linked to RBI Repo Rate are transparent.",
                "PMAY (PM Awas Yojana) subsidises interest for EWS/LIG/MIG categories.",
                "A 1% lower rate on ₹50 lakh over 20 years saves ~₹7 lakh.",
            ],
        },
        "education": {
            "loan_type": "Education Loan",
            "safe_rate_range": "8% – 11% p.a.",
            "typical_bank_rate": "8% – 10.5% p.a.",
            "tips": [
                "Vidya Lakshmi Portal (vidyalakshmi.co.in) lists government-backed education loans.",
                "Moratorium period (no EMI during study + 1 year) is standard.",
                "Under CSIS scheme, interest subsidy available for EWS students.",
            ],
        },
        "gold": {
            "loan_type": "Gold Loan",
            "safe_rate_range": "7% – 12% p.a.",
            "typical_bank_rate": "7% – 10% p.a.",
            "tips": [
                "Gold loans are secured — typically lower rates than personal loans.",
                "Ensure you use RBI-regulated banks or NBFCs (Muthoot, Manappuram, etc.).",
                "LTV (Loan to Value) capped at 75% of gold value by RBI.",
            ],
        },
        "credit_card": {
            "loan_type": "Credit Card Outstanding",
            "safe_rate_range": "N/A — avoid carrying balance",
            "typical_bank_rate": "36% – 42% p.a. (3–3.5% per month)",
            "red_flag_rate": "Credit card revolving debt is ALWAYS expensive",
            "tips": [
                "Always pay the FULL outstanding, not just minimum due.",
                "Minimum payment trap: ₹50,000 at 3.5%/month takes years to clear.",
                "Use credit card only if you can pay 100% by due date.",
            ],
        },
        "microfinance": {
            "loan_type": "Microfinance / SHG Loan",
            "safe_rate_range": "18% – 26% p.a. (RBI-capped for MFIs)",
            "red_flag_rate": "Above 30% — check if lender is RBI-registered",
            "tips": [
                "RBI caps MFI lending rate at 22% p.a. (MCLR-based) as of 2023.",
                "Avoid informal moneylenders charging 40–120% p.a.",
                "SHG bank linkage through NABARD often offers 7–12% p.a.",
                "Verify lender's RBI/NBFC registration at rbi.org.in.",
            ],
        },
    }

    key = loan_type.lower().strip().replace(" ", "_")
    result = loan_data.get(key, loan_data["personal"])
    result["loan_type_queried"] = loan_type
    return result


def calculate_sip_returns(
    monthly_investment: float,
    annual_return_percent: float,
    years: int,
) -> dict[str, Any]:
    """
    Calculate returns from a SIP (Systematic Investment Plan) — monthly investment
    in a mutual fund with compounding.
    """
    n = years * 12
    r = annual_return_percent / 100 / 12
    if r == 0:
        future_value = monthly_investment * n
    else:
        future_value = monthly_investment * ((math.pow(1 + r, n) - 1) / r) * (1 + r)

    total_invested = monthly_investment * n
    wealth_gained = future_value - total_invested

    return {
        "monthly_sip_amount": round(monthly_investment, 2),
        "annual_return_percent": annual_return_percent,
        "investment_period_years": years,
        "total_months": n,
        "total_amount_invested": round(total_invested, 2),
        "estimated_returns": round(wealth_gained, 2),
        "total_value_at_maturity": round(future_value, 2),
        "wealth_multiplier": round(future_value / total_invested, 2),
        "note": "SIP returns are market-linked. Past returns do not guarantee future performance.",
    }


# ---------------------------------------------------------------------------
# JSON Schema definitions for the chat API
# ---------------------------------------------------------------------------

TOOLS_SCHEMA: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "calculate_compound_interest",
            "description": (
                "Calculate compound interest given a principal, annual interest rate, "
                "number of years, and compounding frequency. Returns the final amount "
                "and total interest earned."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "principal": {"type": "number", "description": "Initial investment or deposit amount."},
                    "annual_rate_percent": {"type": "number", "description": "Annual interest rate as a percentage (e.g. 5 for 5%)."},
                    "years": {"type": "integer", "description": "Number of years to grow the investment."},
                    "compounds_per_year": {
                        "type": "integer",
                        "description": "Number of times interest compounds per year. Default 12 (monthly).",
                        "default": 12,
                    },
                },
                "required": ["principal", "annual_rate_percent", "years"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_loan_payment",
            "description": (
                "Calculate the monthly payment, total amount paid, and total interest "
                "for a fixed-rate loan given the principal, annual rate, and term in months."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "principal": {"type": "number", "description": "Loan amount."},
                    "annual_rate_percent": {"type": "number", "description": "Annual interest rate as a percentage."},
                    "term_months": {"type": "integer", "description": "Loan term in months."},
                },
                "required": ["principal", "annual_rate_percent", "term_months"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_budget",
            "description": (
                "Analyse a monthly budget by comparing income against expenses and "
                "benchmarking against the 50/30/20 rule. Returns savings rate and "
                "whether the user is saving enough."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "monthly_income": {"type": "number", "description": "Total gross monthly income."},
                    "expenses": {
                        "type": "object",
                        "description": "Dictionary of expense categories and their monthly amounts.",
                        "additionalProperties": {"type": "number"},
                    },
                },
                "required": ["monthly_income", "expenses"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_financial_concept",
            "description": (
                "Retrieve a concise definition and key facts for a financial concept "
                "(e.g. 'compound interest', 'emergency fund', 'diversification', "
                "'inflation', 'debt-to-income ratio', 'index fund')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "concept": {"type": "string", "description": "The financial concept to explain."},
                },
                "required": ["concept"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_retirement_savings",
            "description": (
                "Project the retirement savings balance using monthly compounding "
                "given current age, retirement age, current savings, monthly "
                "contribution, and expected annual return."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "current_age": {"type": "integer", "description": "Current age of the user."},
                    "retirement_age": {"type": "integer", "description": "Target retirement age."},
                    "current_savings": {"type": "number", "description": "Current retirement savings balance."},
                    "monthly_contribution": {"type": "number", "description": "Monthly contribution to retirement savings."},
                    "expected_annual_return_percent": {"type": "number", "description": "Expected annual return as a percentage."},
                },
                "required": [
                    "current_age",
                    "retirement_age",
                    "current_savings",
                    "monthly_contribution",
                    "expected_annual_return_percent",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_upi_guidance",
            "description": (
                "Get structured guidance on UPI (Unified Payments Interface) — how to send money, "
                "safety tips, transaction limits, popular apps, or troubleshooting. "
                "Use this for any question about UPI, digital payments, PhonePe, GPay, Paytm, BHIM."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query_type": {
                        "type": "string",
                        "enum": ["how_to_send", "safety_tips", "limits", "apps", "troubleshoot", "general"],
                        "description": "The aspect of UPI the user is asking about.",
                    },
                },
                "required": ["query_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "assess_scam_risk",
            "description": (
                "Assess whether a financial scenario described by the user is likely a scam. "
                "Use this whenever the user describes a suspicious call, message, request, "
                "or situation involving money, OTP, QR codes, or unknown contacts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "description": "A description of the suspicious situation or message the user received.",
                    },
                },
                "required": ["scenario"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_loan_interest_info",
            "description": (
                "Get information about typical and safe interest rates for different loan types in India "
                "(personal, home, education, gold, vehicle, microfinance, credit_card). "
                "Use this when asked about loan rates, EMIs, safe borrowing, or comparing lenders."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "loan_type": {
                        "type": "string",
                        "enum": ["personal", "home", "education", "gold", "vehicle", "microfinance", "credit_card"],
                        "description": "The type of loan the user is asking about.",
                    },
                },
                "required": ["loan_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_sip_returns",
            "description": (
                "Calculate the future value of a SIP (Systematic Investment Plan) — "
                "monthly mutual fund investment with compounding. Use this when the user "
                "asks about SIP, monthly investment projections, or mutual fund returns."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "monthly_investment": {"type": "number", "description": "Monthly SIP investment amount (in any currency/₹)."},
                    "annual_return_percent": {"type": "number", "description": "Expected annual return percentage (e.g. 12 for 12%)."},
                    "years": {"type": "integer", "description": "Investment duration in years."},
                },
                "required": ["monthly_investment", "annual_return_percent", "years"],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# Dispatcher — maps tool name → function
# ---------------------------------------------------------------------------

TOOL_REGISTRY: dict[str, Any] = {
    "calculate_compound_interest": calculate_compound_interest,
    "calculate_loan_payment": calculate_loan_payment,
    "calculate_budget": calculate_budget,
    "explain_financial_concept": explain_financial_concept,
    "calculate_retirement_savings": calculate_retirement_savings,
    "get_upi_guidance": get_upi_guidance,
    "assess_scam_risk": assess_scam_risk,
    "get_loan_interest_info": get_loan_interest_info,
    "calculate_sip_returns": calculate_sip_returns,
}


def dispatch_tool(name: str, arguments_json: str) -> str:
    """Execute a tool by name and return its result as a JSON string."""
    if name not in TOOL_REGISTRY:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        args = json.loads(arguments_json)
        result = TOOL_REGISTRY[name](**args)
        return json.dumps(result, indent=2)
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": str(exc)})
