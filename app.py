import streamlit as st
import time
import os
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS — Premium Redesign ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

/* ══════════════════════════════════════════════════════════════════════════════
   DESIGN TOKENS
   ══════════════════════════════════════════════════════════════════════════════ */
:root {
    --bg-primary:    #0c0f14;
    --bg-secondary:  #12161e;
    --bg-card:       #161b26;
    --bg-elevated:   #1c2333;
    --bg-input:      #1a1f2e;

    --border-subtle: rgba(255,255,255,0.06);
    --border-medium: rgba(255,255,255,0.10);
    --border-strong: rgba(255,255,255,0.15);

    --accent:        #f59e0b;
    --accent-hover:  #fbbf24;
    --accent-muted:  rgba(245,158,11,0.15);
    --accent-glow:   rgba(245,158,11,0.25);
    --teal:          #14b8a6;
    --teal-muted:    rgba(20,184,166,0.15);
    --blue:          #3b82f6;
    --blue-muted:    rgba(59,130,246,0.15);
    --rose:          #f43f5e;
    --rose-muted:    rgba(244,63,94,0.12);

    --success:       #22c55e;
    --success-muted: rgba(34,197,94,0.15);
    --warning:       #eab308;
    --danger:        #ef4444;

    --text-primary:   #f1f5f9;
    --text-secondary: #94a3b8;
    --text-tertiary:  #64748b;
    --text-faint:     #475569;

    --radius-sm:  8px;
    --radius-md:  12px;
    --radius-lg:  16px;
    --radius-xl:  20px;

    --shadow-card: 0 1px 3px rgba(0,0,0,0.3), 0 4px 20px rgba(0,0,0,0.2);
    --shadow-elevated: 0 4px 30px rgba(0,0,0,0.4);
    --shadow-glow: 0 0 40px rgba(245,158,11,0.08);

    --transition: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ══════════════════════════════════════════════════════════════════════════════
   GLOBAL RESET
   ══════════════════════════════════════════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.stApp {
    background: var(--bg-primary) !important;
}

/* subtle radial glow behind content */
.stApp::before {
    content: '';
    position: fixed;
    top: -20%; left: 50%;
    transform: translateX(-50%);
    width: 900px; height: 900px;
    background: radial-gradient(circle, rgba(245,158,11,0.04) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* ── Typography ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}

p, span, li, div {
    font-family: 'Inter', sans-serif;
}

/* ══════════════════════════════════════════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

/* Sidebar brand area */
.sidebar-brand {
    padding: 0.25rem 0 1rem 0;
    margin-bottom: 0.25rem;
}

.sidebar-brand-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.35rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    line-height: 1.2;
}

.sidebar-brand-title span {
    background: linear-gradient(135deg, var(--accent) 0%, #f97316 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.sidebar-brand-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-tertiary);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

/* Sidebar section labels */
.sidebar-section {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-tertiary);
    margin: 1rem 0 0.6rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border-subtle);
}

.sidebar-section::before {
    content: '';
    width: 3px;
    height: 12px;
    border-radius: 2px;
    background: var(--accent);
    flex-shrink: 0;
}

/* ══════════════════════════════════════════════════════════════════════════════
   HERO AREA
   ══════════════════════════════════════════════════════════════════════════════ */
.hero-container {
    padding: 1.5rem 0 0.5rem 0;
}

.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.hero-eyebrow::before {
    content: '';
    width: 24px;
    height: 1px;
    background: var(--accent);
}

.hero-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -0.03em;
    margin: 0;
    color: var(--text-primary);
}

.hero-title .gradient-text {
    background: linear-gradient(135deg, var(--accent) 0%, #fb923c 40%, var(--teal) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    font-weight: 400;
    color: var(--text-secondary);
    margin-top: 0.6rem;
    line-height: 1.6;
}

/* thin decorative separator */
.hero-divider {
    height: 1px;
    background: linear-gradient(90deg, var(--accent) 0%, var(--border-subtle) 40%, transparent 100%);
    margin: 1.5rem 0;
    border: none;
}

/* ══════════════════════════════════════════════════════════════════════════════
   CARDS
   ══════════════════════════════════════════════════════════════════════════════ */
.glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color var(--transition), box-shadow var(--transition), transform var(--transition);
    box-shadow: var(--shadow-card);
}

.glass-card:hover {
    border-color: var(--border-strong);
    box-shadow: var(--shadow-elevated);
    transform: translateY(-2px);
}

