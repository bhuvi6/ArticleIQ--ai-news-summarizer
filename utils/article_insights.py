
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Groq Client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_article_insights(article):

    prompt = f"""
    Analyze this news article.

    Return ONLY this format:

    Tone: <one word>
    Sentiment: <Positive/Neutral/Negative>
    Complexity: <Beginner/Intermediate/Advanced>
    Target Audience: <short answer>

    Article:
    {article}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        response = completion.choices[0].message.content

        insights = {
            "tone": "Unknown",
            "sentiment": "Unknown",
            "complexity": "Unknown",
            "audience": "Unknown"
        }

        for line in response.splitlines():

            if "Tone:" in line:
                insights["tone"] = line.replace(
                    "Tone:", ""
                ).strip()

            elif "Sentiment:" in line:
                insights["sentiment"] = line.replace(
                    "Sentiment:", ""
                ).strip()

            elif "Complexity:" in line:
                insights["complexity"] = line.replace(
                    "Complexity:", ""
                ).strip()

            elif "Target Audience:" in line:
                insights["audience"] = line.replace(
                    "Target Audience:", ""
                ).strip()

        return insights

    except Exception as e:
        return {
            "tone": "Error",
            "sentiment": "Error",
            "complexity": "Error",
            "audience": str(e)
        }

