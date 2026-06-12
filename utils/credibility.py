"""
ArticleIQ — Source Credibility Engine
Domain-based reliability scoring with AI-assisted fallback for unknown sources.
"""

from urllib.parse import urlparse
from groq import Groq
import os


# Curated domain reputation database
DOMAIN_REPUTATION: dict[str, dict] = {
    # Tier 1 — Established Global News
    "bbc.com": {"score": 92, "tier": "High", "label": "Global Public Broadcaster"},
    "bbc.co.uk": {"score": 92, "tier": "High", "label": "Global Public Broadcaster"},
    "reuters.com": {"score": 95, "tier": "High", "label": "International Wire Service"},
    "apnews.com": {"score": 94, "tier": "High", "label": "International Wire Service"},
    "theguardian.com": {"score": 88, "tier": "High", "label": "Established Broadsheet"},
    "nytimes.com": {"score": 89, "tier": "High", "label": "Major Newspaper of Record"},
    "wsj.com": {"score": 88, "tier": "High", "label": "Financial Newspaper of Record"},
    "washingtonpost.com": {"score": 87, "tier": "High", "label": "Major National Newspaper"},
    "ft.com": {"score": 91, "tier": "High", "label": "Financial Press"},
    "economist.com": {"score": 90, "tier": "High", "label": "Analysis & Opinion Weekly"},
    "bloomberg.com": {"score": 90, "tier": "High", "label": "Financial & Business Media"},
    "npr.org": {"score": 88, "tier": "High", "label": "Public Radio / News"},
    "pbs.org": {"score": 87, "tier": "High", "label": "Public Broadcasting"},
    "time.com": {"score": 82, "tier": "High", "label": "Major News Magazine"},
    "theatlantic.com": {"score": 83, "tier": "High", "label": "Long-form News & Opinion"},
    # Tier 1 — India
    "thehindu.com": {"score": 88, "tier": "High", "label": "National Newspaper of Record (India)"},
    "hindustantimes.com": {"score": 82, "tier": "High", "label": "Major Indian Newspaper"},
    "ndtv.com": {"score": 80, "tier": "High", "label": "Indian News Broadcaster"},
    "indianexpress.com": {"score": 85, "tier": "High", "label": "National Indian Newspaper"},
    "livemint.com": {"score": 84, "tier": "High", "label": "Indian Financial Press"},
    "economictimes.indiatimes.com": {"score": 83, "tier": "High", "label": "Indian Financial Newspaper"},
    "business-standard.com": {"score": 82, "tier": "High", "label": "Indian Business News"},
    "theprint.in": {"score": 78, "tier": "Medium-High", "label": "Independent Indian News"},
    "scroll.in": {"score": 76, "tier": "Medium-High", "label": "Independent Indian Digital Media"},
    "thewire.in": {"score": 74, "tier": "Medium-High", "label": "Independent Indian Journalism"},
    # Tier 2 — Tech & Business
    "techcrunch.com": {"score": 82, "tier": "High", "label": "Tech Industry Publication"},
    "wired.com": {"score": 83, "tier": "High", "label": "Technology & Culture Magazine"},
    "arstechnica.com": {"score": 84, "tier": "High", "label": "Technology Analysis"},
    "theverge.com": {"score": 79, "tier": "Medium-High", "label": "Technology Media"},
    "venturebeat.com": {"score": 75, "tier": "Medium-High", "label": "Enterprise Technology"},
    "cnn.com": {"score": 78, "tier": "Medium-High", "label": "Cable News Network"},
    "cnbc.com": {"score": 80, "tier": "High", "label": "Financial News Broadcaster"},
    "forbes.com": {"score": 75, "tier": "Medium-High", "label": "Business Magazine"},
    "fortune.com": {"score": 78, "tier": "Medium-High", "label": "Business Magazine"},
    "nature.com": {"score": 96, "tier": "High", "label": "Peer-Reviewed Science Journal"},
    "sciencemag.org": {"score": 95, "tier": "High", "label": "Peer-Reviewed Science Journal"},
    "who.int": {"score": 92, "tier": "High", "label": "UN Health Authority"},
    "nih.gov": {"score": 93, "tier": "High", "label": "US National Health Authority"},
}


