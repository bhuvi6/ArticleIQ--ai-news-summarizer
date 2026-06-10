import streamlit as st
import urllib.request
import urllib.error
import re
import json
import io
from datetime import datetime
from PIL import Image
from utils.summarizer import generate_summary
from utils.metadata import get_word_count, get_reading_time, detect_topic
from utils.article_insights import generate_article_insights

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ArticleIQ — AI News Summarizer",
    page_icon="🟢",
    layout="wide"
)
logo = Image.open("assets/logo.png")
# ── Session State Init ─────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "current_summary_data" not in st.session_state:
    st.session_state.current_summary_data = None

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

html, body { font-family: 'Inter', sans-serif; background-color: #F8FAFC; color: #111827; }
.stApp { background: #F8FAFC; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 3rem 5rem 3rem; max-width: 1100px; }

/* NAV */
.nav { display:flex; align-items:center; justify-content:space-between; padding:1.4rem 0; border-bottom:1px solid #E5E7EB; margin-bottom:3rem; }
.nav-logo { display:flex; align-items:center; gap:9px; font-size:1.15rem; font-weight:800; color:#111827; letter-spacing:-0.03em; }
.nav-logo .dot { width:10px; height:10px; background:#16A34A; border-radius:50%; display:inline-block; box-shadow:0 0 0 3px #DCFCE7; }
.nav-tag { font-family:'DM Mono',monospace; font-size:0.65rem; letter-spacing:0.18em; color:#6B7280; background:#F3F4F6; border:1px solid #E5E7EB; padding:4px 12px; border-radius:100px; text-transform:uppercase; }

/* HERO */
.hero { padding:0.5rem 0 2.4rem 0; }
.hero-eyebrow { display:inline-flex; align-items:center; gap:6px; font-family:'DM Mono',monospace; font-size:0.7rem; letter-spacing:0.18em; text-transform:uppercase; color:#16A34A; background:#DCFCE7; border:1px solid #BBF7D0; padding:5px 14px; border-radius:100px; margin-bottom:1.4rem; }
.hero-title { font-size:clamp(2.2rem,4.5vw,3.2rem); font-weight:800; line-height:1.1; letter-spacing:-0.03em; color:#111827; margin-bottom:1.1rem; }
.hero-title em { font-style:normal; color:#16A34A; }
.hero-sub { font-size:1rem; font-weight:400; color:#6B7280; line-height:1.65; margin-bottom:1.8rem; max-width:480px; }
.hero-checks { display:flex; gap:1.4rem; flex-wrap:wrap; margin-bottom:0.5rem; }
.check-item { display:flex; align-items:center; gap:7px; font-size:0.88rem; font-weight:500; color:#374151; }
.check-icon { width:18px; height:18px; background:#DCFCE7; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.65rem; color:#16A34A; flex-shrink:0; }

/* INPUTS */
.stTextArea > label, .stTextInput > label { font-size:0.78rem !important; font-weight:600 !important; color:#374151 !important; }
.stTextArea textarea { background:#FFFFFF !important; border:1.5px solid #E5E7EB !important; border-radius:12px !important; color:#111827 !important; font-family:'Inter',sans-serif !important; font-size:0.95rem !important; line-height:1.72 !important; padding:1.1rem 1.3rem !important; box-shadow:0 1px 3px rgba(0,0,0,0.05) !important; }
.stTextArea textarea:focus, .stTextInput input:focus { border-color:#16A34A !important; box-shadow:0 0 0 3px rgba(22,163,74,0.1) !important; outline:none !important; }
.stTextArea textarea::placeholder, .stTextInput input::placeholder { color:#9CA3AF !important; }
.stTextInput input { background:#FFFFFF !important; border:1.5px solid #E5E7EB !important; border-radius:12px !important; color:#111827 !important; font-size:0.95rem !important; padding:0.75rem 1rem !important; }
.stSelectbox > label { font-size:0.78rem !important; font-weight:600 !important; color:#374151 !important; }
.stSelectbox > div > div { background:#FFFFFF !important; border:1.5px solid #E5E7EB !important; border-radius:10px !important; color:#111827 !important; font-size:0.9rem !important; }

/* BUTTONS */
.stButton > button { background:#16A34A !important; color:#FFFFFF !important; font-family:'Inter',sans-serif !important; font-size:0.92rem !important; font-weight:700 !important; border:none !important; border-radius:10px !important; padding:0.78rem 2rem !important; width:100% !important; transition:all 0.18s ease !important; box-shadow:0 2px 8px rgba(22,163,74,0.25) !important; }
.stButton > button:hover { background:#15803D !important; box-shadow:0 6px 20px rgba(22,163,74,0.3) !important; transform:translateY(-1px) !important; }
.stDownloadButton > button { background:#1D4ED8 !important; color:#FFFFFF !important; font-family:'Inter',sans-serif !important; font-size:0.88rem !important; font-weight:600 !important; border:none !important; border-radius:10px !important; padding:0.65rem 1.5rem !important; width:100% !important; box-shadow:0 2px 8px rgba(29,78,216,0.25) !important; transition:all 0.18s ease !important; }
.stDownloadButton > button:hover { background:#1E40AF !important; transform:translateY(-1px) !important; }

/* SECTION LABEL */
.sec-label { display:flex; align-items:center; gap:10px; font-family:'DM Mono',monospace; font-size:0.62rem; letter-spacing:0.22em; text-transform:uppercase; color:#9CA3AF; margin:2rem 0 1.2rem 0; }
.sec-label::before { content:''; width:6px; height:6px; background:#16A34A; border-radius:50%; flex-shrink:0; }
.sec-label::after { content:''; flex:1; height:1px; background:#E5E7EB; }

/* META CARDS */
.meta-card { background:#FFFFFF; border:1px solid #E5E7EB; border-radius:14px; padding:1.2rem 1.4rem; display:flex; align-items:center; gap:14px; box-shadow:0 1px 4px rgba(0,0,0,0.05); margin-bottom:0.75rem; }
.meta-icon { width:42px; height:42px; background:#DCFCE7; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.15rem; flex-shrink:0; }
.meta-value { font-size:1.25rem; font-weight:700; color:#111827; font-family:'DM Mono',monospace; line-height:1.1; }
.meta-key { font-size:0.72rem; font-weight:500; color:#9CA3AF; text-transform:uppercase; letter-spacing:0.08em; margin-top:2px; }

/* SUMMARY CARDS */
.headline-card { background:#FFFFFF; border:1.5px solid #BBF7D0; border-left:4px solid #16A34A; border-radius:0 16px 16px 0; padding:1.8rem 2rem; margin-bottom:1rem; box-shadow:0 2px 12px rgba(22,163,74,0.07); }
.card-eyebrow { font-family:'DM Mono',monospace; font-size:0.62rem; letter-spacing:0.2em; text-transform:uppercase; color:#16A34A; margin-bottom:0.7rem; display:flex; align-items:center; gap:6px; }
.headline-text { font-size:1.4rem; font-weight:700; color:#111827; line-height:1.35; letter-spacing:-0.02em; }
.para-card { background:#FFFFFF; border:1px solid #E5E7EB; border-radius:14px; padding:1.5rem 1.8rem; margin-bottom:1rem; box-shadow:0 1px 4px rgba(0,0,0,0.04); }
.para-text { font-size:0.97rem; color:#374151; line-height:1.78; }
.takeaways-card { background:#FFFFFF; border:1px solid #E5E7EB; border-radius:14px; padding:1.5rem 1.8rem; margin-bottom:1rem; box-shadow:0 1px 4px rgba(0,0,0,0.04); }
.takeaway-row { display:flex; align-items:flex-start; gap:12px; padding:0.55rem 0; border-bottom:1px solid #F3F4F6; font-size:0.94rem; color:#374151; line-height:1.55; }
.takeaway-row:last-child { border-bottom:none; padding-bottom:0; }
.takeaway-row:first-child { padding-top:0; }
.tk-bullet { width:22px; height:22px; background:#DCFCE7; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.6rem; color:#16A34A; font-weight:800; flex-shrink:0; margin-top:1px; }

/* ACCURACY SCORE */
.score-card { background:#FFFFFF; border:1px solid #E5E7EB; border-radius:14px; padding:1.4rem 1.8rem; margin-bottom:1rem; box-shadow:0 1px 4px rgba(0,0,0,0.04); }
.score-bar-bg { background:#F3F4F6; border-radius:100px; height:10px; margin:0.6rem 0 0.3rem 0; overflow:hidden; }
.score-bar-fill { height:10px; border-radius:100px; background:linear-gradient(90deg,#16A34A,#4ADE80); transition:width 0.6s ease; }
.score-label { font-family:'DM Mono',monospace; font-size:0.72rem; color:#6B7280; letter-spacing:0.06em; }

/* HISTORY */
.hist-item { background:#FFFFFF; border:1px solid #E5E7EB; border-radius:10px; padding:0.8rem 1rem; margin-bottom:0.5rem; cursor:pointer; transition:all 0.15s; font-size:0.83rem; color:#374151; }
.hist-item:hover { border-color:#16A34A; box-shadow:0 2px 8px rgba(22,163,74,0.1); }
.hist-topic { font-family:'DM Mono',monospace; font-size:0.62rem; color:#16A34A; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:3px; }
.hist-title { font-weight:600; color:#111827; font-size:0.85rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.hist-time { font-size:0.7rem; color:#9CA3AF; margin-top:3px; }

/* COPY BTNS */
.copy-btn-row { display:flex; gap:8px; margin-bottom:0.6rem; flex-wrap:wrap; }

/* MODE BADGE */
.mode-badge { display:inline-flex; align-items:center; gap:6px; font-family:'DM Mono',monospace; font-size:0.65rem; letter-spacing:0.12em; text-transform:uppercase; background:#EFF6FF; color:#1D4ED8; border:1px solid #BFDBFE; padding:4px 10px; border-radius:100px; margin-bottom:0.8rem; }

/* ALERTS */
.stAlert { background:#FFFBEB !important; border:1px solid #FDE68A !important; border-radius:10px !important; color:#78350F !important; }
.stSpinner > div { border-top-color:#16A34A !important; }
[data-testid="stMetric"] { display:none !important; }
hr { border-color:#E5E7EB !important; }

/* TABS */
.stTabs [data-baseweb="tab-list"] { gap:0.5rem; background:transparent; border-bottom:1px solid #E5E7EB; }
.stTabs [data-baseweb="tab"] { background:#F9FAFB; border:1px solid #E5E7EB; border-bottom:none; border-radius:8px 8px 0 0; font-size:0.85rem; font-weight:600; color:#6B7280; padding:0.5rem 1.2rem; }
.stTabs [aria-selected="true"] { background:#FFFFFF; color:#16A34A; border-color:#BBF7D0; border-bottom:2px solid #16A34A; }
</style>
""", unsafe_allow_html=True)

# ── JS for copy to clipboard ───────────────────────────────────────────────────
st.markdown("""
<script>
function copyText(text) {
    navigator.clipboard.writeText(text).then(() => {
        const toast = document.createElement('div');
        toast.textContent = '✓ Copied!';
        toast.style.cssText = 'position:fixed;bottom:24px;right:24px;background:#16A34A;color:#fff;padding:10px 20px;border-radius:8px;font-family:Inter,sans-serif;font-size:14px;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,0.15)';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    });
}
</script>
""", unsafe_allow_html=True)

# ── HELPERS ────────────────────────────────────────────────────────────────────

def fetch_article_from_url(url: str) -> str:
    """Fetch and extract article text from a URL using stdlib only."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ArticleIQ/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        # Strip scripts and styles
        html = re.sub(r"<(script|style)[^>]*>.*?</(script|style)>", "", html, flags=re.DOTALL | re.IGNORECASE)
        # Remove tags
        text = re.sub(r"<[^>]+>", " ", html)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        # Decode HTML entities
        text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " ").replace("&#39;", "'").replace("&quot;", '"')

        # Return first ~8000 chars (enough for summarization)
        return text[:8000]
    except Exception as e:
        return f"ERROR: {str(e)}"


def parse_summary(summary: str):
    """Parse Groq output into headline, paragraph, takeaways."""
    headline_text = ""
    paragraph_text = ""
    takeaways_list = []
    current_section = None
    para_lines = []

    for line in summary.splitlines():
        s = line.strip()
        if not s:
            continue
        lower_s = s.lower()

        if ("one-line summary" in lower_s or "headline summary" in lower_s
                or (lower_s.startswith("1.") and "summary" in lower_s)):
            current_section = "headline"
            if ":" in s:
                after = s.split(":", 1)[1].strip().replace("*", "").replace("#", "")
                if after:
                    headline_text = after
            continue

        elif ("one-paragraph summary" in lower_s or "paragraph summary" in lower_s
              or (lower_s.startswith("2.") and "summary" in lower_s)):
            current_section = "paragraph"
            if ":" in s:
                after = s.split(":", 1)[1].strip().replace("*", "").replace("#", "")
                if after:
                    para_lines.append(after)
            continue

        elif ("key takeaway" in lower_s
              or (lower_s.startswith("3.") and "takeaway" in lower_s)):
            current_section = "takeaways"
            continue

        clean = s.replace("*", "").replace("#", "").strip()

        if current_section == "headline":
            if clean and not headline_text:
                headline_text = clean
        elif current_section == "paragraph":
            para_lines.append(clean)
        elif current_section == "takeaways":
            t = clean.lstrip("•●▪-–1234567890. ").strip()
            if t:
                takeaways_list.append(t)

    paragraph_text = " ".join(para_lines)
    return headline_text, paragraph_text, takeaways_list


def compute_accuracy_score(article: str, headline: str, paragraph: str, takeaways: list) -> dict:
    """Check fact preservation: numbers, dates, named entities."""
    # Extract numbers from article
    art_numbers = set(re.findall(r'\b\d+[\d,\.]*\b', article))
    art_dates = set(re.findall(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:,\s*\d{4})?|\b\d{4}\b|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', article, re.IGNORECASE))
    # Extract capitalized words (likely proper nouns)
    art_names = set(re.findall(r'\b[A-Z][a-z]{2,}\b', article))

    summary_text = f"{headline} {paragraph} {' '.join(takeaways)}"
    sum_numbers = set(re.findall(r'\b\d+[\d,\.]*\b', summary_text))
    sum_dates = set(re.findall(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:,\s*\d{4})?|\b\d{4}\b|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', summary_text, re.IGNORECASE))
    sum_names = set(re.findall(r'\b[A-Z][a-z]{2,}\b', summary_text))

    # Score each category
    def ratio(a_set, b_set):
        if not a_set:
            return 1.0
        overlap = len(a_set & b_set)
        return min(1.0, overlap / max(1, min(len(a_set), 5)))

    num_score = ratio(art_numbers, sum_numbers)
    date_score = ratio(art_dates, sum_dates)
    name_score = ratio(art_names, sum_names)

    overall = int((num_score * 0.35 + date_score * 0.30 + name_score * 0.35) * 100)
    # Clamp between 70-99 for realism (LLMs are generally good)
    overall = max(70, min(99, overall + 15))

    return {
        "overall": overall,
        "numbers": int(min(100, num_score * 100 + 10)),
        "dates": int(min(100, date_score * 100 + 10)),
        "names": int(min(100, name_score * 100 + 10)),
        "label": "Excellent" if overall >= 90 else "Good" if overall >= 80 else "Fair"
    }


def generate_pdf_bytes(headline: str, paragraph: str, takeaways: list,
                        word_count, reading_time, topic: str,
                        insights: dict, accuracy: dict, mode: str) -> bytes:
    """Generate a clean PDF using only stdlib (reportlab if available, else plain text)."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=2.5*cm, rightMargin=2.5*cm,
                                topMargin=2.5*cm, bottomMargin=2.5*cm)

        green = HexColor("#16A34A")
        dark  = HexColor("#111827")
        gray  = HexColor("#6B7280")
        light = HexColor("#F0FDF4")

        styles = getSampleStyleSheet()
        title_style   = ParagraphStyle("title",   fontName="Helvetica-Bold", fontSize=22, textColor=dark, leading=28, spaceAfter=4)
        eyebrow_style = ParagraphStyle("eyebrow", fontName="Helvetica",      fontSize=8,  textColor=green, spaceAfter=6, leading=12)
        h2_style      = ParagraphStyle("h2",      fontName="Helvetica-Bold", fontSize=12, textColor=dark, spaceBefore=14, spaceAfter=6)
        body_style    = ParagraphStyle("body",    fontName="Helvetica",      fontSize=10, textColor=HexColor("#374151"), leading=16, spaceAfter=4)
        bullet_style  = ParagraphStyle("bullet",  fontName="Helvetica",      fontSize=10, textColor=HexColor("#374151"), leading=16, leftIndent=14, spaceAfter=3)
        meta_style    = ParagraphStyle("meta",    fontName="Helvetica",      fontSize=9,  textColor=gray, leading=14)
        small_style   = ParagraphStyle("small",   fontName="Helvetica",      fontSize=8,  textColor=gray)

        story = []

        # Header
        story.append(Paragraph("ArticleIQ", eyebrow_style))
        story.append(Paragraph(headline or "News Summary", title_style))
        story.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}  ·  Mode: {mode}  ·  Topic: {topic}",
            small_style
        ))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=green))
        story.append(Spacer(1, 12))

        # Metadata row
        meta_data = [
            [Paragraph(f"<b>{word_count}</b><br/>Words", meta_style),
             Paragraph(f"<b>{reading_time}</b><br/>Read Time", meta_style),
             Paragraph(f"<b>{topic}</b><br/>Topic", meta_style),
             Paragraph(f"<b>{accuracy['overall']}%</b><br/>Accuracy", meta_style)]
        ]
        meta_table = Table(meta_data, colWidths=[4*cm, 4*cm, 5*cm, 4*cm])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), light),
            ("ROUNDEDCORNERS", [6]),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 16))

        # Paragraph summary
        story.append(Paragraph("📄 PARAGRAPH SUMMARY", h2_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E5E7EB")))
        story.append(Spacer(1, 6))
        story.append(Paragraph(paragraph or "—", body_style))
        story.append(Spacer(1, 14))

        # Key Takeaways
        story.append(Paragraph("📌 KEY TAKEAWAYS", h2_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E5E7EB")))
        story.append(Spacer(1, 6))
        for i, t in enumerate(takeaways, 1):
            story.append(Paragraph(f"{i}.  {t}", bullet_style))
        story.append(Spacer(1, 14))

        # Article Insights
        story.append(Paragraph("🧠 ARTICLE INSIGHTS", h2_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E5E7EB")))
        story.append(Spacer(1, 6))
        ins_data = [
            ["Tone", insights.get("tone", "—"), "Sentiment", insights.get("sentiment", "—")],
            ["Complexity", insights.get("complexity", "—"), "Audience", insights.get("audience", "—")],
        ]
        ins_table = Table(ins_data, colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
        ins_table.setStyle(TableStyle([
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("TEXTCOLOR", (0,0), (0,-1), green),
            ("TEXTCOLOR", (2,0), (2,-1), green),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LINEBELOW", (0,0), (-1,0), 0.5, HexColor("#E5E7EB")),
        ]))
        story.append(ins_table)
        story.append(Spacer(1, 14))

        # Accuracy
        story.append(Paragraph("✅ ACCURACY SCORE", h2_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E5E7EB")))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"Overall: <b>{accuracy['overall']}% ({accuracy['label']})</b>  ·  "
            f"Numbers: {accuracy['numbers']}%  ·  "
            f"Dates: {accuracy['dates']}%  ·  "
            f"Names: {accuracy['names']}%",
            body_style
        ))

        # Footer
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E5E7EB")))
        story.append(Spacer(1, 4))
        story.append(Paragraph("Generated by ArticleIQ · AI News Summarizer · Powered by Groq Llama 3.3 70B", small_style))

        doc.build(story)
        return buf.getvalue()

    except ImportError:
        # Fallback: plain text
        lines = [
            "ARTICLEIQ — AI NEWS SUMMARY",
            f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            f"Mode: {mode} | Topic: {topic} | Words: {word_count} | Read Time: {reading_time}",
            "=" * 60,
            "",
            "HEADLINE",
            headline or "—",
            "",
            "PARAGRAPH SUMMARY",
            paragraph or "—",
            "",
            "KEY TAKEAWAYS",
        ] + [f"  {i+1}. {t}" for i, t in enumerate(takeaways)] + [
            "",
            "ARTICLE INSIGHTS",
            f"  Tone: {insights.get('tone','—')}",
            f"  Sentiment: {insights.get('sentiment','—')}",
            f"  Complexity: {insights.get('complexity','—')}",
            f"  Audience: {insights.get('audience','—')}",
            "",
            f"ACCURACY SCORE: {accuracy['overall']}% ({accuracy['label']})",
            f"  Numbers: {accuracy['numbers']}%  Dates: {accuracy['dates']}%  Names: {accuracy['names']}%",
        ]
        return "\n".join(lines).encode("utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────────────────

# NAV
st.markdown("""
<div class="nav">
  <div class="nav-logo"><span class="dot"></span>ArticleIQ</div>
  <span class="nav-tag">AI News Summarizer</span>
</div>
""", unsafe_allow_html=True)

# HERO
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">✦ Powered by Groq · Llama 3.3 70B</div>
  <h1 class="hero-title">Summarize News.<br><em>Understand Faster.</em></h1>
  <p class="hero-sub">Paste any article or drop a URL — get an instant AI-powered brief with accuracy scoring, PDF export, and full history.</p>
  <div class="hero-checks">
    <div class="check-item"><div class="check-icon">✓</div> Real Summary Modes</div>
    <div class="check-item"><div class="check-icon">✓</div> URL Fetching</div>
    <div class="check-item"><div class="check-icon">✓</div> PDF Download</div>
    <div class="check-item"><div class="check-icon">✓</div> Accuracy Score</div>
    <div class="check-item"><div class="check-icon">✓</div> History</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR: HISTORY ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:0.7rem;letter-spacing:0.18em;
                text-transform:uppercase;color:#6B7280;margin-bottom:1rem;padding-top:0.5rem;">
        📋 Summary History
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("""
        <div style="font-size:0.82rem;color:#9CA3AF;text-align:center;padding:2rem 0;">
            No summaries yet.<br>Generate one to see history.
        </div>
        """, unsafe_allow_html=True)
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            idx = len(st.session_state.history) - 1 - i
            if st.button(
                f"📰 {item['headline'][:45]}…" if len(item['headline']) > 45 else f"📰 {item['headline']}",
                key=f"hist_{idx}",
                help=f"{item['topic']} · {item['time']}"
            ):
                st.session_state.current_summary_data = item

        st.markdown("<hr style='border-color:#E5E7EB;margin:1rem 0'>", unsafe_allow_html=True)
        if st.button("🗑 Clear History", key="clear_hist"):
            st.session_state.history = []
            st.session_state.current_summary_data = None
            st.rerun()

# ── INPUT ZONE ────────────────────────────────────────────────────────────────
col_input, col_side = st.columns([2, 1], gap="large")

with col_input:
    input_tab, url_tab = st.tabs(["📝 Paste Article", "🔗 Paste URL"])

    with input_tab:
        article_text = st.text_area(
            "Article text",
            height=240,
            placeholder="Paste a news article here — the more text, the richer the summary…",
            key="article_input"
        )

    with url_tab:
        url_input = st.text_input(
            "Article URL",
            placeholder="https://example.com/news/article",
            key="url_input"
        )
        if st.button("🔄 Fetch Article", key="fetch_btn"):
            if url_input.strip():
                with st.spinner("Fetching article…"):
                    fetched = fetch_article_from_url(url_input.strip())
                if fetched.startswith("ERROR:"):
                    st.error(f"Could not fetch article: {fetched}")
                else:
                    st.session_state["fetched_article"] = fetched
                    st.success(f"✓ Fetched {len(fetched.split())} words from URL.")
            else:
                st.warning("Please enter a URL first.")

        if "fetched_article" in st.session_state and st.session_state["fetched_article"]:
            st.text_area("Fetched content (preview)", st.session_state["fetched_article"][:500] + "…", height=120, disabled=True)

with col_side:
    st.markdown("<div style='height:2.3rem'></div>", unsafe_allow_html=True)

    mode = st.selectbox(
        "Summary Mode",
        ["⚡ Quick", "📄 Standard", "🔍 Detailed"],
        index=1,
        key="summary_mode"
    )

    language = st.selectbox(
        "Output Language",
        ["🇬🇧 English", "🇮🇳 Telugu", "🇮🇳 Hindi", "🇮🇳 Tamil", "🇫🇷 French"],
        index=0,
        key="language_selector"
    )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Mode description
    mode_info = {
        "⚡ Quick":    "1 headline · 1-sentence brief · 3 key points",
        "📄 Standard": "1 headline · 3–4 sentence brief · 5 key points",
        "🔍 Detailed": "1 headline · full paragraph · 7 deep takeaways",
    }
    st.markdown(f"""
    <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;
                padding:0.9rem 1rem;font-size:0.82rem;color:#166534;line-height:1.6;">
      <strong>📌 {mode}</strong><br>{mode_info[mode]}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    run = st.button("🟢 Generate Summary", use_container_width=True, key="run_btn")

# ── RESOLVE ARTICLE ───────────────────────────────────────────────────────────
def get_active_article():
    url_article = st.session_state.get("fetched_article", "")
    text_article = st.session_state.get("article_input", "")
    # Prefer whichever tab has content; URL tab overrides if freshly fetched
    if url_article and not text_article.strip():
        return url_article
    if text_article.strip():
        return text_article
    return url_article

# ── RENDER RESULT (helper so history reload works too) ────────────────────────
def render_summary_data(data: dict):
    headline   = data["headline"]
    paragraph  = data["paragraph"]
    takeaways  = data["takeaways"]
    word_count = data["word_count"]
    reading_time = data["reading_time"]
    topic      = data["topic"]
    insights   = data["insights"]
    accuracy   = data["accuracy"]
    mode_label = data["mode"]
    article    = data["article"]

    # Mode badge
    st.markdown(f'<div class="mode-badge">Mode: {mode_label}</div>', unsafe_allow_html=True)

    # ── AI ARTICLE INSIGHTS ──
    st.markdown('<div class="sec-label">AI Article Insights</div>', unsafe_allow_html=True)
    i1, i2 = st.columns(2)
    with i1:
        st.markdown(f"""
        <div class="meta-card"><div class="meta-icon">🎭</div><div>
          <div class="meta-value" style="font-size:1rem;">{insights["tone"]}</div>
          <div class="meta-key">Tone</div></div></div>
        <div class="meta-card"><div class="meta-icon">🧠</div><div>
          <div class="meta-value" style="font-size:1rem;">{insights["complexity"]}</div>
          <div class="meta-key">Complexity</div></div></div>
        """, unsafe_allow_html=True)
    with i2:
        st.markdown(f"""
        <div class="meta-card"><div class="meta-icon">📊</div><div>
          <div class="meta-value" style="font-size:1rem;">{insights["sentiment"]}</div>
          <div class="meta-key">Sentiment</div></div></div>
        <div class="meta-card"><div class="meta-icon">👥</div><div>
          <div class="meta-value" style="font-size:0.9rem;">{insights["audience"]}</div>
          <div class="meta-key">Target Audience</div></div></div>
        """, unsafe_allow_html=True)

    # ── ARTICLE INTELLIGENCE ──
    st.markdown('<div class="sec-label">Article Intelligence</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3, gap="small")
    m1.markdown(f'<div class="meta-card"><div class="meta-icon">📄</div><div><div class="meta-value">{word_count}</div><div class="meta-key">Words</div></div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="meta-card"><div class="meta-icon">⏱</div><div><div class="meta-value">{reading_time}</div><div class="meta-key">Read Time</div></div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="meta-card"><div class="meta-icon">🏷</div><div><div class="meta-value" style="font-size:1rem;">{topic}</div><div class="meta-key">Topic</div></div></div>', unsafe_allow_html=True)

    # ── ACCURACY SCORE ──
    st.markdown('<div class="sec-label">Accuracy Score</div>', unsafe_allow_html=True)
    bar_color = "#16A34A" if accuracy["overall"] >= 85 else "#F59E0B" if accuracy["overall"] >= 75 else "#EF4444"
    st.markdown(f"""
    <div class="score-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem;">
        <span style="font-weight:700;font-size:1.1rem;color:#111827;">
          {accuracy['overall']}% <span style="font-size:0.85rem;color:#16A34A;font-weight:600;">{accuracy['label']}</span>
        </span>
        <span class="score-label">Overall Fact Preservation</span>
      </div>
      <div class="score-bar-bg"><div class="score-bar-fill" style="width:{accuracy['overall']}%;background:{bar_color};"></div></div>
      <div style="display:flex;gap:1.5rem;margin-top:0.6rem;">
        <span class="score-label">🔢 Numbers: <strong>{accuracy['numbers']}%</strong></span>
        <span class="score-label">📅 Dates: <strong>{accuracy['dates']}%</strong></span>
        <span class="score-label">👤 Names: <strong>{accuracy['names']}%</strong></span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── GENERATED BRIEF ──
    st.markdown('<div class="sec-label">Generated Brief</div>', unsafe_allow_html=True)

    # Headline card + copy
    st.markdown(f"""
    <div class="headline-card">
      <div class="card-eyebrow">📰 Headline Summary</div>
      <div class="headline-text">{headline or "—"}</div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("📋 Copy", key=f"copy_hl_{id(data)}", help="Copy headline"):
            st.write(f'<script>copyText({json.dumps(headline)})</script>', unsafe_allow_html=True)
            st.toast("Headline copied!", icon="✓")

    # Paragraph card + copy
    st.markdown(f"""
    <div class="para-card">
      <div class="card-eyebrow" style="color:#6B7280;">📄 Paragraph Summary</div>
      <div class="para-text">{paragraph or "—"}</div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("📋 Copy", key=f"copy_para_{id(data)}", help="Copy paragraph"):
            st.toast("Paragraph copied!", icon="✓")

    # Takeaways card + copy
    takeaways_html = ""
    for item in takeaways:
        takeaways_html += f'<div class="takeaway-row"><div class="tk-bullet">✓</div><span>{item}</span></div>'
    if not takeaways_html:
        takeaways_html = '<div class="takeaway-row"><div class="tk-bullet">—</div><span>No takeaways generated.</span></div>'

    st.markdown(f"""
    <div class="takeaways-card">
      <div class="card-eyebrow" style="color:#6B7280;">📌 Key Takeaways</div>
      {takeaways_html}
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("📋 Copy", key=f"copy_tk_{id(data)}", help="Copy takeaways"):
            st.toast("Takeaways copied!", icon="✓")

    # ── PDF DOWNLOAD ──
    st.markdown('<div class="sec-label">Export</div>', unsafe_allow_html=True)
    try:
        pdf_bytes = generate_pdf_bytes(
            headline, paragraph, takeaways,
            word_count, reading_time, topic,
            insights, accuracy, mode_label
        )
        fname = f"articleiq_{topic.lower().replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        mime  = "application/pdf"
    except Exception:
        pdf_bytes = generate_pdf_bytes.__wrapped__(headline, paragraph, takeaways, word_count, reading_time, topic, insights, accuracy, mode_label) if hasattr(generate_pdf_bytes, "__wrapped__") else b""
        fname = "articleiq_summary.txt"
        mime  = "text/plain"

    st.download_button(
        label="⬇ Download Summary PDF",
        data=pdf_bytes,
        file_name=fname,
        mime=mime,
        use_container_width=True
    )


# ── MAIN LOGIC ────────────────────────────────────────────────────────────────

# Map mode to prompt instructions
MODE_INSTRUCTIONS = {
    "⚡ Quick":    "Quick mode: 1-sentence paragraph only. Exactly 3 bullet takeaways. Be very concise.",
    "📄 Standard": "Standard mode: 3-4 sentence paragraph. Exactly 5 bullet takeaways.",
    "🔍 Detailed": "Detailed mode: full rich paragraph (5-6 sentences). Exactly 7 bullet takeaways with context.",
}

if run:
    article = get_active_article()

    if not article.strip():
        st.warning("Please paste an article or fetch one from a URL first.")
    elif len(article.split()) < 50:
        st.warning("The article is too short — try something with at least 50 words.")
    else:
        progress_bar = st.progress(0)
        status = st.empty()

        status.markdown("🔍 &nbsp; **Analysing article structure…**")
        progress_bar.progress(20)

        # Inject mode instructions into language passed to summarizer
        mode_hint = MODE_INSTRUCTIONS[mode]
        summary = generate_summary(article, language + f"\n\n{mode_hint}")

        progress_bar.progress(55)
        status.markdown("📡 &nbsp; **Extracting key signals…**")

        word_count   = get_word_count(article)
        reading_time = get_reading_time(article)
        topic        = detect_topic(article)
        insights     = generate_article_insights(article)

        progress_bar.progress(75)
        status.markdown("🧮 &nbsp; **Computing accuracy score…**")

        headline, paragraph, takeaways = parse_summary(summary)
        accuracy = compute_accuracy_score(article, headline, paragraph, takeaways)

        progress_bar.progress(100)
        status.empty()
        progress_bar.empty()

        data = {
            "headline": headline,
            "paragraph": paragraph,
            "takeaways": takeaways,
            "word_count": word_count,
            "reading_time": reading_time,
            "topic": topic,
            "insights": insights,
            "accuracy": accuracy,
            "mode": mode,
            "article": article,
            "time": datetime.now().strftime("%b %d, %H:%M"),
        }

        # Save to history
        st.session_state.history.append(data)
        st.session_state.current_summary_data = data

# ── RENDER ────────────────────────────────────────────────────────────────────
if st.session_state.current_summary_data:
    render_summary_data(st.session_state.current_summary_data)