"""
ArticleIQ — Summarization Engine
Groq + Llama 3.3 70B powered summarization with multilingual support.
Modes: Quick / Standard / Detailed
Languages: English, Telugu, Hindi, Tamil, French
"""

from groq import Groq
import os


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set in environment or secrets.")
    return Groq(api_key=api_key)


LANGUAGE_INSTRUCTIONS = {
    "English": "Respond entirely in English.",
    "Telugu": "Respond entirely in Telugu (తెలుగు). All output must be in Telugu script.",
    "Hindi": "Respond entirely in Hindi (हिंदी). All output must be in Devanagari script.",
    "Tamil": "Respond entirely in Tamil (தமிழ்). All output must be in Tamil script.",
    "French": "Respond entirely in French. All output must be in French.",
}

MODE_CONFIGS = {
    "Quick": {
        "headline_words": 15,
        "paragraph_words": 80,
        "takeaways_count": 3,
        "max_tokens": 400,
    },
    "Standard": {
        "headline_words": 20,
        "paragraph_words": 150,
        "takeaways_count": 5,
        "max_tokens": 700,
    },
    "Detailed": {
        "headline_words": 25,
        "paragraph_words": 250,
        "takeaways_count": 7,
        "max_tokens": 1100,
    },
}


def summarize_article(
    article: str,
    mode: str = "Standard",
    language: str = "English",
) -> dict:
    """
    Summarize a news article with headline, paragraph summary, and key takeaways.

    Returns dict with keys: headline, paragraph, takeaways (list[str]).
    """
    client = get_groq_client()
    cfg = MODE_CONFIGS.get(mode, MODE_CONFIGS["Standard"])
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["English"])

    prompt = f"""{lang_instruction}

You are an expert news analyst. Summarize the article below.

Return ONLY this exact structure — no extra commentary:

HEADLINE: <compelling headline, max {cfg['headline_words']} words>
PARAGRAPH: <summary paragraph, approximately {cfg['paragraph_words']} words>
TAKEAWAYS:
- <takeaway 1>
- <takeaway 2>
- <takeaway 3>
{"- <takeaway 4>" if cfg['takeaways_count'] >= 4 else ""}
{"- <takeaway 5>" if cfg['takeaways_count'] >= 5 else ""}
{"- <takeaway 6>" if cfg['takeaways_count'] >= 6 else ""}
{"- <takeaway 7>" if cfg['takeaways_count'] >= 7 else ""}

Article:
{article[:5000]}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.25,
            max_tokens=cfg["max_tokens"],
        )
        raw = completion.choices[0].message.content.strip()
        return _parse_summary_response(raw)

    except Exception as e:
        return {
            "headline": "Summarization failed",
            "paragraph": f"Error: {str(e)[:200]}",
            "takeaways": ["Please check your API key and try again."],
        }


def _parse_summary_response(raw: str) -> dict:
    """Parse structured LLM response into headline, paragraph, takeaways."""
    result = {"headline": "", "paragraph": "", "takeaways": []}
    lines = raw.splitlines()
    mode = None

    paragraph_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.upper().startswith("HEADLINE:"):
            result["headline"] = stripped.split(":", 1)[-1].strip()
            mode = None

        elif stripped.upper().startswith("PARAGRAPH:"):
            content = stripped.split(":", 1)[-1].strip()
            if content:
                paragraph_lines.append(content)
            mode = "paragraph"

        elif stripped.upper().startswith("TAKEAWAYS:"):
            if paragraph_lines:
                result["paragraph"] = " ".join(paragraph_lines)
                paragraph_lines = []
            mode = "takeaways"

        elif mode == "paragraph":
            paragraph_lines.append(stripped)

        elif mode == "takeaways" and stripped.startswith("-"):
            takeaway = stripped.lstrip("- ").strip()
            if takeaway:
                result["takeaways"].append(takeaway)

    if paragraph_lines and not result["paragraph"]:
        result["paragraph"] = " ".join(paragraph_lines)

    # Fallbacks
    if not result["headline"]:
        result["headline"] = "Summary Generated"
    if not result["paragraph"]:
        result["paragraph"] = raw[:400]
    if not result["takeaways"]:
        result["takeaways"] = ["See paragraph summary above."]

    return result