import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Design system ─────────────────────────────────────────────────────────────
# Palette: near-white canvas, deep navy base, electric indigo accent, soft sage for success
# Type: Space Grotesk (display) + Inter (body) + JetBrains Mono (labels/code)
# Signature: animated gradient "scanner" line that pulses on the active pipeline step

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #1a1f36;
}

/* ── Canvas ── */
.stApp {
    background: #f5f6fa;
    min-height: 100vh;
}

/* ── Hide chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Layout shell ── */
.rm-shell {
    display: grid;
    grid-template-columns: 300px 1fr;
    grid-template-rows: 64px 1fr;
    min-height: 100vh;
    max-width: 1440px;
    margin: 0 auto;
}

/* ── Top bar ── */
.rm-topbar {
    grid-column: 1 / -1;
    background: #ffffff;
    border-bottom: 1px solid #e8eaf0;
    display: flex;
    align-items: center;
    padding: 0 2rem;
    gap: 1rem;
    position: sticky;
    top: 0;
    z-index: 100;
}
.rm-logo {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #1a1f36;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.rm-logo-dot {
    width: 8px;
    height: 8px;
    background: #4f46e5;
    border-radius: 50%;
    display: inline-block;
}
.rm-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 400;
    color: #6b7280;
    background: #f0f1f5;
    border: 1px solid #e2e4ec;
    border-radius: 4px;
    padding: 0.2rem 0.55rem;
    letter-spacing: 0.05em;
}
.rm-topbar-right {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 1.5rem;
}
.rm-status-dot {
    width: 7px;
    height: 7px;
    background: #10b981;
    border-radius: 50%;
    display: inline-block;
    margin-right: 0.4rem;
}
.rm-status-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #6b7280;
    letter-spacing: 0.05em;
}

/* ── Sidebar ── */
.rm-sidebar {
    grid-column: 1;
    background: #ffffff;
    border-right: 1px solid #e8eaf0;
    padding: 2rem 1.5rem;
    min-height: calc(100vh - 64px);
}
.rm-sidebar-section {
    margin-bottom: 2.5rem;
}
.rm-sidebar-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid #f0f1f5;
}

