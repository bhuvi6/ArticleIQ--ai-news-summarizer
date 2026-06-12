"""
ArticleIQ — AI Insights Engine
Groq-powered article analysis: tone, sentiment, complexity, audience.
"""

from groq import Groq
import os


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set in environment or secrets.")
    return Groq(api_key=api_key)


def generate_article_insights(article: str) -> dict:
    """
    Analyse tone, sentiment, complexity, and target audience of an article.
    Returns a dict with keys: tone, sentiment, complexity, audience.
    """
    client = get_groq_client()

    prompt = f"""Analyze this news article carefully.

Return ONLY this exact format with no extra text:

Tone: <one word>
Sentiment: <Positive/Neutral/Negative>
Complexity: <Beginner/Intermediate/Advanced>
Target Audience: <short answer, max 8 words>

Article:
{article[:4000]}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=120,
        )
        response = completion.choices[0].message.content.strip()

        insights = {
            "tone": "Unknown",
            "sentiment": "Unknown",
            "complexity": "Unknown",
            "audience": "Unknown",
        }

        for line in response.splitlines():
            line = line.strip()
            if line.startswith("Tone:"):
                insights["tone"] = line.replace("Tone:", "").strip()
            elif line.startswith("Sentiment:"):
                insights["sentiment"] = line.replace("Sentiment:", "").strip()
            elif line.startswith("Complexity:"):
                insights["complexity"] = line.replace("Complexity:", "").strip()
            elif line.startswith("Target Audience:"):
                insights["audience"] = line.replace("Target Audience:", "").strip()

        return insights

    except Exception as e:
        return {
            "tone": "Unavailable",
            "sentiment": "Unavailable",
            "complexity": "Unavailable",
            "audience": f"Error: {str(e)[:80]}",
        }


def generate_why_this_matters(article: str, summary: str) -> str:
    """
    Generate a 'Why This Matters' section explaining real-world impact.
    Returns markdown-formatted text.
    """
    client = get_groq_client()

    prompt = f"""You are a senior policy analyst. Based on this news article and its summary, write a concise "Why This Matters" section.

Explain real-world impact across relevant domains from: jobs, economy, education, business, startups, consumers, technology, geopolitics, healthcare.

Format:
- Use 3–5 short, punchy bullet points.
- Each bullet starts with a bold domain label, e.g. **Economy:**
- Be specific and insightful. Avoid generic statements.
- Total response: under 180 words.

Article Summary:
{summary[:2000]}

Original Article (excerpt):
{article[:1500]}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Unable to generate impact analysis: {str(e)[:120]}"
