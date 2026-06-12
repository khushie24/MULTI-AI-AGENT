import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nexus Research",
    page_icon="✧",
    layout="centered", # Centered layout creates a cleaner, focused single-column reading experience
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* ── Global Styles ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #e2e8f0;
}

.stApp {
    background: #090d16;
}

/* ── Hide Streamlit Chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 3rem 1.5rem 6rem; max-width: 800px; }

/* ── Header / Top Bar ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #1e293b;
    margin-bottom: 4rem;
}
.topbar-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #f8fafc;
}
.topbar-logo span {
    color: #38bdf8;
    font-weight: 400;
}
.topbar-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.05em;
    color: #64748b;
    background: #1e293b;
    padding: 0.25rem 0.6rem;
    border-radius: 4px;
}

/* ── Hero Presentation ── */
.hero {
    text-align: center;
    margin-bottom: 3.5rem;
}
.hero-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #38bdf8;
    margin-bottom: 1rem;
}
.hero h1 {
    font-size: 3rem;
    font-weight: 700;
    line-height: 1.15;
    letter-spacing: -0.03em;
    color: #f8fafc;
    margin: 0 0 1rem;
}
.hero-desc {
    font-size: 1.05rem;
    font-weight: 400;
    color: #94a3b8;
    max-width: 580px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ── Input & Form Fields ── */
.stTextInput > div > div > input {
    background: #111827 !important;
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
    color: #f9fafb !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.2s ease !important;
    caret-color: #38bdf8 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 1px #38bdf8 !important;
}
.stTextInput > label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.05em;
    text-transform: uppercase !important;
    color: #94a3b8 !important;
    margin-bottom: 0.5rem !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #38bdf8 !important;
    color: #0f172a !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.7rem 1.5rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15) !important;
}
.stButton > button:hover {
    background: #7dd3fc !important;
    box-shadow: 0 4px 20px rgba(56, 189, 248, 0.3) !important;
}

