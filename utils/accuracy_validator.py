"""
ArticleIQ — AI Accuracy Validation Engine
Second Groq pass: compares original article vs generated summary for factual fidelity.
"""

from groq import Groq
import os
import re


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set in environment or secrets.")
    return Groq(api_key=api_key)


def validate_summary_accuracy(original_article: str, generated_summary: str) -> dict:
    """
    Use a second Groq LLM call to evaluate factual accuracy of the summary
    against the original article.

    Returns dict with keys:
        score (int 0–100), confidence (str), explanation (str),
        hallucination_risk (str), missing_info (list[str])
    """
    client = get_groq_client()

    prompt = f"""You are an expert fact-checker and AI evaluator.

Compare the ORIGINAL ARTICLE with the GENERATED SUMMARY below.

Evaluate on these dimensions:
1. Factual preservation — are the core facts correctly represented?
2. Numbers & dates — are all specific figures preserved accurately?
3. Named entities — are people, organizations, and places correctly named?
4. Hallucination risk — does the summary introduce facts NOT in the article?
5. Missing information — what important facts from the article are absent?

Return ONLY this exact format:

SCORE: <integer 0-100>
CONFIDENCE: <High/Medium/Low>
HALLUCINATION_RISK: <None/Low/Medium/High>
EXPLANATION: <2-3 sentences explaining the score>
MISSING:
- <missing item 1, or "None" if nothing important is missing>
- <missing item 2>
- <missing item 3>

ORIGINAL ARTICLE (excerpt):
{original_article[:3000]}

GENERATED SUMMARY:
{generated_summary[:1500]}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500,
        )
        raw = completion.choices[0].message.content.strip()
        return _parse_accuracy_response(raw)

    except Exception as e:
        return {
            "score": 0,
            "confidence": "Error",
            "hallucination_risk": "Unknown",
            "explanation": f"Validation unavailable: {str(e)[:150]}",
            "missing_info": [],
        }


def _parse_accuracy_response(raw: str) -> dict:
    """Parse structured accuracy evaluation from LLM output."""
    result = {
        "score": 75,
        "confidence": "Medium",
        "hallucination_risk": "Low",
        "explanation": "",
        "missing_info": [],
    }

    lines = raw.splitlines()
    mode = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.upper().startswith("SCORE:"):
            raw_score = stripped.split(":", 1)[-1].strip()
            digits = re.sub(r"[^\d]", "", raw_score)
            if digits:
                result["score"] = max(0, min(100, int(digits)))

        elif stripped.upper().startswith("CONFIDENCE:"):
            result["confidence"] = stripped.split(":", 1)[-1].strip()

        elif stripped.upper().startswith("HALLUCINATION_RISK:"):
            result["hallucination_risk"] = stripped.split(":", 1)[-1].strip()

        elif stripped.upper().startswith("EXPLANATION:"):
            result["explanation"] = stripped.split(":", 1)[-1].strip()
            mode = "explanation"

        elif stripped.upper().startswith("MISSING:"):
            mode = "missing"

        elif mode == "explanation" and not stripped.startswith("-"):
            if result["explanation"]:
                result["explanation"] += " " + stripped
            else:
                result["explanation"] = stripped

        elif mode == "missing" and stripped.startswith("-"):
            item = stripped.lstrip("- ").strip()
            if item and item.lower() != "none":
                result["missing_info"].append(item)

    return result
