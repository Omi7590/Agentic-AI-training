# RTI Mitra - ui/app.py
# Streamlit chat interface for RTI Mitra.
#
# Features:
#   - Chat with /ask (RAG) or /agent (LangGraph agent)
#   - Shows citations for every answer
#   - Thumbs up / thumbs down feedback saved to ui/feedback.jsonl
#   - Signature feature: Live RTI letter preview
#     As the user types the information sought, it fills the
#     Annexure 'A' format, shows a 150-word counter, a fee box
#     (Rs 10 or nil for BPL) and a 'reply due by' date.

import json
import os
from datetime import datetime, timedelta

import requests
import streamlit as st

API_BASE = os.getenv("RTI_API_BASE", "http://127.0.0.1:8000")
FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "feedback.jsonl")

st.set_page_config(
    page_title="RTI Mitra",
    page_icon="⚖️",
    layout="wide",
)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"thread-{datetime.now().strftime('%H%M%S')}"


# ── Helpers ───────────────────────────────────────────────────────────────────

def ask_api(question: str, use_agent: bool = False) -> dict:
    """Call /ask or /agent and return the response dict."""
    try:
        if use_agent:
            resp = requests.post(
                f"{API_BASE}/agent",
                json={"question": question, "thread_id": st.session_state.thread_id},
                timeout=30,
            )
        else:
            resp = requests.post(
                f"{API_BASE}/ask",
                json={"question": question, "top_k": 5},
                timeout=30,
            )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {
            "answer": "⚠️ Cannot connect to the RTI Mitra API. Make sure the API is running.",
            "citations": [],
        }
    except (ValueError, RuntimeError) as e:
        return {"answer": f"⚠️ Error: {e}", "citations": []}
    except requests.exceptions.RequestException as e:
        return {"answer": f"⚠️ API error: {e}", "citations": []}


def save_feedback(question: str, answer: str, thumb: str):
    """Append thumbs up/down feedback to feedback.jsonl."""
    record = {
        "ts": datetime.now().isoformat(),
        "question": question,
        "answer": answer[:200],
        "feedback": thumb,
    }
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def word_count(text: str) -> int:
    return len([w for w in text.split() if w])


def reply_due_date(via_apio: bool = False) -> str:
    days = 35 if via_apio else 30
    return (datetime.now() + timedelta(days=days)).strftime("%d %B %Y")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg",
        width=60,
    )
    st.title("RTI Mitra ⚖️")
    st.caption("Right to Information Act 2005 — Maharashtra & Central")

    mode = st.radio("Mode", ["RAG (/ask)", "Agent (/agent)"], index=0)
    use_agent = mode == "Agent (/agent)"

    st.divider()
    st.markdown("**About**")
    st.markdown(
        "RTI Mitra explains the RTI Act in simple language and helps draft "
        "correct RTI applications for Maharashtra or central offices."
    )
    st.caption("General information on the RTI Act, not legal advice.")

    st.divider()
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.session_state.thread_id = f"thread-{datetime.now().strftime('%H%M%S')}"
        st.rerun()


# ── Main layout: Chat (left) + Live RTI Preview (right) ──────────────────────
chat_col, preview_col = st.columns([3, 2])

# ── Chat column — messages only ───────────────────────────────────────────────
with chat_col:
    st.header("💬 Chat with RTI Mitra")

    # Scrollable message history container
    messages_container = st.container(height=500)
    with messages_container:
        for i, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

                if msg["role"] == "assistant" and msg.get("citations"):
                    with st.expander("📚 Citations"):
                        for c in msg["citations"]:
                            st.markdown(
                                f"- **{c.get('title', 'Source')}** — "
                                f"[{c.get('source', '')}]({c.get('source', '')})"
                            )

                if msg["role"] == "assistant":
                    col1, col2, _ = st.columns([1, 1, 8])
                    with col1:
                        if st.button("👍", key=f"up_{i}"):
                            save_feedback(
                                st.session_state.messages[i - 1]["content"] if i > 0 else "",
                                msg["content"],
                                "thumbs_up",
                            )
                            st.toast("Thanks! 👍")
                    with col2:
                        if st.button("👎", key=f"down_{i}"):
                            save_feedback(
                                st.session_state.messages[i - 1]["content"] if i > 0 else "",
                                msg["content"],
                                "thumbs_down",
                            )
                            st.toast("Thanks! 👎")

    # Chat input pinned below the message container
    if prompt := st.chat_input("Ask an RTI question...", key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Searching RTI rules..."):
            result = ask_api(prompt, use_agent=use_agent)

        answer = result.get("answer", "No answer returned.")
        citations = result.get("citations", [])

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "citations": citations,
        })
        st.rerun()


# ── Live RTI Letter Preview (Signature feature) ───────────────────────────────
with preview_col:
    st.header("📝 Live RTI Letter Preview")
    st.caption("Fill in the details — the letter updates as you type.")

    applicant_name = st.text_input("Your name", placeholder="Om Jarhad")
    applicant_address = st.text_input(
        "Your address", placeholder="Kopargaon, Dist. Ahmednagar, Maharashtra"
    )
    authority = st.text_input(
        "Authority (PIO office)", placeholder="Kopargaon Panchayat Samiti"
    )
    authority_address = st.text_input(
        "Authority address", placeholder="Kopargaon, Dist. Ahmednagar - 423601"
    )

    information_sought = st.text_area(
        "Information sought (max 150 words for Maharashtra)",
        placeholder="Please provide a copy of the 2026 road-repair work order...",
        height=120,
    )

    col_bpl, col_apio = st.columns(2)
    with col_bpl:
        is_bpl = st.checkbox("BPL applicant (fee exempt)")
    with col_apio:
        via_apio = st.checkbox("Filing via APIO (+5 days)")

    # Live counters
    wc = word_count(information_sought)
    fee = "**Nil** (BPL)" if is_bpl else "**Rs 10**"
    reply_date = reply_due_date(via_apio)

    if wc == 0:
        st.caption("Words: 0 / 150")
    elif wc <= 150:
        st.success(f"✅ Words: {wc} / 150")
    else:
        st.error(f"❌ Words: {wc} / 150 — exceeds Maharashtra limit!")

    col_fee, col_date = st.columns(2)
    with col_fee:
        st.info(f"💰 Fee: {fee}")
    with col_date:
        st.info(f"📅 Reply due: {reply_date}")

    st.divider()

    # Annexure A live letter
    name = applicant_name or "[Your Name]"
    addr = applicant_address or "[Your Address]"
    auth = authority or "[Authority Name]"
    auth_addr = authority_address or "[Authority Address]"
    info = information_sought or "[Describe the information you need]"
    today = datetime.now().strftime("%d %B %Y")
    days = 35 if via_apio else 30
    fee_line = "Nil (BPL — attaching BPL certificate)" if is_bpl else "Rs 10"
    via_note = " (submitted via APIO)" if via_apio else ""

    letter = f"""**To,**
The Public Information Officer,
{auth},
{auth_addr}

**Date:** {today}

**Subject:** Application under the Right to Information Act, 2005{via_note}

Sir/Madam,

I, **{name}**, a citizen of India, hereby request the following
information under Section 6(1) of the RTI Act, 2005:

_{info}_

I am enclosing the application fee of **{fee_line}**.

Please provide the information within **{days} days** as required under
Section 7(1) of the RTI Act, 2005. Reply due by: **{reply_date}**.

Yours faithfully,
**{name}**
{addr}

---
*General information on the RTI Act, not legal advice.*"""

    st.markdown(letter)