/* ── Modern Status Grid Pipeline ── */
.pipeline-container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin: 2.5rem 0;
}
.pipeline-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 1.2rem;
    transition: all 0.3s ease;
}
.card-waiting { opacity: 0.4; }
.card-running { 
    border-color: #38bdf8; 
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.1);
    animation: pulse 2s infinite ease-in-out;
}
.card-done { border-color: #10b981; }

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}
.card-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #64748b;
}
.card-running .card-num { color: #38bdf8; }
.card-done .card-num { color: #10b981; }

.card-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #f8fafc;
}
.card-desc {
    font-size: 0.8rem;
    color: #94a3b8;
    line-height: 1.4;
}

@keyframes pulse {
    0% { opacity: 0.8; }
    50% { opacity: 1; border-color: #7dd3fc; }
    100% { opacity: 0.8; }
}

/* ── Output Containers ── */
.section-divider {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #64748b;
    margin: 4rem 0 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.section-divider::after { content: ''; flex: 1; height: 1px; background: #1e293b; }

.output-container {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 2.2rem;
    margin-bottom: 1.5rem;
    line-height: 1.75;
}
.report-box { border-left: 4px solid #38bdf8; }
.critic-box { border-left: 4px solid #f59e0b; background: #111422; border-color: #f59e0b; }

.raw-scroll-box {
    background: #0b0f19;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #94a3b8;
    max-height: 200px;
    overflow-y: auto;
    white-space: pre-wrap;
}

/* ── Components Fixes ── */
.stDownloadButton > button {
    background: transparent !important;
    color: #38bdf8 !important;
    border: 1px solid #38bdf8 !important;
    font-size: 0.8rem !important;
    padding: 0.5rem 1.2rem !important;
    border-radius: 6px !important;
    box-shadow: none !important;
}
.stDownloadButton > button:hover {
    background: rgba(56, 189, 248, 0.08) !important;
}

.footer {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.05em;
    color: #475569;
    text-align: center;
    margin-top: 6rem;
    padding-top: 2rem;
    border-top: 1px solid #1e293b;
}
</style>
""", unsafe_allow_html=True)

# ── Topbar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-logo">◈ nexus.<span>research</span></div>
    <div class="topbar-tag">Pipeline v1.0</div>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False

# ── Hero Block ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-label">Autonomous Knowledge Assembly</div>
    <h1>Deep research, on demand.</h1>
    <p class="hero-desc">
        Four localized specialized agents run asynchronously in a sequential layout pipeline to crawl, aggregate, compose, and critique rigorous research outputs.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Input Area ────────────────────────────────────────────────────────────────
topic = st.text_input(
    "Research Target & Constraints",
    placeholder="e.g., Practical constraints of room temperature superconductors in 2026",
    key="topic_input",
)

# Inline subtle suggestions tags
st.markdown("""
<div style="display:flex; gap:0.5rem; align-items:center; margin-top:-0.5rem; margin-bottom:1.5rem; opacity:0.6;">
    <span style="font-size:0.75rem; color:#64748b;">Suggestions:</span>
    <span style="font-size:0.72rem; background:#1e293b; padding:0.1rem 0.4rem; border-radius:4px; color:#94a3b8;">Neuromorphic Computing</span>
    <span style="font-size:0.72rem; background:#1e293b; padding:0.1rem 0.4rem; border-radius:4px; color:#94a3b8;">Solid State Batteries</span>
</div>
""", unsafe_allow_html=True)

run_btn = st.button("Initialize Pipeline Process", use_container_width=True)

# ── Pipeline Visualization Grid ───────────────────────────────────────────────
st.markdown('<div class="section-divider">Pipeline Status</div>', unsafe_allow_html=True)

r = st.session_state.results

def get_card_status_class(step_key):
    steps = ["search", "reader", "writer", "critic"]
    if step_key in r:
        return "card-done"
    if st.session_state.running:
        for k in steps:
            if k not in r:
                return "card-running" if k == step_key else "card-waiting"
    return "card-waiting"

pipeline_steps = [
    ("01", "search", "Search Agent", "Mining recent indexing data & nodes"),
    ("02", "reader", "Reader Agent", "Parsing unstructured markup content"),
    ("03", "writer", "Writer Chain", "Structuring comprehensive report synthesis"),
    ("04", "critic", "Critic Chain", "Auditing verification & technical alignment"),
]

# Generate grid cards
grid_html = '<div class="pipeline-container">'
for num, key, name, sub in pipeline_steps:
    status_cls = get_card_status_class(key)
    grid_html += f"""
    <div class="pipeline-card {status_cls}">
        <div class="card-header">
            <span class="card-title">{name}</span>
            <span class="card-num">// {num}</span>
        </div>
        <div class="card-desc">{sub}</div>
    </div>
    """
grid_html += '</div>'
st.markdown(grid_html, unsafe_allow_html=True)

# ── Pipeline Trigger Execution ────────────────────────────────────────────────
if run_btn:
    if not st.session_state.topic_input.strip():
        st.warning("Please define a structured query before initializing operations.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    with st.spinner("Quarrying indices..."):
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)

    with st.spinner("Scraping DOM targets..."):
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

    with st.spinner("Compiling contextual drafts..."):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)

    with st.spinner("Executing structural review..."):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()

# ── Dynamic Results Output Rendering ──────────────────────────────────────────
if r:
    st.markdown('<div class="section-divider">Assembled Deliverables</div>', unsafe_allow_html=True)

    # Report Component
    if "writer" in r:
        st.markdown('<div class="output-container report-box">', unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.download_button(
            label="Download Research Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    # Critic Review Component
    if "critic" in r:
        st.markdown('<div style="margin-top: 2.5rem;"></div>', unsafe_allow_html=True)
        st.caption("Pipeline Assessment & Alignment Report")
        st.markdown('<div class="output-container critic-box">', unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown('</div>', unsafe_allow_html=True)

    # Debug logs grouped neatly at the bottom inside standard expanders
    st.markdown('<div style="margin-top: 3rem;"></div>', unsafe_allow_html=True)
    if "search" in r:
        with st.expander("Inspect Raw Search Agent Node Artifacts"):
            st.markdown(f'<div class="raw-scroll-box">{r["search"]}</div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("Inspect Raw Scraping Engine Buffer Document"):
            st.markdown(f'<div class="raw-scroll-box">{r["reader"]}</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Nexus Research System Platform • Fueled by LangChain Multi-Agent Matrix
</div>
""", unsafe_allow_html=True)