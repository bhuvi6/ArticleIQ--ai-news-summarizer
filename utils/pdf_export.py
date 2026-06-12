"""
ArticleIQ — PDF Export Engine
Professional report generation using ReportLab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import io
from datetime import datetime


# Brand palette
BRAND_GREEN = colors.HexColor("#16a34a")
BRAND_DARK = colors.HexColor("#0f172a")
BRAND_LIGHT_GREEN = colors.HexColor("#dcfce7")
BRAND_GRAY = colors.HexColor("#64748b")
BRAND_LIGHT_GRAY = colors.HexColor("#f8fafc")
BRAND_BORDER = colors.HexColor("#e2e8f0")


def generate_pdf_report(
    headline: str,
    paragraph: str,
    takeaways: list[str],
    insights: dict,
    accuracy: dict | None = None,
    credibility: dict | None = None,
    why_matters: str | None = None,
    source_url: str = "",
    language: str = "English",
    mode: str = "Standard",
) -> bytes:
    """
    Generate a professional PDF report for a summarized article.
    Returns bytes of the PDF file.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2.2 * cm,
        leftMargin=2.2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.2 * cm,
    )

    styles = _build_styles()
    story = []

    # ── Header ──────────────────────────────────────────────────
    story.append(Paragraph("ArticleIQ", styles["brand_name"]))
    story.append(Paragraph("AI Research Intelligence Platform", styles["brand_tagline"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=BRAND_GREEN))
    story.append(Spacer(1, 0.4 * cm))

    # ── Report metadata ──────────────────────────────────────────
    meta_data = [
        ["Generated", datetime.now().strftime("%B %d, %Y at %H:%M")],
        ["Mode", mode],
        ["Language", language],
        ["Source", source_url[:70] + ("…" if len(source_url) > 70 else "") if source_url else "Pasted Text"],
    ]
    meta_table = Table(meta_data, colWidths=[3.5 * cm, 13 * cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("TEXTCOLOR", (0, 0), (0, -1), BRAND_GRAY),
        ("TEXTCOLOR", (1, 0), (1, -1), BRAND_DARK),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.6 * cm))

    # ── Headline ─────────────────────────────────────────────────
    story.append(Paragraph("HEADLINE", styles["section_label"]))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(headline, styles["headline"]))
    story.append(Spacer(1, 0.6 * cm))

    # ── Credibility (if available) ───────────────────────────────
    if credibility:
        story.append(Paragraph("SOURCE CREDIBILITY", styles["section_label"]))
        story.append(Spacer(1, 0.15 * cm))
        cred_score = credibility.get("score", "N/A")
        cred_tier = credibility.get("tier", "Unknown")
        cred_label = credibility.get("label", "")
        cred_text = f"<b>{cred_score}/100</b> — {cred_tier} ({cred_label}). {credibility.get('explanation', '')}"
        story.append(Paragraph(cred_text, styles["body_text"]))
        story.append(Spacer(1, 0.5 * cm))

    # ── Summary ──────────────────────────────────────────────────
    story.append(Paragraph("SUMMARY", styles["section_label"]))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(paragraph, styles["body_text"]))
    story.append(Spacer(1, 0.6 * cm))

    # ── Key Takeaways ─────────────────────────────────────────────
    story.append(Paragraph("KEY TAKEAWAYS", styles["section_label"]))
    story.append(Spacer(1, 0.15 * cm))
    for i, t in enumerate(takeaways, 1):
        story.append(Paragraph(f"{i}.  {t}", styles["takeaway"]))
        story.append(Spacer(1, 0.1 * cm))
    story.append(Spacer(1, 0.5 * cm))

    # ── AI Insights ───────────────────────────────────────────────
    story.append(Paragraph("AI INSIGHTS", styles["section_label"]))
    story.append(Spacer(1, 0.2 * cm))
    insight_data = [
        ["Tone", insights.get("tone", "—"),
         "Sentiment", insights.get("sentiment", "—")],
        ["Complexity", insights.get("complexity", "—"),
         "Audience", insights.get("audience", "—")],
    ]
    insight_table = Table(insight_data, colWidths=[3 * cm, 6.5 * cm, 3 * cm, 6.5 * cm])
    insight_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BRAND_LIGHT_GREEN),
        ("BACKGROUND", (2, 0), (2, -1), BRAND_LIGHT_GREEN),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), BRAND_GREEN),
        ("TEXTCOLOR", (2, 0), (2, -1), BRAND_GREEN),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, BRAND_BORDER),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BRAND_LIGHT_GRAY, colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(insight_table)
    story.append(Spacer(1, 0.6 * cm))

    # ── Accuracy Score (if available) ────────────────────────────
    if accuracy:
        story.append(Paragraph("ACCURACY VALIDATION", styles["section_label"]))
        story.append(Spacer(1, 0.15 * cm))
        acc_score = accuracy.get("score", "N/A")
        acc_conf = accuracy.get("confidence", "")
        acc_risk = accuracy.get("hallucination_risk", "")
        acc_expl = accuracy.get("explanation", "")
        story.append(Paragraph(
            f"<b>Score: {acc_score}/100</b> | Confidence: {acc_conf} | Hallucination Risk: {acc_risk}",
            styles["body_text"]
        ))
        if acc_expl:
            story.append(Spacer(1, 0.1 * cm))
            story.append(Paragraph(acc_expl, styles["body_text"]))
        missing = accuracy.get("missing_info", [])
        if missing:
            story.append(Spacer(1, 0.15 * cm))
            story.append(Paragraph("<b>Missing from summary:</b>", styles["body_text"]))
            for item in missing:
                story.append(Paragraph(f"• {item}", styles["body_text"]))
        story.append(Spacer(1, 0.5 * cm))

    # ── Why This Matters ─────────────────────────────────────────
    if why_matters:
        story.append(Paragraph("WHY THIS MATTERS", styles["section_label"]))
        story.append(Spacer(1, 0.15 * cm))
        # Convert markdown bold to ReportLab bold
        import re
        formatted = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", why_matters)
        for line in formatted.splitlines():
            stripped = line.strip()
            if stripped.startswith("-"):
                stripped = "• " + stripped[1:].strip()
            if stripped:
                story.append(Paragraph(stripped, styles["body_text"]))
                story.append(Spacer(1, 0.08 * cm))
        story.append(Spacer(1, 0.5 * cm))

    # ── Footer ───────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=BRAND_BORDER))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "Generated by ArticleIQ — AI Research Intelligence Platform | For informational purposes only.",
        styles["footer"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def _build_styles() -> dict:
    base = getSampleStyleSheet()

    return {
        "brand_name": ParagraphStyle(
            "brand_name",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=BRAND_GREEN,
            spaceAfter=2,
            alignment=TA_LEFT,
        ),
        "brand_tagline": ParagraphStyle(
            "brand_tagline",
            fontName="Helvetica",
            fontSize=9,
            textColor=BRAND_GRAY,
            spaceAfter=4,
            alignment=TA_LEFT,
        ),
        "section_label": ParagraphStyle(
            "section_label",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            textColor=BRAND_GREEN,
            spaceAfter=2,
            spaceBefore=4,
            letterSpacing=1.5,
            alignment=TA_LEFT,
        ),
        "headline": ParagraphStyle(
            "headline",
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=BRAND_DARK,
            leading=22,
            spaceAfter=4,
            alignment=TA_LEFT,
        ),
        "body_text": ParagraphStyle(
            "body_text",
            fontName="Helvetica",
            fontSize=10,
            textColor=BRAND_DARK,
            leading=15,
            spaceAfter=3,
            alignment=TA_LEFT,
        ),
        "takeaway": ParagraphStyle(
            "takeaway",
            fontName="Helvetica",
            fontSize=10,
            textColor=BRAND_DARK,
            leading=14,
            leftIndent=8,
            spaceAfter=2,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica",
            fontSize=7.5,
            textColor=BRAND_GRAY,
            alignment=TA_CENTER,
        ),
    }