def get_credibility_score(url: str) -> dict:
    """
    Evaluate source credibility from URL domain.
    Falls back to AI-assisted scoring for unknown domains.

    Returns dict with: score (int), tier (str), label (str), domain (str), explanation (str)
    """
    if not url or not url.startswith("http"):
        return _unknown_source()

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().lstrip("www.")
    except Exception:
        return _unknown_source()

    # Exact match
    if domain in DOMAIN_REPUTATION:
        rep = DOMAIN_REPUTATION[domain]
        return {
            "score": rep["score"],
            "tier": rep["tier"],
            "label": rep["label"],
            "domain": domain,
            "explanation": _build_explanation(domain, rep["score"], rep["tier"], rep["label"], known=True),
        }

    # Subdomain fallback — check base domain
    parts = domain.split(".")
    for i in range(len(parts) - 1):
        base = ".".join(parts[i:])
        if base in DOMAIN_REPUTATION:
            rep = DOMAIN_REPUTATION[base]
            return {
                "score": rep["score"],
                "tier": rep["tier"],
                "label": rep["label"],
                "domain": domain,
                "explanation": _build_explanation(domain, rep["score"], rep["tier"], rep["label"], known=True),
            }

    # Unknown domain — AI-assisted scoring
    return _ai_score_domain(domain)


def _ai_score_domain(domain: str) -> dict:
    """Use Groq to estimate credibility for unrecognized domains."""
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("No API key")

        client = Groq(api_key=api_key)
        prompt = f"""You are a media credibility expert.

Evaluate the news source domain: {domain}

Return ONLY this format:
SCORE: <integer 0-100>
TIER: <High/Medium-High/Medium/Low>
LABEL: <short description, max 6 words>
EXPLANATION: <one sentence explaining the rating>
"""
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=120,
        )
        raw = completion.choices[0].message.content.strip()
        return _parse_ai_credibility(raw, domain)

    except Exception:
        return {
            "score": 55,
            "tier": "Medium",
            "label": "Unknown Source",
            "domain": domain,
            "explanation": "This domain is not in our credibility database. Exercise caution and verify independently.",
        }


def _parse_ai_credibility(raw: str, domain: str) -> dict:
    result = {"score": 55, "tier": "Medium", "label": "Unknown Source", "domain": domain, "explanation": ""}
    for line in raw.splitlines():
        s = line.strip()
        if s.startswith("SCORE:"):
            try:
                result["score"] = max(0, min(100, int(s.split(":", 1)[1].strip().split()[0])))
            except Exception:
                pass
        elif s.startswith("TIER:"):
            result["tier"] = s.split(":", 1)[1].strip()
        elif s.startswith("LABEL:"):
            result["label"] = s.split(":", 1)[1].strip()
        elif s.startswith("EXPLANATION:"):
            result["explanation"] = s.split(":", 1)[1].strip()
    if not result["explanation"]:
        result["explanation"] = f"AI-estimated credibility for {domain}. Verify this source independently."
    return result


def _unknown_source() -> dict:
    return {
        "score": 50,
        "tier": "Unknown",
        "label": "Source Not Identified",
        "domain": "N/A",
        "explanation": "No URL provided. Credibility cannot be assessed.",
    }


def _build_explanation(domain: str, score: int, tier: str, label: str, known: bool) -> str:
    if score >= 90:
        return f"{domain} is a highly trusted {label.lower()} with a strong editorial record and international recognition."
    elif score >= 80:
        return f"{domain} is a reputable {label.lower()} with established editorial standards."
    elif score >= 70:
        return f"{domain} is a generally reliable source. Cross-reference critical claims with primary sources."
    else:
        return f"{domain} has moderate credibility. Verify important claims independently before relying on this source."
