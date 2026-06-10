from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def load_rules():
    with open("summarization_rules.json", "r") as file:
        return json.load(file)


def generate_summary(article: str, language: str) -> str:
    """
    Generate multilingual article summary using Groq.
    `language` may contain mode instructions appended after a newline.
    """
    rules = load_rules()

    # Split language from any appended mode hint
    parts = language.split("\n\n", 1)
    lang_name    = parts[0].strip()
    mode_hint    = parts[1].strip() if len(parts) > 1 else ""

    prompt = f"""
You are an AI News Article Summarizer.

Follow these strict rules:

ACCURACY RULES:
{rules["summarization_rules"]["accuracy_rules"]}

TONE RULES:
{rules["summarization_rules"]["tone_rules"]}

CONTENT RULES:
{rules["summarization_rules"]["content_rules"]}

OUTPUT LANGUAGE:
Generate the entire summary in this language: {lang_name}
Translate naturally while preserving facts, dates, names, and numbers.
Do NOT mistranslate proper nouns.

SUMMARY MODE INSTRUCTIONS:
{mode_hint if mode_hint else "Standard mode: 3-4 sentence paragraph. Exactly 5 bullet takeaways."}

Output Format (use these EXACT section headers):

1. One-Line Summary:
<headline here>

2. One-Paragraph Summary:
<paragraph here>

3. Key Takeaways:
- <point 1>
- <point 2>
- <point 3>
(continue per mode instructions)

Article:
{article}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"