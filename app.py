"""
FinLit AI — Digital Financial Literacy Agent
IBM Granite 4H Small · watsonx.ai · Dark ChatGPT-style UI
"""
from __future__ import annotations
import streamlit as st
from dotenv import load_dotenv
from financial_literacy_agent import FinancialLiteracyAgent

load_dotenv()

st.set_page_config(
    page_title="FinLit AI",
    page_icon="🏦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>

/* ── FULLSCREEN / RESET ── */
html, body { margin: 0; padding: 0; background: #212121 !important; }
.stApp, .stApp > div {
    background: #212121 !important;
    margin: 0 !important; padding: 0 !important;
    min-height: 100vh !important;
}
section.main {
    background: #212121 !important;
    padding: 0 !important;
}
section.main > div.block-container {
    padding: 0 !important;
    max-width: 800px !important;
    width: 100% !important;
    margin: 0 auto !important;
    background: #212121 !important;
}
/* hide all chrome */
.stAppHeader,
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
#MainMenu, header, footer { display: none !important; height: 0 !important; }

/* hide sidebar entirely */
[data-testid="stSidebar"] { display: none !important; }

/* ── TOPBAR ── */
.topbar {
    background: #171717;
    border-bottom: 1px solid #2f2f2f;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 28px;
    position: sticky;
    top: 0;
    z-index: 100;
}
.tb-l { display: flex; align-items: center; gap: 12px; }
.tb-logo {
    width: 34px; height: 34px; background: #10a37f;
    border-radius: 9px; display: flex; align-items: center;
    justify-content: center; font-size: 1.05rem; flex-shrink: 0;
}
.tb-title { font-size: 1.05rem; font-weight: 700; color: #ececec; }
.tb-sub   { font-size: 0.73rem; color: #6b7280; }
.tb-r { display: flex; align-items: center; gap: 8px; }
.pill {
    border-radius: 20px; padding: 3px 12px;
    font-size: 0.69rem; font-weight: 600;
}
.pill-g { background: #0a1f13; border: 1px solid #10a37f; color: #10a37f; }
.pill-b { background: #0d0d2a; border: 1px solid #3b5bdb; color: #6b9ef8; }
.ldot {
    display: inline-block; width: 6px; height: 6px;
    background: #10a37f; border-radius: 50%;
    margin-right: 5px; vertical-align: middle;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 5px 0 !important;
    max-width: 800px !important;
    margin: 0 auto !important;
}
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] { display: none !important; }

/* ── CHAT INPUT ── */
[data-testid="stBottom"] {
    background: #171717 !important;
    border-top: 1px solid #2f2f2f !important;
    padding: 16px 0 20px !important;
    position: sticky !important;
    bottom: 0 !important;
    z-index: 99 !important;
}
[data-testid="stBottom"] > div {
    max-width: 800px !important;
    margin: 0 auto !important;
    padding: 0 20px !important;
}
/* visible rounded input box */
[data-testid="stChatInput"],
.stChatInput {
    background: #2f2f2f !important;
    border: 1.5px solid #3a3a3a !important;
    border-radius: 14px !important;
    padding: 2px 6px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stChatInput"]:focus-within,
.stChatInput:focus-within {
    border-color: #10a37f !important;
    box-shadow: 0 0 0 3px rgba(16,163,127,0.12) !important;
}
/* textarea inside — transparent so box shows through */
[data-testid="stChatInputTextArea"] {
    background: transparent !important;
    color: #ececec !important;
    caret-color: #10a37f !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
    padding: 10px 12px !important;
}
[data-testid="stChatInputTextArea"]::placeholder {
    color: #6b7280 !important;
    opacity: 1 !important;
}
/* send button */
[data-testid="stChatInputSubmitButton"] > button {
    background: #10a37f !important;
    border: none !important;
    border-radius: 8px !important;
    color: #fff !important;
    margin: 4px !important;
}
[data-testid="stChatInputSubmitButton"] > button:hover {
    background: #0d8c6c !important;
}
[data-testid="stChatInputSubmitButton"] svg { fill: #fff !important; }

/* ── WELCOME SCREEN ── */
.wl {
    text-align: center;
    padding: 56px 20px 0;
    max-width: 640px;
    margin: 0 auto;
}
.wl-logo  { font-size: 3rem; margin-bottom: 16px; }
.wl-title { font-size: 1.65rem; font-weight: 700; color: #ececec; margin-bottom: 10px; }
.wl-sub   { font-size: 0.9rem; color: #8e8e8e; line-height: 1.8; margin-bottom: 36px; }
.wl-grid  {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 12px; margin-bottom: 16px; text-align: left;
}
.wl-card {
    background: #2a2a2a; border: 1px solid #3a3a3a;
    border-radius: 14px; padding: 16px;
    cursor: default;
}
.wl-ci { font-size: 1.2rem; margin-bottom: 6px; }
.wl-ct { font-size: 0.83rem; font-weight: 600; color: #ececec; margin-bottom: 3px; }
.wl-cd { font-size: 0.75rem; color: #8e8e8e; line-height: 1.5; }

/* ── CHAT PADDING ── */
.chat-pad { padding: 20px 0 8px; }

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for k, v in [("messages", []), ("history", [])]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# AGENT
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_agent() -> FinancialLiteracyAgent:
    return FinancialLiteracyAgent()

try:
    agent = load_agent()
    _ok = True
except Exception as _e:
    _ok, _err = False, str(_e)

# ─────────────────────────────────────────────────────────────────────────────
# TOPBAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="tb-l">
    <div class="tb-logo">🏦</div>
    <span class="tb-title">FinLit AI</span>
    <span class="tb-sub">Digital Financial Literacy Agent</span>
  </div>
  <div class="tb-r">
    <span class="pill pill-g"><span class="ldot"></span>Connected · granite-4-h-small</span>
    <span class="pill pill-b">IBM watsonx.ai</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# GUARD
# ─────────────────────────────────────────────────────────────────────────────
if not _ok:
    st.error(f"Could not connect to watsonx.ai: {_err}")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# WELCOME SCREEN
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state["messages"]:
    st.markdown("""
    <div class="wl">
      <div class="wl-logo">🏦</div>
      <div class="wl-title">How can I help you today?</div>
      <div class="wl-sub">
        I'm <strong style="color:#ececec">FinLit AI</strong> — your Digital Financial Literacy assistant,<br>
        powered by <strong style="color:#10a37f">IBM Granite 4H Small</strong> + RAG on watsonx.ai.<br>
        Ask me about UPI, scams, loans, budgeting, or investing — in 8 Indian languages.
      </div>
      <div class="wl-grid">
        <div class="wl-card">
          <div class="wl-ci">💳</div>
          <div class="wl-ct">UPI &amp; Digital Payments</div>
          <div class="wl-cd">Safe transfers, PhonePe, GPay, BHIM, limits</div>
        </div>
        <div class="wl-card">
          <div class="wl-ci">🚨</div>
          <div class="wl-ct">Fraud &amp; Scam Protection</div>
          <div class="wl-cd">OTP fraud, QR scams, fake bank calls, KYC fraud</div>
        </div>
        <div class="wl-card">
          <div class="wl-ci">📊</div>
          <div class="wl-ct">Loans &amp; Interest Rates</div>
          <div class="wl-cd">Safe borrowing rates, EMI calculator, RBI guidelines</div>
        </div>
        <div class="wl-card">
          <div class="wl-ci">📈</div>
          <div class="wl-ct">Investing &amp; SIP</div>
          <div class="wl-cd">SIP returns, mutual funds, retirement planning</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONVERSATION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="chat-pad">', unsafe_allow_html=True)

for msg in st.session_state["messages"]:
    role, content = msg["role"], msg["content"]
    with st.chat_message(role, avatar=None):
        if role == "user":
            st.markdown(
                f'<div style="background:#2a2a2a;color:#ececec;'
                f'border-radius:18px 18px 4px 18px;padding:12px 16px;'
                f'max-width:72%;margin-left:auto;font-size:0.9rem;'
                f'line-height:1.65;border:1px solid #3a3a3a">{content}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="background:#1e1e1e;color:#ececec;'
                f'border-radius:4px 18px 18px 18px;padding:14px 18px;'
                f'max-width:88%;font-size:0.9rem;line-height:1.8;'
                f'border:1px solid #2f2f2f">{content}</div>',
                unsafe_allow_html=True,
            )

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# INPUT
# ─────────────────────────────────────────────────────────────────────────────
typed = st.chat_input("Message FinLit AI…")

if typed:
    st.session_state["messages"].append({"role": "user", "content": typed})
    with st.chat_message("user", avatar=None):
        st.markdown(
            f'<div style="background:#2a2a2a;color:#ececec;'
            f'border-radius:18px 18px 4px 18px;padding:12px 16px;'
            f'max-width:72%;margin-left:auto;font-size:0.9rem;'
            f'line-height:1.65;border:1px solid #3a3a3a">{typed}</div>',
            unsafe_allow_html=True,
        )

    with st.chat_message("assistant", avatar=None):
        ph = st.empty()
        ph.markdown(
            '<div style="background:#1e1e1e;color:#6b7280;'
            'border-radius:4px 18px 18px 18px;padding:14px 18px;'
            'max-width:88%;font-size:0.9rem;border:1px solid #2f2f2f">'
            '⏳ Thinking…</div>',
            unsafe_allow_html=True,
        )
        try:
            reply, updated_history = agent.chat(typed, history=st.session_state["history"])
            st.session_state["history"] = updated_history
        except Exception as exc:
            reply = f"Sorry, an error occurred: {exc}"
        ph.markdown(
            f'<div style="background:#1e1e1e;color:#ececec;'
            f'border-radius:4px 18px 18px 18px;padding:14px 18px;'
            f'max-width:88%;font-size:0.9rem;line-height:1.8;'
            f'border:1px solid #2f2f2f">{reply}</div>',
            unsafe_allow_html=True,
        )
        st.session_state["messages"].append({"role": "assistant", "content": reply})