/* ── Pipeline steps in sidebar ── */
.pipeline-step {
    display: flex;
    align-items: flex-start;
    gap: 0.9rem;
    padding: 0.85rem 0.7rem;
    border-radius: 10px;
    margin-bottom: 0.3rem;
    transition: background 0.2s;
    position: relative;
}
.pipeline-step.state-waiting  { background: transparent; }
.pipeline-step.state-running  { background: #eef2ff; }
.pipeline-step.state-done     { background: #f0fdf4; }

.pipeline-step-icon {
    width: 34px;
    height: 34px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    flex-shrink: 0;
}
.state-waiting  .pipeline-step-icon { background: #f3f4f6; }
.state-running  .pipeline-step-icon { background: #e0e7ff; }
.state-done     .pipeline-step-icon { background: #dcfce7; }

.pipeline-step-body { flex: 1; }
.pipeline-step-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    color: #1a1f36;
    margin-bottom: 0.12rem;
}
.state-waiting .pipeline-step-name { color: #9ca3af; }

.pipeline-step-desc {
    font-size: 0.72rem;
    color: #9ca3af;
    line-height: 1.4;
}
.state-running .pipeline-step-desc { color: #6366f1; }
.state-done    .pipeline-step-desc { color: #10b981; }

.pipeline-step-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.08em;
    font-weight: 500;
    padding: 0.15rem 0.45rem;
    border-radius: 4px;
    align-self: center;
    flex-shrink: 0;
}
.state-waiting .pipeline-step-badge  { background: #f3f4f6; color: #d1d5db; }
.state-running .pipeline-step-badge  { background: #e0e7ff; color: #4f46e5; }
.state-done    .pipeline-step-badge  { background: #dcfce7; color: #059669; }

/* Scanner animation for running step */
@keyframes scan {
    0%   { opacity: 0.3; transform: scaleX(0); }
    50%  { opacity: 1;   transform: scaleX(1); }
    100% { opacity: 0.3; transform: scaleX(0); }
}
.pipeline-step.state-running::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0.7rem; right: 0.7rem;
    height: 1.5px;
    background: linear-gradient(90deg, transparent, #4f46e5, transparent);
    border-radius: 1px;
    animation: scan 1.6s ease-in-out infinite;
    transform-origin: left;
}

/* Connector line between steps */
.pipeline-connector {
    width: 1px;
    height: 10px;
    background: #e8eaf0;
    margin: 0 auto 0 1.3rem;
}

/* ── Main content area ── */
.rm-main {
    grid-column: 2;
    padding: 2.5rem 3rem;
    overflow-y: auto;
}

/* ── Input card ── */
.rm-input-card {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 16px;
    padding: 2rem 2.5rem 1.8rem;
    margin-bottom: 2.5rem;
    box-shadow: 0 1px 4px rgba(26,31,54,0.04);
}
.rm-input-heading {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1f36;
    letter-spacing: -0.02em;
    margin-bottom: 0.35rem;
}
.rm-input-sub {
    font-size: 0.875rem;
    color: #6b7280;
    margin-bottom: 1.5rem;
    line-height: 1.5;
}

/* ── Streamlit widget overrides ── */
.stTextInput > div > div > input {
    background: #f8f9fc !important;
    border: 1.5px solid #e2e4ec !important;
    border-radius: 10px !important;
    color: #1a1f36 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.8rem 1.1rem !important;
    transition: border-color 0.18s, box-shadow 0.18s !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input::placeholder { color: #c0c4d4 !important; }
.stTextInput > div > div > input:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.1) !important;
    background: #ffffff !important;
}
.stTextInput > label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: #6b7280 !important;
    font-weight: 500 !important;
    margin-bottom: 0.4rem !important;
}

/* ── Button ── */
.stButton > button {
    background: #4f46e5 !important;
    color: #ffffff !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.01em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.72rem 2rem !important;
    cursor: pointer !important;
    transition: background 0.15s, transform 0.1s, box-shadow 0.15s !important;
    box-shadow: 0 2px 8px rgba(79,70,229,0.22) !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #4338ca !important;
    box-shadow: 0 4px 16px rgba(79,70,229,0.3) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Example chips ── */
.rm-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1.2rem;
    align-items: center;
}
.rm-chip-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: #c0c4d4;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.rm-chip {
    background: #f3f4f6;
    border: 1px solid #e8eaf0;
    border-radius: 6px;
    padding: 0.3rem 0.75rem;
    font-size: 0.78rem;
    color: #4b5563;
    font-family: 'Inter', sans-serif;
    cursor: default;
    transition: background 0.15s;
}
.rm-chip:hover { background: #eef2ff; border-color: #c7d2fe; color: #4f46e5; }

/* ── Results section ── */
.rm-results-heading {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #1a1f36;
    letter-spacing: -0.02em;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.rm-results-heading::before {
    content: '';
    display: block;
    width: 4px;
    height: 1.2rem;
    background: #4f46e5;
    border-radius: 2px;
}

/* ── Expander overrides ── */
details {
    background: #ffffff;
    border: 1px solid #e8eaf0 !important;
    border-radius: 12px !important;
    margin-bottom: 0.75rem;
    overflow: hidden;
}
details[open] { box-shadow: 0 1px 4px rgba(26,31,54,0.05); }
details summary {
    padding: 1rem 1.4rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: #374151 !important;
    cursor: pointer;
    list-style: none;
    user-select: none;
}
details summary::-webkit-details-marker { display: none; }

/* ── Raw output block ── */
.rm-raw {
    background: #f8f9fc;
    border-top: 1px solid #f0f1f5;
    padding: 1.2rem 1.4rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #4b5563;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 320px;
    overflow-y: auto;
}

/* ── Report panel ── */
.rm-report {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(26,31,54,0.04);
}
.rm-report-header {
    padding: 1.1rem 1.8rem;
    background: #f8f9fc;
    border-bottom: 1px solid #e8eaf0;
    display: flex;
    align-items: center;
    gap: 0.7rem;
}
.rm-report-header-icon {
    width: 28px;
    height: 28px;
    background: #eef2ff;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
}
.rm-report-header-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.88rem;
    font-weight: 600;
    color: #1a1f36;
}
.rm-report-header-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: #9ca3af;
    margin-left: auto;
    letter-spacing: 0.08em;
}
.rm-report-body {
    padding: 2rem 2.2rem;
}
/* Markdown within report */
.rm-report-body h1, .rm-report-body h2, .rm-report-body h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #1a1f36 !important;
}

/* ── Critic panel ── */
.rm-critic {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(26,31,54,0.04);
}
.rm-critic-header {
    padding: 1.1rem 1.8rem;
    background: #f0fdf4;
    border-bottom: 1px solid #d1fae5;
    display: flex;
    align-items: center;
    gap: 0.7rem;
}
.rm-critic-header-icon {
    width: 28px;
    height: 28px;
    background: #dcfce7;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
}
.rm-critic-header-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.88rem;
    font-weight: 600;
    color: #065f46;
}
.rm-critic-body { padding: 2rem 2.2rem; }

/* ── Download button override ── */
.stDownloadButton > button {
    background: #ffffff !important;
    color: #4f46e5 !important;
    border: 1.5px solid #c7d2fe !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.4rem !important;
    box-shadow: none !important;
    width: auto !important;
    transition: background 0.15s, border-color 0.15s !important;
}
.stDownloadButton > button:hover {
    background: #eef2ff !important;
    border-color: #a5b4fc !important;
    transform: none !important;
}

/* ── Spinner ── */
.stSpinner > div { color: #4f46e5 !important; }
[data-testid="stSpinner"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    color: #6b7280 !important;
    letter-spacing: 0.06em !important;
}

/* ── Divider ── */
.rm-divider {
    height: 1px;
    background: #e8eaf0;
    margin: 2rem 0;
}

/* ── Footer ── */
.rm-footer {
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e8eaf0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.rm-footer-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #d1d5db;
    letter-spacing: 0.08em;
}

/* ── Warning / info override ── */
.stAlert {
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Pipeline step state helper ────────────────────────────────────────────────
def step_state(step):
    r = st.session_state.results
    steps = ["search", "reader", "writer", "critic"]
    if step in r:
        return "done"
    if st.session_state.running:
        for k in steps:
            if k not in r:
                return "running" if k == step else "waiting"
    return "waiting"


# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rm-topbar">
    <div class="rm-logo">
        <span class="rm-logo-dot"></span>
        ResearchMind
    </div>
    <span class="rm-badge">MULTI-AGENT</span>
    <div class="rm-topbar-right">
        <span class="rm-status-text">
            <span class="rm-status-dot"></span>AGENTS READY
        </span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Two-column layout ─────────────────────────────────────────────────────────
sidebar_col, main_col = st.columns([1, 3], gap="small")


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with sidebar_col:
    st.markdown('<div style="padding: 2rem 0.5rem 2rem 1rem;">', unsafe_allow_html=True)

    # Pipeline section
    st.markdown('<div class="rm-sidebar-label">Pipeline</div>', unsafe_allow_html=True)

    pipeline_steps = [
        ("search", "🔍", "Search Agent",  "Web information retrieval"),
        ("reader", "📄", "Reader Agent",  "Deep content extraction"),
        ("writer", "✍️", "Writer",        "Report synthesis"),
        ("critic", "🧐", "Critic",        "Quality assessment"),
    ]

    for i, (key, icon, name, desc) in enumerate(pipeline_steps):
        state = step_state(key)
        badge_map = {"waiting": "IDLE", "running": "RUNNING", "done": "DONE"}
        badge = badge_map[state]
        st.markdown(f"""
        <div class="pipeline-step state-{state}">
            <div class="pipeline-step-icon">{icon}</div>
            <div class="pipeline-step-body">
                <div class="pipeline-step-name">{name}</div>
                <div class="pipeline-step-desc">{desc}</div>
            </div>
            <div class="pipeline-step-badge">{badge}</div>
        </div>
        {"<div class='pipeline-connector'></div>" if i < len(pipeline_steps)-1 else ""}
        """, unsafe_allow_html=True)

    # About section
    st.markdown('<div style="margin-top: 2.5rem;" class="rm-sidebar-label">About</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 0.78rem; color: #9ca3af; line-height: 1.7;">
        Four specialized AI agents work in sequence to search the web, extract deep content, 
        draft a structured report, and provide quality feedback — all from a single query.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ── MAIN CONTENT ──────────────────────────────────────────────────────────────
with main_col:
    st.markdown('<div style="padding: 2.5rem 2rem 2rem;">', unsafe_allow_html=True)

    # Input card
    st.markdown("""
    <div class="rm-input-card">
        <div class="rm-input-heading">What should we research?</div>
        <div class="rm-input-sub">
            Enter any topic and the pipeline will gather, synthesize, and critique a full report.
        </div>
    </div>
    """, unsafe_allow_html=True)

    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("Run Research Pipeline →", use_container_width=True)

    # Example chips
    st.markdown("""
    <div class="rm-chips">
        <span class="rm-chip-label">Try →</span>
        <span class="rm-chip">LLM agents 2025</span>
        <span class="rm-chip">CRISPR gene editing</span>
        <span class="rm-chip">Fusion energy progress</span>
        <span class="rm-chip">Autonomous vehicles</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="rm-divider"></div>', unsafe_allow_html=True)

    # ── Trigger ──────────────────────────────────────────────────────────────
    if run_btn:
        if not topic.strip():
            st.warning("Please enter a research topic to begin.")
        else:
            st.session_state.results = {}
            st.session_state.running = True
            st.session_state.done = False
            st.rerun()

    if st.session_state.running and not st.session_state.done:
        results = {}
        topic_val = st.session_state.topic_input

        with st.spinner("Search Agent · Gathering web information…"):
            search_agent = build_search_agent()
            sr = search_agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
            })
            results["search"] = sr["messages"][-1].content
            st.session_state.results = dict(results)

        with st.spinner("Reader Agent · Extracting deep content…"):
            reader_agent = build_reader_agent()
            rr = reader_agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic_val}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{results['search'][:800]}"
                )]
            })
            results["reader"] = rr["messages"][-1].content
            st.session_state.results = dict(results)

        with st.spinner("Writer · Drafting the research report…"):
            research_combined = (
                f"SEARCH RESULTS:\n{results['search']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
            )
            results["writer"] = writer_chain.invoke({
                "topic": topic_val,
                "research": research_combined
            })
            st.session_state.results = dict(results)

        with st.spinner("Critic · Reviewing and scoring the report…"):
            results["critic"] = critic_chain.invoke({
                "report": results["writer"]
            })
            st.session_state.results = dict(results)

        st.session_state.running = False
        st.session_state.done = True
        st.rerun()

    # ── Results ───────────────────────────────────────────────────────────────
    r = st.session_state.results

    if r:
        st.markdown('<div class="rm-results-heading">Results</div>', unsafe_allow_html=True)

        # Raw outputs — collapsible
        if "search" in r:
            with st.expander("🔍  Search Results", expanded=False):
                st.markdown(f'<div class="rm-raw">{r["search"]}</div>', unsafe_allow_html=True)

        if "reader" in r:
            with st.expander("📄  Scraped Content", expanded=False):
                st.markdown(f'<div class="rm-raw">{r["reader"]}</div>', unsafe_allow_html=True)

        # Final report
        if "writer" in r:
            st.markdown("""
            <div class="rm-report">
                <div class="rm-report-header">
                    <div class="rm-report-header-icon">📝</div>
                    <span class="rm-report-header-title">Research Report</span>
                    <span class="rm-report-header-sub">WRITER OUTPUT</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.container():
                st.markdown(r["writer"])

            st.download_button(
                label="⬇  Download as Markdown",
                data=r["writer"],
                file_name=f"research_report_{int(time.time())}.md",
                mime="text/markdown",
            )

        # Critic
        if "critic" in r:
            st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="rm-critic">
                <div class="rm-critic-header">
                    <div class="rm-critic-header-icon">✅</div>
                    <span class="rm-critic-header-title">Critic Feedback</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.container():
                st.markdown(r["critic"])

    # Footer
    st.markdown("""
    <div class="rm-footer">
        <span class="rm-footer-text">RESEARCHMIND · LANGCHAIN MULTI-AGENT · STREAMLIT</span>
        <span class="rm-footer-text">v1.0</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)