# RTI Mitra - ui/app.py
# Modern Streamlit chat UI for RTI Mitra

import json
import os
from datetime import datetime, timedelta

import requests
import streamlit as st

API_BASE = os.getenv("RTI_API_BASE", "http://127.0.0.1:8000")
FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "feedback.jsonl")

st.set_page_config(
    page_title="RTI Mitra — Right to Information Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Modern CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Import font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide default streamlit header/footer */
#MainMenu, footer, header {visibility: hidden;}

/* Main background */
.stApp {
    background: #0f1117;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] .stMarkdown p {
    color: #8b949e;
    font-size: 0.85rem;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
    padding: 12px 16px !important;
}

/* User message */
[data-testid="stChatMessage"][data-testid*="user"] {
    background: #1f2937 !important;
}

/* Input box */
[data-testid="stChatInput"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    color: #e6edf3 !important;
    font-size: 0.95rem !important;
}

/* Text inputs */
.stTextInput input, .stTextArea textarea {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
    font-size: 0.88rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 3px rgba(88,166,255,0.1) !important;
}

/* Labels */
.stTextInput label, .stTextArea label {
    color: #8b949e !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

/* Buttons */
.stButton button {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #8b949e !important;
    font-size: 0.85rem !important;
    transition: all 0.2s !important;
}
.stButton button:hover {
    background: #30363d !important;
    border-color: #58a6ff !important;
    color: #58a6ff !important;
}

/* Success/error/info boxes */
.stSuccess {
    background: rgba(35,134,54,0.1) !important;
    border: 1px solid rgba(35,134,54,0.3) !important;
    border-radius: 8px !important;
    color: #3fb950 !important;
}
.stError {
    background: rgba(248,81,73,0.1) !important;
    border: 1px solid rgba(248,81,73,0.3) !important;
    border-radius: 8px !important;
}
.stInfo {
    background: rgba(88,166,255,0.08) !important;
    border: 1px solid rgba(88,166,255,0.2) !important;
    border-radius: 8px !important;
    color: #58a6ff !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 8px !important;
}

/* Divider */
hr {
    border-color: #21262d !important;
}

/* Headers */
h1, h2, h3 {
    color: #e6edf3 !important;
    font-weight: 600 !important;
}

/* Radio */
.stRadio label {
    color: #8b949e !important;
}
.stRadio [data-testid="stMarkdownContainer"] p {
    color: #e6edf3 !important;
}

/* Checkbox */
.stCheckbox label {
    color: #8b949e !important;
    font-size: 0.85rem !important;
}

/* Scrollable container */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important;
}

/* Letter preview box */
.letter-box {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px;
    font-family: 'Georgia', serif;
    font-size: 0.85rem;
    line-height: 1.8;
    color: #c9d1d9;
}

/* Badge pill */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
}
.badge-green { background: rgba(35,134,54,0.2); color: #3fb950; border: 1px solid rgba(35,134,54,0.3); }
.badge-blue  { background: rgba(88,166,255,0.1); color: #58a6ff; border: 1px solid rgba(88,166,255,0.2); }
.badge-orange{ background: rgba(210,153,34,0.1); color: #d29922; border: 1px solid rgba(210,153,34,0.3); }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"thread-{datetime.now().strftime('%H%M%S')}"


# ── Helpers ───────────────────────────────────────────────────────────────────

def ask_api(question: str, use_agent: bool = False) -> dict:
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
        return {"answer": "⚠️ Cannot connect to the RTI Mitra API.", "citations": []}
    except (ValueError, RuntimeError) as e:
        return {"answer": f"⚠️ Error: {e}", "citations": []}
    except requests.exceptions.RequestException as e:
        return {"answer": f"⚠️ API error: {e}", "citations": []}


def save_feedback(question: str, answer: str, thumb: str):
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
    st.markdown("""
    <div style='display:flex;align-items:center;gap:12px;padding:8px 0 16px 0;border-bottom:1px solid #21262d;margin-bottom:16px'>
        <img src='https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg' width='36'/>
        <div>
            <div style='color:#e6edf3;font-weight:700;font-size:1.1rem;'>RTI Mitra</div>
            <div style='color:#8b949e;font-size:0.75rem;'>Right to Information AI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="color:#8b949e;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px">Mode</div>', unsafe_allow_html=True)
    mode = st.radio("", ["RAG (/ask)", "Agent (/agent)"], index=0, label_visibility="collapsed")
    use_agent = mode == "Agent (/agent)"

    st.markdown('<br>', unsafe_allow_html=True)

    # API status
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        if r.status_code == 200:
            st.markdown('<span class="badge badge-green">● API Online</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge badge-orange">● API Degraded</span>', unsafe_allow_html=True)
    except Exception:  # noqa: BLE001
        st.markdown('<span class="badge badge-orange">● API Offline</span>', unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#1a2233;border:1px solid #21262d;border-radius:10px;padding:12px;margin-bottom:12px'>
        <div style='color:#8b949e;font-size:0.75rem;margin-bottom:6px;font-weight:600'>QUICK QUESTIONS</div>
        <div style='color:#58a6ff;font-size:0.8rem;line-height:1.8'>
            • RTI fee in Maharashtra?<br>
            • PIO reply deadline?<br>
            • Draft RTI to Kopargaon Samiti<br>
            • BPL fee exemption?<br>
            • First appeal process?
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🗑️ New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = f"thread-{datetime.now().strftime('%H%M%S')}"
        st.rerun()

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div style="color:#484f58;font-size:0.72rem;text-align:center">General information on the RTI Act,<br>not legal advice.</div>', unsafe_allow_html=True)


# ── Main layout ───────────────────────────────────────────────────────────────
chat_col, preview_col = st.columns([3, 2], gap="medium")

# ── Chat column ───────────────────────────────────────────────────────────────
with chat_col:
    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;margin-bottom:16px'>
        <div style='font-size:1.4rem'>💬</div>
        <div>
            <div style='color:#e6edf3;font-weight:700;font-size:1.15rem'>Chat with RTI Mitra</div>
            <div style='color:#8b949e;font-size:0.78rem'>Ask anything about the RTI Act 2005</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Welcome message if no messages
    if not st.session_state.messages:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#1a2233,#161b22);border:1px solid #21262d;border-radius:14px;padding:24px;text-align:center;margin-bottom:16px'>
            <div style='font-size:2rem;margin-bottom:8px'>⚖️</div>
            <div style='color:#e6edf3;font-weight:600;font-size:1rem;margin-bottom:6px'>Welcome to RTI Mitra</div>
            <div style='color:#8b949e;font-size:0.85rem;line-height:1.6'>
                I help you understand your rights under the RTI Act 2005<br>
                and draft correct RTI applications for Maharashtra or central offices.
            </div>
            <div style='display:flex;justify-content:center;gap:8px;margin-top:16px;flex-wrap:wrap'>
                <span class="badge badge-blue">📋 Draft RTI letters</span>
                <span class="badge badge-green">📖 Explain RTI rules</span>
                <span class="badge badge-orange">⏱️ Compute deadlines</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    messages_container = st.container(height=480)
    with messages_container:
        for i, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

                if msg["role"] == "assistant" and msg.get("citations"):
                    with st.expander("📚 Sources & Citations"):
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
                            st.toast("Helpful! Thanks 👍")
                    with col2:
                        if st.button("👎", key=f"down_{i}"):
                            save_feedback(
                                st.session_state.messages[i - 1]["content"] if i > 0 else "",
                                msg["content"],
                                "thumbs_down",
                            )
                            st.toast("Thanks for the feedback 👎")

    if prompt := st.chat_input("Ask an RTI question...", key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with messages_container, st.chat_message("user"):
            st.markdown(prompt)

        with messages_container, st.chat_message("assistant"):
            with st.spinner("Searching RTI rules..."):
                result = ask_api(prompt, use_agent=use_agent)

            answer = result.get("answer", "No answer returned.")
            citations = result.get("citations", [])
            st.markdown(answer)

            if citations:
                with st.expander("📚 Sources & Citations"):
                    for c in citations:
                        st.markdown(
                            f"- **{c.get('title', 'Source')}** — "
                            f"[{c.get('source', '')}]({c.get('source', '')})"
                        )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "citations": citations,
        })
        st.rerun()


# ── Live RTI Letter Preview ───────────────────────────────────────────────────
with preview_col:
    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;margin-bottom:16px'>
        <div style='font-size:1.4rem'>📋</div>
        <div>
            <div style='color:#e6edf3;font-weight:700;font-size:1.15rem'>Live RTI Letter</div>
            <div style='color:#8b949e;font-size:0.78rem'>Fills as you type · Annexure A format</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        applicant_name = st.text_input("Your full name", placeholder="Om Jarhad", label_visibility="visible")
        applicant_address = st.text_input("Your address", placeholder="Kopargaon, Dist. Ahmednagar, Maharashtra")
        authority = st.text_input("Authority / PIO office", placeholder="Kopargaon Panchayat Samiti")
        authority_address = st.text_input("Authority address", placeholder="Kopargaon, Dist. Ahmednagar - 423601")
        information_sought = st.text_area(
            "Information sought",
            placeholder="Please provide a copy of the 2026 road-repair work order...",
            height=100,
        )

        col_bpl, col_apio = st.columns(2)
        with col_bpl:
            is_bpl = st.checkbox("BPL (fee exempt)")
        with col_apio:
            via_apio = st.checkbox("Via APIO (+5 days)")

    # Live stats bar
    wc = word_count(information_sought)
    fee = "Nil (BPL)" if is_bpl else "Rs 10"
    reply_date = reply_due_date(via_apio)
    days = 35 if via_apio else 30

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        color = "#3fb950" if wc <= 150 else "#f85149"
        st.markdown(f'<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:8px;text-align:center"><div style="color:{color};font-weight:700;font-size:1rem">{wc}/150</div><div style="color:#8b949e;font-size:0.7rem">words</div></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:8px;text-align:center"><div style="color:#58a6ff;font-weight:700;font-size:1rem">{fee}</div><div style="color:#8b949e;font-size:0.7rem">fee</div></div>', unsafe_allow_html=True)
    with col_c:
        st.markdown(f'<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:8px;text-align:center"><div style="color:#d29922;font-weight:700;font-size:0.75rem">{reply_date}</div><div style="color:#8b949e;font-size:0.7rem">reply due</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Letter preview
    name = applicant_name or "[Your Name]"
    addr = applicant_address or "[Your Address]"
    auth = authority or "[Authority Name]"
    auth_addr = authority_address or "[Authority Address]"
    info = information_sought or "[Describe the information you need — max 150 words for Maharashtra]"
    today = datetime.now().strftime("%d %B %Y")
    fee_line = "Nil (BPL — attaching BPL certificate)" if is_bpl else "Rs 10"
    via_note = " (submitted via APIO)" if via_apio else ""

    letter_html = f"""
    <div class="letter-box">
        <div style="font-size:0.75rem;color:#484f58;margin-bottom:12px;text-transform:uppercase;letter-spacing:0.05em">Annexure A — RTI Application</div>
        <b>To,</b><br>
        The Public Information Officer,<br>
        {auth},<br>
        {auth_addr}<br><br>
        <b>Date:</b> {today}<br><br>
        <b>Subject:</b> Application under the Right to Information Act, 2005{via_note}<br><br>
        Sir/Madam,<br><br>
        I, <b>{name}</b>, a citizen of India, hereby request the following information
        under Section 6(1) of the RTI Act, 2005:<br><br>
        <i style="color:#a5d6ff">{info}</i><br><br>
        I am enclosing the application fee of <b>{fee_line}</b>.<br><br>
        Please provide the information within <b>{days} days</b> as required under
        Section 7(1) of the RTI Act, 2005. Reply due by: <b>{reply_date}</b>.<br><br>
        Yours faithfully,<br>
        <b>{name}</b><br>
        {addr}<br><br>
        <div style="font-size:0.72rem;color:#484f58;border-top:1px solid #21262d;padding-top:8px;margin-top:8px">
        General information on the RTI Act, not legal advice.
        </div>
    </div>
    """
    st.markdown(letter_html, unsafe_allow_html=True)