/* accent strip on left */
.glass-card.accent-amber::before  { content:''; position:absolute; top:0; left:0; width:3px; height:100%; background: linear-gradient(180deg, var(--accent), #f97316); border-radius: 3px 0 0 3px; }
.glass-card.accent-teal::before   { content:''; position:absolute; top:0; left:0; width:3px; height:100%; background: linear-gradient(180deg, var(--teal), #0ea5e9);  border-radius: 3px 0 0 3px; }
.glass-card.accent-blue::before   { content:''; position:absolute; top:0; left:0; width:3px; height:100%; background: linear-gradient(180deg, var(--blue), #8b5cf6);  border-radius: 3px 0 0 3px; }
.glass-card.accent-rose::before   { content:''; position:absolute; top:0; left:0; width:3px; height:100%; background: linear-gradient(180deg, var(--rose), #ec4899);  border-radius: 3px 0 0 3px; }
.glass-card.accent-green::before  { content:''; position:absolute; top:0; left:0; width:3px; height:100%; background: linear-gradient(180deg, var(--success), var(--teal)); border-radius: 3px 0 0 3px; }

.card-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1rem;
}

.card-icon {
    width: 32px; height: 32px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    flex-shrink: 0;
}

.card-icon.amber  { background: var(--accent-muted); }
.card-icon.teal   { background: var(--teal-muted); }
.card-icon.blue   { background: var(--blue-muted); }
.card-icon.rose   { background: var(--rose-muted); }
.card-icon.green  { background: var(--success-muted); }

.card-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-tertiary);
}

.card-body {
    font-size: 0.88rem;
    line-height: 1.75;
    color: var(--text-secondary);
}

.card-body-large {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
    line-height: 1.3;
}

/* ══════════════════════════════════════════════════════════════════════════════
   BADGES
   ══════════════════════════════════════════════════════════════════════════════ */
.pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.3rem 0.75rem;
    border-radius: 100px;
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}

.pill-amber  { background: var(--accent-muted); color: var(--accent-hover); border: 1px solid rgba(245,158,11,0.20); }
.pill-teal   { background: var(--teal-muted);   color: var(--teal);         border: 1px solid rgba(20,184,166,0.20); }
.pill-green  { background: var(--success-muted); color: var(--success);     border: 1px solid rgba(34,197,94,0.20); }
.pill-blue   { background: var(--blue-muted);    color: var(--blue);        border: 1px solid rgba(59,130,246,0.20); }

/* ══════════════════════════════════════════════════════════════════════════════
   INPUTS & BUTTONS
   ══════════════════════════════════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    transition: border-color var(--transition), box-shadow var(--transition) !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-muted) !important;
}

.stTextInput > div > div > input::placeholder {
    color: var(--text-faint) !important;
}

/* Primary button */
.stButton > button {
    background: linear-gradient(135deg, var(--accent) 0%, #d97706 100%) !important;
    color: #0c0f14 !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.03em !important;
    padding: 0.65rem 1.5rem !important;
    transition: all var(--transition) !important;
    box-shadow: 0 2px 8px rgba(245,158,11,0.25) !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(245,158,11,0.35) !important;
    filter: brightness(1.08) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

/* Secondary button */
.stButton > button[kind="secondary"] {
    background: var(--bg-elevated) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-medium) !important;
    box-shadow: none !important;
}

.stButton > button[kind="secondary"]:hover {
    border-color: var(--border-strong) !important;
    color: var(--text-primary) !important;
    background: var(--bg-card) !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   PIPELINE STATUS BAR
   ══════════════════════════════════════════════════════════════════════════════ */
.pipeline-step {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.6rem 0.85rem;
    background: var(--bg-card);
    border-radius: var(--radius-sm);
    margin: 0.3rem 0;
    border: 1px solid var(--border-subtle);
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-secondary);
    transition: all var(--transition);
}

.pipeline-step:hover {
    background: var(--bg-elevated);
}

.step-indicator {
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
    transition: all var(--transition);
}

.ind-active  {
    background: var(--accent);
    box-shadow: 0 0 10px var(--accent-glow);
    animation: pulse-amber 1.8s ease-in-out infinite;
}
.ind-done    { background: var(--success); box-shadow: 0 0 6px rgba(34,197,94,0.3); }
.ind-pending { background: var(--text-faint); }

@keyframes pulse-amber {
    0%, 100% { opacity: 1; box-shadow: 0 0 10px var(--accent-glow); }
    50%      { opacity: 0.45; box-shadow: 0 0 4px var(--accent-glow); }
}

/* ══════════════════════════════════════════════════════════════════════════════
   CHAT UI
   ══════════════════════════════════════════════════════════════════════════════ */
.chat-area {
    background: var(--bg-card);
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    max-height: 440px;
    overflow-y: auto;
    margin-bottom: 1rem;
}

.chat-message {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.chat-sender {
    font-family: 'Inter', sans-serif;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.chat-text {
    display: inline-block;
    padding: 0.65rem 1rem;
    border-radius: var(--radius-md);
    font-size: 0.84rem;
    line-height: 1.65;
    max-width: 88%;
}

.sender-user   { color: var(--accent); }
.sender-bot    { color: var(--teal); }

.bubble-user {
    background: var(--accent-muted);
    border: 1px solid rgba(245,158,11,0.18);
    align-self: flex-end;
    color: var(--text-primary);
}

.bubble-bot {
    background: rgba(20,184,166,0.08);
    border: 1px solid rgba(20,184,166,0.15);
    align-self: flex-start;
    color: var(--text-secondary);
}

/* ══════════════════════════════════════════════════════════════════════════════
   EMPTY STATE
   ══════════════════════════════════════════════════════════════════════════════ */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
}

.empty-icon {
    width: 72px; height: 72px;
    border-radius: var(--radius-lg);
    background: var(--accent-muted);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 0 50px rgba(245,158,11,0.08);
}

.empty-heading {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.empty-desc {
    font-size: 0.88rem;
    color: var(--text-tertiary);
    max-width: 420px;
    line-height: 1.7;
    margin-bottom: 1.75rem;
}

.feature-pills {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    justify-content: center;
}

/* ══════════════════════════════════════════════════════════════════════════════
   TRANSCRIPT BOX
   ══════════════════════════════════════════════════════════════════════════════ */
.transcript-box {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 1.25rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.85;
    max-height: 320px;
    overflow-y: auto;
    color: var(--text-tertiary);
    white-space: pre-wrap;
    word-break: break-word;
}

/* ══════════════════════════════════════════════════════════════════════════════
   STREAMLIT OVERRIDES
   ══════════════════════════════════════════════════════════════════════════════ */
.stProgress > div > div > div { background: linear-gradient(90deg, var(--accent), var(--teal)) !important; }
.stSpinner > div { border-top-color: var(--accent) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text-secondary) !important; }
label { color: var(--text-tertiary) !important; font-family: 'Inter', sans-serif !important; font-size: 0.78rem !important; font-weight: 500 !important; }

hr {
    border: none !important;
    border-top: 1px solid var(--border-subtle) !important;
    margin: 1.25rem 0 !important;
}

/* expander styling */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: var(--radius-md) !important;
}

[data-testid="stExpander"] summary {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    color: var(--text-secondary) !important;
}

/* scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--text-faint); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* Alert overrides */
[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    font-family: 'Inter', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
def step_css(steps: dict, key: str) -> str:
    s = steps.get(key, "pending")
    if s == "active":  return "ind-active"
    if s == "done":    return "ind-done"
    return "ind-pending"

def render_pipeline_step(label: str, key: str, icon: str):
    css = step_css(st.session_state.pipeline_steps, key)
    st.markdown(f"""
    <div class="pipeline-step">
        <div class="step-indicator {css}"></div>
        <span>{icon}&ensp;{label}</span>
    </div>""", unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">🎬 <span>AI Video</span><br>Assistant</div>
        <div class="sidebar-brand-sub">Meeting Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Source input
    st.markdown('<div class="sidebar-section">Source Input</div>', unsafe_allow_html=True)
    source = st.text_input(
        "YouTube URL or File Path",
        placeholder="https://youtube.com/watch?v=... or C:\\path\\to\\file.mp4",
    )
    language = st.selectbox("Language", ["english", "hinglish"], index=0)

    # ── API Configuration
    st.markdown('<div class="sidebar-section">API Configuration</div>', unsafe_allow_html=True)
    current_key = os.getenv("MISTRAL_API_KEY", "")
    if current_key == "your_mistral_api_key_here":
        current_key = ""

    mistral_key_input = st.text_input(
        "Mistral API Key",
        value=current_key,
        type="password",
        placeholder="Paste your API key here",
        help="Get a key from https://console.mistral.ai/",
    )

    if mistral_key_input.strip():
        os.environ["MISTRAL_API_KEY"] = mistral_key_input.strip()
        try:
            with open(".env", "w") as f:
                f.write(f"MISTRAL_API_KEY={mistral_key_input.strip()}\n")
        except Exception:
            pass

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    run_btn = st.button("⚡  Run Analysis", use_container_width=True)

    # ── Pipeline Status (Placeholder for real-time updates)
    status_placeholder = st.empty()

def draw_status():
    with status_placeholder.container():
        st.markdown('<div class="sidebar-section">Pipeline Status</div>', unsafe_allow_html=True)
        for step_key, icon, label in [
            ("audio",      "🔊", "Audio Processing"),
            ("transcript", "📝", "Transcription"),
            ("title",      "🏷️",  "Title Generation"),
            ("summary",    "📋", "Summarisation"),
            ("extract",    "🔍", "Extraction"),
            ("rag",        "🧠", "RAG Engine"),
        ]:
            render_pipeline_step(label, step_key, icon)

if st.session_state.pipeline_done or st.session_state.processing:
    draw_status()

# ─── Main Area — Hero ───────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-eyebrow">AI-Powered Analysis</div>
    <div class="hero-title">
        <span class="gradient-text">Video &amp; Meeting</span><br>
        Intelligence
    </div>
    <div class="hero-subtitle">
        Transcribe, summarise, extract insights, and chat with your meetings — powered by Whisper &amp; Mistral AI.
    </div>
</div>
<div class="hero-divider"></div>
""", unsafe_allow_html=True)

# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    if not os.getenv("MISTRAL_API_KEY") or os.getenv("MISTRAL_API_KEY") == "your_mistral_api_key_here":
        st.error("❌ Please enter a valid Mistral API Key in the sidebar.")
    elif not source.strip():
        st.error("Please enter a YouTube URL or file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.processing = True
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state
            draw_status()

        try:
            with progress_placeholder.container():
                st.info("⚙️  Pipeline running — check sidebar for live progress…")

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items = extract_action_items(transcript)
            decisions    = extract_key_decisions(transcript)
            questions    = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            st.session_state.processing = False
            progress_placeholder.success("✅  Analysis complete!")
            time.sleep(0.5)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            st.session_state.processing = False
            for k in ["audio", "transcript", "title", "summary", "extract", "rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            draw_status()
            progress_placeholder.error(f"❌  Error: {e}")

# ── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # ── Title banner
    st.markdown(f"""
    <div class="glass-card accent-amber" style="padding:1.75rem">
        <div class="card-header">
            <div class="card-icon amber">📌</div>
            <div class="card-label">Session Title</div>
        </div>
        <div class="card-body-large">{r['title']}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Summary + Transcript row
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown(f"""
        <div class="glass-card accent-teal">
            <div class="card-header">
                <div class="card-icon teal">📋</div>
                <div class="card-label">Summary</div>
            </div>
            <div class="card-body">{r['summary']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        with st.expander("📝  Full Transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)

    # ── Action Items | Decisions | Questions row
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="glass-card accent-green">
            <div class="card-header">
                <div class="card-icon green">✅</div>
                <div class="card-label">Action Items</div>
            </div>
            <div class="card-body">{r['action_items']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="glass-card accent-blue">
            <div class="card-header">
                <div class="card-icon blue">🔑</div>
                <div class="card-label">Key Decisions</div>
            </div>
            <div class="card-body">{r['key_decisions']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="glass-card accent-rose">
            <div class="card-header">
                <div class="card-icon rose">❓</div>
                <div class="card-label">Open Questions</div>
            </div>
            <div class="card-body">{r['open_questions']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="hero-divider"></div>', unsafe_allow_html=True)

    # ── RAG Chat ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem">
        <div class="card-icon amber" style="width:28px;height:28px;font-size:0.85rem">💬</div>
        <span style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.1rem;font-weight:700;color:var(--text-primary)">
            Chat with your Meeting
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Chat history display
    if st.session_state.chat_history:
        chat_html = '<div class="chat-area">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-message" style="align-items:flex-end">
                    <span class="chat-sender sender-user">You</span>
                    <div class="chat-text bubble-user">{msg['content']}</div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-message" style="align-items:flex-start">
                    <span class="chat-sender sender-bot">🤖 Assistant</span>
                    <div class="chat-text bubble-bot">{msg['content']}</div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:2.25rem">
            <div style="font-size:1.8rem;margin-bottom:0.5rem">💬</div>
            <div style="color:var(--text-tertiary);font-size:0.85rem;font-weight:500">
                Ask anything about your meeting transcript
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat input
    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input(
            "Your question",
            placeholder="What were the main decisions made?",
            label_visibility="collapsed",
        )
    with chat_col2:
        send_btn = st.button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user",      "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️  Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    # ── Empty state
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🎬</div>
        <div class="empty-heading">Ready to Analyse</div>
        <div class="empty-desc">
            Paste a YouTube URL or local file path in the sidebar,
            choose your language, and hit <strong>Run Analysis</strong> to get started.
        </div>
        <div class="feature-pills">
            <span class="pill pill-amber">⚡ Transcription</span>
            <span class="pill pill-teal">📋 Summarisation</span>
            <span class="pill pill-green">✅ Action Items</span>
            <span class="pill pill-blue">💬 RAG Chat</span>
        </div>
    </div>
    """, unsafe_allow_html=True)