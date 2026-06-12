"""
ArticleIQ — AI Research Intelligence Platform
Premium multilingual news intelligence powered by Groq + Llama 3.3 70B.
"""

import streamlit as st
import os
from datetime import datetime

# ── Load secrets / env ────────────────────────────────────────────────────────
try:
    groq_key = st.secrets["GROQ_API_KEY"]
    os.environ["GROQ_API_KEY"] = groq_key
except Exception:
    pass  # Fall through to dotenv or existing env

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Utils imports ─────────────────────────────────────────────────────────────
from utils.summarizer import summarize_article
from utils.ai_insights import generate_article_insights, generate_why_this_matters
from utils.accuracy_validator import validate_summary_accuracy
from utils.credibility import get_credibility_score
from utils.fetcher import fetch_article, fetch_multiple_articles
from utils.multi_article import analyze_multiple_articles
from utils.pdf_export import generate_pdf_report
from utils.rss_monitor import fetch_topic_news

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ArticleIQ — AI Research Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global reset ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid #334155;
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label { color: #94a3b8 !important; font-size: 0.78rem !important; }

    /* ── Header / hero ── */
    .aiq-hero {
        background: linear-gradient(135deg, #0f172a 0%, #164e35 50%, #0f172a 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.8rem;
        border: 1px solid #1e3a2b;
        position: relative;
        overflow: hidden;
    }
    .aiq-hero::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 220px; height: 220px;
        background: radial-gradient(circle, #16a34a22, transparent 70%);
        border-radius: 50%;
    }
    .aiq-brand { font-size: 2.2rem; font-weight: 800; color: #16a34a; letter-spacing: -0.5px; margin: 0; }
    .aiq-tagline { font-size: 0.9rem; color: #94a3b8; margin: 0.2rem 0 0; font-weight: 400; }
    .aiq-badge {
        display: inline-block;
        background: #16a34a22;
        border: 1px solid #16a34a55;
        color: #4ade80;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        margin-top: 0.8rem;
        letter-spacing: 0.5px;
    }

    /* ── Glass cards ── */
    .glass-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(8px);
    }
    .glass-card-green {
        background: linear-gradient(135deg, #052e1622 0%, #16a34a11 100%);
        border: 1px solid #16a34a33;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
    }

    /* ── Section labels ── */
    .section-label {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 1.8px;
        color: #16a34a;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
        display: block;
    }
    .section-headline {
        font-size: 1.45rem;
        font-weight: 700;
        color: #f1f5f9;
        line-height: 1.4;
        margin: 0.3rem 0 0.8rem;
    }

    /* ── Insight chips ── */
    .insight-grid { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.4rem; }
    .insight-chip {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 0.5rem 0.9rem;
        min-width: 110px;
    }
    .insight-chip-label { font-size: 0.65rem; color: #64748b; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; }
    .insight-chip-value { font-size: 0.95rem; color: #e2e8f0; font-weight: 600; margin-top: 2px; }

    /* ── Score rings ── */
    .score-block {
        display: flex; align-items: center; gap: 1.2rem;
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1rem 1.4rem;
        margin-top: 0.5rem;
    }
    .score-ring {
        width: 64px; height: 64px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem; font-weight: 800; color: #fff;
        flex-shrink: 0;
    }
    .score-ring-green { background: conic-gradient(#16a34a var(--pct), #1e293b var(--pct)); }
    .score-meta { flex: 1; }
    .score-title { font-size: 0.8rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px; }
    .score-value { font-size: 1.6rem; font-weight: 800; color: #f1f5f9; line-height: 1.1; }
    .score-sub { font-size: 0.78rem; color: #64748b; margin-top: 2px; }

    /* ── Takeaway list ── */
    .takeaway-item {
        display: flex; align-items: flex-start; gap: 0.7rem;
        padding: 0.6rem 0;
        border-bottom: 1px solid #1e293b;
    }
    .takeaway-num {
        background: #16a34a;
        color: #fff;
        font-size: 0.72rem;
        font-weight: 700;
        width: 22px; height: 22px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
        margin-top: 1px;
    }
    .takeaway-text { font-size: 0.9rem; color: #cbd5e1; line-height: 1.5; }

    /* ── Source comparison table ── */
    .compare-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
    .compare-table th {
        background: #0f172a;
        color: #16a34a;
        padding: 0.6rem 0.9rem;
        text-align: left;
        font-size: 0.72rem;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        border-bottom: 2px solid #16a34a33;
    }
    .compare-table td {
        padding: 0.6rem 0.9rem;
        color: #cbd5e1;
        border-bottom: 1px solid #1e293b;
        vertical-align: top;
    }
    .compare-table tr:nth-child(even) td { background: #ffffff05; }

    /* ── Sentiment badge ── */
    .badge { display: inline-block; border-radius: 20px; font-size: 0.72rem; font-weight: 600; padding: 2px 10px; }
    .badge-pos { background: #16a34a22; color: #4ade80; border: 1px solid #16a34a44; }
    .badge-neg { background: #dc262622; color: #f87171; border: 1px solid #dc262644; }
    .badge-neu { background: #64748b22; color: #94a3b8; border: 1px solid #64748b44; }
    .badge-high { background: #16a34a22; color: #4ade80; border: 1px solid #16a34a44; }
    .badge-med  { background: #d9770622; color: #fb923c; border: 1px solid #d9770644; }
    .badge-low  { background: #dc262622; color: #f87171; border: 1px solid #dc262644; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #0f172a;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #64748b;
        font-weight: 500;
        font-size: 0.85rem;
        padding: 0.4rem 0.9rem;
    }
    .stTabs [aria-selected="true"] {
        background: #16a34a !important;
        color: #fff !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #16a34a, #15803d);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.875rem;
        padding: 0.5rem 1.4rem;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #15803d, #166534);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px #16a34a44;
    }

    /* ── Inputs ── */
    .stTextArea textarea, .stTextInput input {
        background: #0f172a !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
        font-size: 0.875rem !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #16a34a !important;
        box-shadow: 0 0 0 2px #16a34a33 !important;
    }

    /* ── Progress / spinner ── */
    .stSpinner > div { border-top-color: #16a34a !important; }

    /* ── Footer ── */
    .aiq-footer {
        text-align: center;
        padding: 1.5rem 0 0.5rem;
        color: #334155;
        font-size: 0.75rem;
        border-top: 1px solid #1e293b;
        margin-top: 2rem;
    }
    .aiq-footer a { color: #16a34a; text-decoration: none; }

    /* ── Why this matters bullets ── */
    .wtm-item { display: flex; gap: 0.6rem; align-items: flex-start; margin: 0.4rem 0; }
    .wtm-dot { width: 8px; height: 8px; border-radius: 50%; background: #16a34a; margin-top: 6px; flex-shrink: 0; }
    .wtm-text { color: #cbd5e1; font-size: 0.88rem; line-height: 1.55; }

    /* ── RSS feed card ── */
    .feed-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.6rem;
        transition: border-color 0.2s;
    }
    .feed-card:hover { border-color: #16a34a44; }
    .feed-title { font-size: 0.92rem; font-weight: 600; color: #e2e8f0; }
    .feed-meta { font-size: 0.75rem; color: #475569; margin-top: 0.2rem; }

    /* ── Dark override for Streamlit elements ── */
    .stMarkdown p { color: #cbd5e1; }
    h1, h2, h3, h4 { color: #f1f5f9 !important; }
    .stExpander { background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "history": [],
        "current_summary": None,
        "current_article": None,
        "current_url": "",
        "total_summaries": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Helpers ───────────────────────────────────────────────────────────────────
def score_color(score: int) -> str:
    if score >= 80:
        return "#16a34a"
    elif score >= 60:
        return "#f59e0b"
    return "#ef4444"


def sentiment_badge(s: str) -> str:
    s_lower = s.lower() if s else ""
    if "positive" in s_lower:
        return f'<span class="badge badge-pos">{s}</span>'
    elif "negative" in s_lower:
        return f'<span class="badge badge-neg">{s}</span>'
    return f'<span class="badge badge-neu">{s}</span>'


def tier_badge(tier: str) -> str:
    tier_lower = tier.lower() if tier else ""
    if "high" in tier_lower:
        return f'<span class="badge badge-high">{tier}</span>'
    elif "medium" in tier_lower:
        return f'<span class="badge badge-med">{tier}</span>'
    return f'<span class="badge badge-low">{tier}</span>'


def render_score_block(score: int, label: str, sub: str = ""):
    color = score_color(score)
    st.markdown(f"""
    <div class="score-block">
        <div style="width:64px;height:64px;border-radius:50%;background:conic-gradient(
            {color} {score * 3.6}deg, #1e293b {score * 3.6}deg);
            display:flex;align-items:center;justify-content:center;flex-shrink:0;">
            <div style="width:48px;height:48px;border-radius:50%;background:#0f172a;
                display:flex;align-items:center;justify-content:center;
                font-size:0.9rem;font-weight:800;color:{color};">
                {score}
            </div>
        </div>
        <div class="score-meta">
            <div class="score-title">{label}</div>
            <div class="score-value">{score}<span style="font-size:1rem;color:#475569;">/100</span></div>
            {"<div class='score-sub'>" + sub + "</div>" if sub else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_takeaways(takeaways: list):
    html = ""
    for i, t in enumerate(takeaways, 1):
        html += f"""
        <div class="takeaway-item">
            <div class="takeaway-num">{i}</div>
            <div class="takeaway-text">{t}</div>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_insight_chips(insights: dict):
    st.markdown(f"""
    <div class="insight-grid">
        <div class="insight-chip">
            <div class="insight-chip-label">Tone</div>
            <div class="insight-chip-value">{insights.get('tone','—')}</div>
        </div>
        <div class="insight-chip">
            <div class="insight-chip-label">Sentiment</div>
            <div class="insight-chip-value">{insights.get('sentiment','—')}</div>
        </div>
        <div class="insight-chip">
            <div class="insight-chip-label">Complexity</div>
            <div class="insight-chip-value">{insights.get('complexity','—')}</div>
        </div>
        <div class="insight-chip" style="min-width:180px;">
            <div class="insight-chip-label">Audience</div>
            <div class="insight-chip-value">{insights.get('audience','—')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding:1rem 0 0.5rem;">
            <div style="font-size:1.3rem;font-weight:800;color:#16a34a;">ArticleIQ</div>
            <div style="font-size:0.72rem;color:#475569;margin-top:2px;">AI Research Intelligence</div>
        </div>
        <hr style="border-color:#1e293b;margin:0.6rem 0 1rem;">
        """, unsafe_allow_html=True)

        mode = st.selectbox(
            "Summary Mode",
            ["Quick", "Standard", "Detailed"],
            index=1,
            help="Quick = fast & brief | Standard = balanced | Detailed = comprehensive"
        )

        language = st.selectbox(
            "Output Language",
            ["English", "Telugu", "Hindi", "Tamil", "French"],
            index=0,
        )

        st.markdown("<hr style='border-color:#1e293b;margin:1rem 0;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.72rem;color:#475569;font-weight:600;letter-spacing:1px;text-transform:uppercase;'>Options</div>", unsafe_allow_html=True)
        run_accuracy = st.checkbox("AI Accuracy Validation", value=True)
        run_credibility = st.checkbox("Source Credibility Score", value=True)
        run_why_matters = st.checkbox("Why This Matters", value=True)

        st.markdown("<hr style='border-color:#1e293b;margin:1rem 0;'>", unsafe_allow_html=True)

        # History
        if st.session_state.history:
            st.markdown("<div style='font-size:0.72rem;color:#475569;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:0.5rem;'>Recent Summaries</div>", unsafe_allow_html=True)
            for i, item in enumerate(reversed(st.session_state.history[-5:])):
                headline_short = item["headline"][:42] + "…" if len(item["headline"]) > 42 else item["headline"]
                st.markdown(f"""
                <div style="font-size:0.78rem;color:#94a3b8;padding:0.3rem 0;
                    border-bottom:1px solid #1e293b;cursor:pointer;">
                    {headline_short}
                </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style='margin-top:1.5rem;font-size:0.72rem;color:#334155;text-align:center;'>
            {st.session_state.total_summaries} articles analyzed
        </div>""", unsafe_allow_html=True)

    return mode, language, run_accuracy, run_credibility, run_why_matters


# ── Tab 1: Single Article ─────────────────────────────────────────────────────
def tab_single_article(mode: str, language: str, run_accuracy: bool, run_credibility: bool, run_why_matters: bool):
    st.markdown('<span class="section-label">Input</span>', unsafe_allow_html=True)

    input_method = st.radio("Source", ["Paste URL", "Paste Article Text"], horizontal=True, label_visibility="collapsed")

    url = ""
    article_text = ""

    if input_method == "Paste URL":
        url = st.text_input("Article URL", placeholder="https://www.reuters.com/article/...", label_visibility="collapsed")
    else:
        article_text = st.text_area("Article Text", placeholder="Paste the full article text here…", height=200, label_visibility="collapsed")

    col1, col2 = st.columns([2, 8])
    with col1:
        analyze_btn = st.button("Analyze Article →", use_container_width=True)

    if not analyze_btn:
        return

    # Input validation
    if input_method == "Paste URL" and not url.strip():
        st.warning("Please enter a URL to analyze.")
        return
    if input_method == "Paste Article Text" and len(article_text.strip()) < 100:
        st.warning("Please paste at least 100 characters of article text.")
        return

    # Fetch if URL
    if input_method == "Paste URL":
        with st.spinner("Fetching article…"):
            result = fetch_article(url.strip())
        if not result["success"]:
            st.error(f"Could not fetch article: {result['error']}")
            return
        article_text = result["content"]
        st.session_state.current_url = url.strip()
        st.success(f"✓ Fetched {result['word_count']:,} words from {result['title'] or url}")
    else:
        st.session_state.current_url = ""

    st.session_state.current_article = article_text

    # ── Run pipeline ─────────────────────────────────────────────
    progress = st.progress(0, text="Starting analysis…")

    with st.spinner("Generating summary…"):
        summary = summarize_article(article_text, mode=mode, language=language)
        progress.progress(25, text="Summary complete…")

    with st.spinner("Analyzing insights…"):
        insights = generate_article_insights(article_text)
        progress.progress(45, text="Insights ready…")

    accuracy_data = None
    if run_accuracy:
        with st.spinner("Validating accuracy…"):
            full_summary_text = f"{summary['headline']}\n{summary['paragraph']}\n" + "\n".join(summary["takeaways"])
            accuracy_data = validate_summary_accuracy(article_text, full_summary_text)
            progress.progress(65, text="Accuracy validated…")

    credibility_data = None
    if run_credibility and st.session_state.current_url:
        with st.spinner("Scoring source credibility…"):
            credibility_data = get_credibility_score(st.session_state.current_url)
            progress.progress(80, text="Credibility assessed…")

    why_matters_text = None
    if run_why_matters:
        with st.spinner("Generating impact analysis…"):
            why_matters_text = generate_why_this_matters(article_text, summary["paragraph"])
            progress.progress(95, text="Almost done…")

    progress.progress(100, text="Analysis complete!")
    progress.empty()

    # Store history
    st.session_state.history.append({
        "headline": summary["headline"],
        "timestamp": datetime.now().strftime("%H:%M"),
        "mode": mode,
        "language": language,
    })
    st.session_state.current_summary = summary
    st.session_state.total_summaries += 1

    # ── Render Results ────────────────────────────────────────────
    st.markdown("---")
    _render_single_results(
        summary, insights, accuracy_data, credibility_data,
        why_matters_text, article_text, mode, language, url
    )


def _render_single_results(summary, insights, accuracy_data, credibility_data,
                            why_matters_text, article_text, mode, language, url):
    # ── Headline card ─────────────────────────────────────────────
    st.markdown(f"""
    <div class="glass-card-green">
        <span class="section-label">Headline</span>
        <div class="section-headline">{summary['headline']}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column layout ─────────────────────────────────────────
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        # Summary paragraph
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Summary</span>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#cbd5e1;line-height:1.7;font-size:0.92rem;">{summary["paragraph"]}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Key takeaways
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Key Takeaways</span>', unsafe_allow_html=True)
        render_takeaways(summary["takeaways"])
        st.markdown('</div>', unsafe_allow_html=True)

        # Why this matters
        if why_matters_text:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<span class="section-label">Why This Matters</span>', unsafe_allow_html=True)
            import re
            lines = why_matters_text.strip().split("\n")
            html = ""
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Convert **bold** markdown
                line = re.sub(r"\*\*(.+?)\*\*", r"<strong style='color:#4ade80;'>\1</strong>", line)
                if line.startswith("- ") or line.startswith("• "):
                    line = line.lstrip("- •").strip()
                    html += f'<div class="wtm-item"><div class="wtm-dot"></div><div class="wtm-text">{line}</div></div>'
                else:
                    html += f'<div class="wtm-text" style="margin-bottom:0.3rem;">{line}</div>'
            st.markdown(html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        # AI Insights
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">AI Insights</span>', unsafe_allow_html=True)
        render_insight_chips(insights)
        st.markdown('</div>', unsafe_allow_html=True)

        # Credibility
        if credibility_data:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<span class="section-label">Source Credibility</span>', unsafe_allow_html=True)
            render_score_block(
                credibility_data["score"],
                "Source Reliability",
                f"{credibility_data['label']} · {credibility_data['domain']}"
            )
            st.markdown(f"""
            <div style="margin-top:0.6rem;">
                {tier_badge(credibility_data['tier'])}
                <p style="color:#64748b;font-size:0.8rem;margin-top:0.4rem;">{credibility_data['explanation']}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Accuracy
        if accuracy_data:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<span class="section-label">AI Accuracy Validation</span>', unsafe_allow_html=True)
            render_score_block(
                accuracy_data["score"],
                "Factual Accuracy",
                f"Confidence: {accuracy_data['confidence']} · Hallucination Risk: {accuracy_data['hallucination_risk']}"
            )
            if accuracy_data.get("explanation"):
                st.markdown(f'<p style="color:#64748b;font-size:0.8rem;margin-top:0.5rem;">{accuracy_data["explanation"]}</p>', unsafe_allow_html=True)
            if accuracy_data.get("missing_info"):
                st.markdown('<span style="font-size:0.72rem;color:#475569;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;">Missing Info</span>', unsafe_allow_html=True)
                for item in accuracy_data["missing_info"]:
                    st.markdown(f'<div class="wtm-item"><div class="wtm-dot" style="background:#f59e0b;"></div><div class="wtm-text">{item}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # PDF Export
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Export</span>', unsafe_allow_html=True)
        try:
            pdf_bytes = generate_pdf_report(
                headline=summary["headline"],
                paragraph=summary["paragraph"],
                takeaways=summary["takeaways"],
                insights=insights,
                accuracy=accuracy_data,
                credibility=credibility_data,
                why_matters=why_matters_text,
                source_url=url or "",
                language=language,
                mode=mode,
            )
            st.download_button(
                label="⬇ Download PDF Report",
                data=pdf_bytes,
                file_name=f"articleiq_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.caption(f"PDF generation error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)


# ── Tab 2: Multi-Article Intelligence ─────────────────────────────────────────
def tab_multi_article(mode: str, language: str):
    st.markdown("""
    <div class="glass-card-green" style="margin-bottom:1rem;">
        <span class="section-label">Multi-Article Intelligence Mode</span>
        <div style="color:#94a3b8;font-size:0.88rem;margin-top:0.3rem;">
            Compare 2–5 sources on the same story. Detect agreements, contradictions, and
            coverage gaps — then get a unified intelligence brief.
        </div>
    </div>
    """, unsafe_allow_html=True)

    num_articles = st.slider("Number of articles to compare", min_value=2, max_value=5, value=2)

    urls = []
    for i in range(num_articles):
        u = st.text_input(
            f"Source {i + 1} URL",
            placeholder=f"https://source{i+1}.com/article…",
            key=f"multi_url_{i}"
        )
        urls.append(u.strip())

    col1, _ = st.columns([2, 8])
    with col1:
        compare_btn = st.button("Run Intelligence Analysis →", use_container_width=True)

    if not compare_btn:
        return

    valid_urls = [u for u in urls if u.startswith("http")]
    if len(valid_urls) < 2:
        st.warning("Please enter at least 2 valid URLs (starting with http/https).")
        return

    # Fetch all articles
    with st.spinner(f"Fetching {len(valid_urls)} articles…"):
        fetch_results = fetch_multiple_articles(valid_urls)

    failed = [r for r in fetch_results if not r["success"]]
    successful = [r for r in fetch_results if r["success"]]

    if failed:
        for f in failed:
            st.warning(f"⚠ Could not fetch: {f['url'][:60]}… — {f['error']}")

    if len(successful) < 2:
        st.error("Need at least 2 successfully fetched articles to compare.")
        return

    articles_for_analysis = [
        {"url": r["url"], "content": r["content"], "title": r["title"]}
        for r in successful
    ]

    # Run multi-article intelligence
    with st.spinner("Running cross-source intelligence analysis… (this may take 30–60 seconds)"):
        analysis = analyze_multiple_articles(articles_for_analysis)

    if analysis.get("error") and not analysis.get("unified_summary"):
        st.error(f"Analysis failed: {analysis['error']}")
        return

    # ── Render multi-article results ──────────────────────────────
    st.markdown("---")

    # What Actually Happened — flagship card
    st.markdown(f"""
    <div class="glass-card-green">
        <span class="section-label">What Actually Happened</span>
        <div class="section-headline" style="font-size:1.15rem;">{analysis.get('what_actually_happened', 'See unified summary below.')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs for sections
    t_unified, t_agree, t_contra, t_sentiment, t_sources = st.tabs([
        "Unified Summary", "Agreements", "Contradictions", "Sentiment", "Source Breakdown"
    ])

    with t_unified:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#cbd5e1;line-height:1.75;font-size:0.92rem;">{analysis.get("unified_summary", "")}</p>', unsafe_allow_html=True)

        # Missing coverage
        missing = analysis.get("missing_coverage", [])
        if missing:
            st.markdown('<span class="section-label" style="margin-top:1rem;display:block;">Coverage Gaps Detected</span>', unsafe_allow_html=True)
            for item in missing:
                st.markdown(f'<div class="wtm-item"><div class="wtm-dot" style="background:#f59e0b;"></div><div class="wtm-text">{item}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with t_agree:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Points of Agreement</span>', unsafe_allow_html=True)
        agreements = analysis.get("agreement_points", [])
        if agreements:
            for i, ag in enumerate(agreements, 1):
                st.markdown(f"""
                <div class="takeaway-item">
                    <div class="takeaway-num" style="background:#16a34a;">✓</div>
                    <div class="takeaway-text">{ag}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#64748b;">No clear agreements detected across sources.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Viewpoint differences
        vp_diffs = analysis.get("viewpoint_differences", [])
        if vp_diffs:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<span class="section-label">Framing Differences</span>', unsafe_allow_html=True)
            for item in vp_diffs:
                st.markdown(f'<div class="wtm-item"><div class="wtm-dot" style="background:#8b5cf6;"></div><div class="wtm-text">{item}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with t_contra:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Contradiction Analysis</span>', unsafe_allow_html=True)
        contradictions = analysis.get("contradictions", [])
        if contradictions:
            for c in contradictions:
                st.markdown(f"""
                <div style="background:#0f172a;border:1px solid #dc262633;border-radius:10px;
                    padding:0.9rem 1.1rem;margin-bottom:0.7rem;">
                    <div style="font-size:0.8rem;font-weight:700;color:#f87171;margin-bottom:0.4rem;">
                        ⚡ {c.get('claim','Disputed claim')}
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;margin-top:0.4rem;">
                        <div style="font-size:0.82rem;color:#94a3b8;">
                            <span style="color:#64748b;font-size:0.7rem;font-weight:600;text-transform:uppercase;">Version A</span><br>
                            {c.get('source_a','—')}
                        </div>
                        <div style="font-size:0.82rem;color:#94a3b8;">
                            <span style="color:#64748b;font-size:0.7rem;font-weight:600;text-transform:uppercase;">Version B</span><br>
                            {c.get('source_b','—')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#64748b;">No direct contradictions found. Sources are broadly consistent.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with t_sentiment:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Source Sentiment & Bias</span>', unsafe_allow_html=True)
        sentiments = analysis.get("sentiment_by_source", [])
        if sentiments:
            html = """<table class="compare-table">
                <thead><tr>
                    <th>Source</th><th>Sentiment</th><th>Political Lean</th>
                </tr></thead><tbody>"""
            for s in sentiments:
                sent_badge = sentiment_badge(s.get("sentiment", "—"))
                html += f"""<tr>
                    <td style="font-weight:600;">{s.get('source','—')}</td>
                    <td>{sent_badge}</td>
                    <td style="color:#94a3b8;">{s.get('bias_lean','Unknown')}</td>
                </tr>"""
            html += "</tbody></table>"
            st.markdown(html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with t_sources:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Per-Source Breakdown</span>', unsafe_allow_html=True)
        comparisons = analysis.get("source_comparison", [])
        if comparisons:
            html = """<table class="compare-table">
                <thead><tr>
                    <th>Source</th><th>Coverage Focus</th><th>Tone</th><th>Key Claims</th>
                </tr></thead><tbody>"""
            for s in comparisons:
                claims = "; ".join(s.get("key_claims", []))
                html += f"""<tr>
                    <td style="font-weight:600;">{s.get('source','—')}</td>
                    <td>{s.get('coverage_focus','—')}</td>
                    <td style="color:#94a3b8;">{s.get('tone','—')}</td>
                    <td style="color:#64748b;font-size:0.8rem;">{claims}</td>
                </tr>"""
            html += "</tbody></table>"
            st.markdown(html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Individual article summaries (collapsible)
    st.markdown("---")
    st.markdown('<span class="section-label">Individual Summaries</span>', unsafe_allow_html=True)
    for i, art in enumerate(successful, 1):
        with st.expander(f"Source {i}: {art.get('title','Article')[:60]}"):
            with st.spinner(f"Summarizing Source {i}…"):
                s = summarize_article(art["content"], mode=mode, language=language)
            st.markdown(f"**{s['headline']}**")
            st.markdown(f'<p style="color:#94a3b8;font-size:0.88rem;">{s["paragraph"]}</p>', unsafe_allow_html=True)
            render_takeaways(s["takeaways"])


# ── Tab 3: Topic Intelligence Feed ───────────────────────────────────────────
def tab_topic_feed():
    st.markdown("""
    <div class="glass-card-green" style="margin-bottom:1rem;">
        <span class="section-label">Topic Intelligence Feed</span>
        <div style="color:#94a3b8;font-size:0.88rem;margin-top:0.3rem;">
            Enter any topic to get a live feed of the latest news, auto-curated and ready to summarize.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([4, 2])
    with col1:
        topic = st.text_input("Topic", placeholder="e.g. AI, Tesla, RBI policy, Startups, Quantum Computing…", label_visibility="collapsed")
    with col2:
        max_items = st.selectbox("Articles", [3, 5, 8, 10], index=1, label_visibility="collapsed")

    fetch_btn = st.button("Fetch Latest News →", use_container_width=False)

    if not fetch_btn or not topic.strip():
        return

    with st.spinner(f"Fetching latest news on '{topic}'…"):
        articles = fetch_topic_news(topic.strip(), max_articles=max_items)

    if not articles:
        st.warning("No articles found. Try a different topic.")
        return

    st.markdown(f'<span class="section-label">Latest: {topic}</span>', unsafe_allow_html=True)

    for art in articles:
        if art.get("error") and not art.get("title"):
            st.error(f"Feed error: {art['error']}")
            continue

        col_main, col_action = st.columns([6, 1])
        with col_main:
            st.markdown(f"""
            <div class="feed-card">
                <div class="feed-title">{art.get('title','No title')}</div>
                <div class="feed-meta">{art.get('source','Unknown')} · {art.get('published','')}</div>
                {f"<div style='color:#475569;font-size:0.78rem;margin-top:0.3rem;'>{art.get('snippet','')}</div>" if art.get('snippet') else ""}
            </div>
            """, unsafe_allow_html=True)
        with col_action:
            if art.get("url"):
                st.markdown(f'<a href="{art["url"]}" target="_blank" style="font-size:0.75rem;color:#16a34a;text-decoration:none;">Open ↗</a>', unsafe_allow_html=True)


# ── Tab 4: Dashboard ─────────────────────────────────────────────────────────
def tab_dashboard():
    total = st.session_state.total_summaries
    history = st.session_state.history

    st.markdown("""
    <div class="glass-card-green">
        <span class="section-label">Personal Dashboard</span>
        <div style="color:#94a3b8;font-size:0.88rem;margin-top:0.2rem;">Your ArticleIQ research session at a glance.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div style="font-size:2.5rem;font-weight:800;color:#16a34a;">{total}</div>
            <div style="color:#64748b;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;">Articles Analyzed</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        modes = [h["mode"] for h in history]
        top_mode = max(set(modes), key=modes.count) if modes else "—"
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div style="font-size:2.5rem;font-weight:800;color:#16a34a;">{top_mode}</div>
            <div style="color:#64748b;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;">Preferred Mode</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        langs = [h["language"] for h in history]
        top_lang = max(set(langs), key=langs.count) if langs else "—"
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div style="font-size:2.5rem;font-weight:800;color:#16a34a;">{top_lang}</div>
            <div style="color:#64748b;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;">Top Language</div>
        </div>""", unsafe_allow_html=True)

    if history:
        st.markdown('<span class="section-label" style="margin-top:1.5rem;display:block;">Recent Summaries</span>', unsafe_allow_html=True)
        for item in reversed(history[-10:]):
            st.markdown(f"""
            <div class="feed-card">
                <div class="feed-title">{item['headline']}</div>
                <div class="feed-meta">{item['timestamp']} · {item['mode']} · {item['language']}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#475569;text-align:center;padding:2rem;">Analyze your first article to see your dashboard.</p>', unsafe_allow_html=True)


# ── Main app ──────────────────────────────────────────────────────────────────
def main():
    inject_css()
    init_session()

    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        st.error("⚠ GROQ_API_KEY not configured. Add it to Streamlit secrets or your .env file.")
        st.info("Set it in `.streamlit/secrets.toml` as:\n\n```toml\nGROQ_API_KEY = 'your-key-here'\n```")
        st.stop()

    # Sidebar controls
    mode, language, run_accuracy, run_credibility, run_why_matters = render_sidebar()

    # Hero header
    st.markdown("""
    <div class="aiq-hero">
        <div class="aiq-brand">ArticleIQ</div>
        <div class="aiq-tagline">AI Research Intelligence Platform — Powered by Llama 3.3 70B</div>
        <div class="aiq-badge">🔬 RESEARCH GRADE · MULTILINGUAL · MULTI-SOURCE</div>
    </div>
    """, unsafe_allow_html=True)

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Single Article",
        "⚡ Multi-Source Intelligence",
        "📡 Topic Feed",
        "📊 Dashboard",
    ])

    with tab1:
        tab_single_article(mode, language, run_accuracy, run_credibility, run_why_matters)

    with tab2:
        tab_multi_article(mode, language)

    with tab3:
        tab_topic_feed()

    with tab4:
        tab_dashboard()

    # Footer
    st.markdown("""
    <div class="aiq-footer">
        ArticleIQ · AI Research Intelligence Platform ·
        Powered by <a href="https://groq.com" target="_blank">Groq</a> &
        <a href="https://www.llama.com" target="_blank">Llama 3.3 70B</a> ·
        Built for research and informational purposes only.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()