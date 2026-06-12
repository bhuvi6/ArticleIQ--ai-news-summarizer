"""
ArticleIQ — Multi-Article Intelligence Engine
Compare 2–5 articles: detect agreements, contradictions, viewpoints, and generate unified intelligence.
"""

from groq import Groq
import os
import json
import re


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set in environment or secrets.")
    return Groq(api_key=api_key)


def analyze_multiple_articles(articles: list[dict]) -> dict:
    """
    Perform cross-article intelligence analysis.

    Input:
        articles: list of dicts with keys: url (str), content (str), title (str)
                  Length: 2 to 5 articles.

    Returns dict with:
        unified_summary (str)
        agreement_points (list[str])
        contradictions (list[dict]: {claim, source_a, source_b})
        viewpoint_differences (list[str])
        missing_coverage (list[str])
        sentiment_by_source (list[dict]: {source, sentiment, bias_lean})
        what_actually_happened (str)
        source_comparison (list[dict]: {source, coverage_focus, tone, key_claims})
    """
    if not articles or len(articles) < 2:
        return _error_result("At least 2 articles are required for comparison.")

    articles = articles[:5]  # Cap at 5
    client = get_groq_client()

    # Build article block for prompt
    article_blocks = []
    for i, art in enumerate(articles, 1):
        label = f"SOURCE {i}"
        domain = _extract_domain(art.get("url", ""))
        content_excerpt = art.get("content", "")[:2000]
        article_blocks.append(
            f"--- {label} ({domain}) ---\n{content_excerpt}\n"
        )

    combined = "\n\n".join(article_blocks)

    prompt = f"""You are an elite intelligence analyst comparing multiple news sources on the same story or topic.

Analyze these {len(articles)} articles carefully.

Return ONLY valid JSON in this exact structure (no markdown, no code fences):

{{
  "unified_summary": "<2-3 paragraph unified narrative combining all sources>",
  "agreement_points": [
    "<fact or claim all/most sources agree on>",
    "<another agreement>"
  ],
  "contradictions": [
    {{
      "claim": "<the disputed point>",
      "source_a": "<what one source says>",
      "source_b": "<what another source says>"
    }}
  ],
  "viewpoint_differences": [
    "<how Source 1 frames the story differently from Source 2>",
    "<another framing difference>"
  ],
  "missing_coverage": [
    "<important angle Source 1 misses>",
    "<what Source 2 fails to address>"
  ],
  "sentiment_by_source": [
    {{
      "source": "Source 1 (domain.com)",
      "sentiment": "Neutral/Positive/Negative",
      "bias_lean": "Left/Center-Left/Center/Center-Right/Right/Unknown"
    }}
  ],
  "what_actually_happened": "<Concise 2-3 sentence factual brief: what actually happened based on cross-referencing all sources>",
  "source_comparison": [
    {{
      "source": "Source 1 (domain.com)",
      "coverage_focus": "<what this source emphasizes>",
      "tone": "<one word tone>",
      "key_claims": ["<claim 1>", "<claim 2>"]
    }}
  ]
}}

Articles to analyze:
{combined}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.15,
            max_tokens=2500,
        )
        raw = completion.choices[0].message.content.strip()

        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
        raw = raw.strip()

        data = json.loads(raw)

        # Inject source domain labels if missing
        for i, item in enumerate(data.get("sentiment_by_source", [])):
            if i < len(articles):
                domain = _extract_domain(articles[i].get("url", ""))
                if domain and "Source" in item.get("source", ""):
                    item["source"] = f"Source {i + 1} ({domain})"

        for i, item in enumerate(data.get("source_comparison", [])):
            if i < len(articles):
                domain = _extract_domain(articles[i].get("url", ""))
                if domain and "Source" in item.get("source", ""):
                    item["source"] = f"Source {i + 1} ({domain})"

        return data

    except json.JSONDecodeError:
        # Attempt partial extraction fallback
        return _fallback_parse(raw, articles)
    except Exception as e:
        return _error_result(str(e))


def _extract_domain(url: str) -> str:
    if not url:
        return "unknown"
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.lstrip("www.")
    except Exception:
        return "unknown"


def _error_result(msg: str) -> dict:
    return {
        "unified_summary": f"Analysis failed: {msg}",
        "agreement_points": [],
        "contradictions": [],
        "viewpoint_differences": [],
        "missing_coverage": [],
        "sentiment_by_source": [],
        "what_actually_happened": "Unable to determine.",
        "source_comparison": [],
        "error": msg,
    }


def _fallback_parse(raw: str, articles: list) -> dict:
    """Return a graceful partial result if JSON parsing fails."""
    return {
        "unified_summary": raw[:800] if raw else "Parsing failed.",
        "agreement_points": ["Cross-reference results unavailable — see unified summary."],
        "contradictions": [],
        "viewpoint_differences": [],
        "missing_coverage": [],
        "sentiment_by_source": [
            {"source": f"Source {i+1} ({_extract_domain(a.get('url',''))})", "sentiment": "Unknown", "bias_lean": "Unknown"}
            for i, a in enumerate(articles)
        ],
        "what_actually_happened": "Please review the unified summary above.",
        "source_comparison": [],
    }
