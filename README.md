🔗 **Live Demo:** [articleiq-ai-news.streamlit.app](https://articleiq-ai-news.streamlit.app/)
📦 **GitHub:** [github.com/Bhuvi-123/articleiq-ai-news-summarizer](https://github.com/Bhuvi-123/articleiq-ai-news-summarizer)

---

# ArticleIQ — AI Research Intelligence Platform

> **Transform news into intelligence.** Premium multilingual article analysis powered by Groq + Llama 3.3 70B.

---

## What It Does

ArticleIQ is a market-level AI research tool that goes far beyond summarization:

| Feature | Description |
|---|---|
| **Single Article Analysis** | Summarize any article with headline, paragraph, and key takeaways |
| **Multi-Source Intelligence** | Compare 2–5 sources — detect agreements, contradictions, and coverage gaps |
| **AI Accuracy Validation** | Second LLM pass compares summary vs original for factual fidelity |
| **Source Credibility Engine** | Domain reputation scoring with AI fallback for unknown sources |
| **Why This Matters** | Real-world impact analysis across economy, jobs, business, etc. |
| **Topic Intelligence Feed** | Live RSS-based news feed for any topic, auto-curated |
| **Multilingual Summaries** | English, Telugu, Hindi, Tamil, French |
| **PDF Export** | Branded professional report with all insights |
| **Personal Dashboard** | Session stats and recent summary history |

---

## Project Structure

```
articleiq/
├── app.py                        # Main Streamlit application
├── requirements.txt              # All Python dependencies
├── .env.example                  # Environment variable template
├── .gitignore
├── .streamlit/
│   ├── config.toml               # Streamlit theme + server config
│   └── secrets.toml              # API keys (local dev — DO NOT commit)
└── utils/
    ├── __init__.py
    ├── ai_insights.py            # Tone, sentiment, complexity, "Why This Matters"
    ├── summarizer.py             # Core summarization engine (all modes/languages)
    ├── accuracy_validator.py     # AI-powered factual accuracy check
    ├── credibility.py            # Source credibility scoring
    ├── fetcher.py                # URL article fetcher (BeautifulSoup)
    ├── multi_article.py          # Multi-source intelligence analysis
    ├── pdf_export.py             # PDF report generation (ReportLab)
    └── rss_monitor.py            # Topic feed via Google News RSS
```

---

## Local Setup

### 1. Clone / download the project

```bash
git clone https://github.com/your-username/articleiq.git
cd articleiq
```

### 2. Create virtual environment

```bash
python -m venv venv

# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

```bash
cp .env.example .env
```

Open `.env` and add your Groq API key:

```env
GROQ_API_KEY=your-groq-api-key-here
```

Get a free Groq API key at: https://console.groq.com/keys

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Streamlit Cloud Deployment

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial ArticleIQ deployment"
git remote add origin https://github.com/your-username/articleiq.git
git push -u origin main
```

**Important:** Make sure `.gitignore` is in place so `.env` and `secrets.toml` are not committed.

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select your repository and branch
4. Set **Main file path** to `app.py`
5. Click **Deploy**

### 3. Configure Secrets

1. In your deployed app, click **Settings → Secrets**
2. Add:

```toml
GROQ_API_KEY = "your-groq-api-key-here"
```

3. Click **Save** — the app will restart automatically.

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Groq API key for LLM calls |

---

## Feature Guide

### Single Article Mode
- Paste a URL or raw article text
- Choose **Summary Mode**: Quick (fast), Standard (balanced), Detailed (comprehensive)
- Choose **Language**: English, Telugu, Hindi, Tamil, French
- Toggle optional analysis in the sidebar: Accuracy Validation, Credibility Score, Why This Matters
- Download a professional PDF report

### Multi-Source Intelligence
- Enter 2–5 article URLs on the same story
- ArticleIQ fetches all articles, then runs a cross-source analysis
- Results: Unified Summary, Agreement Points, Contradiction Analysis, Sentiment per Source, Coverage Gaps, Source Breakdown
- Each source also gets its own individual summary

### Topic Feed
- Enter any topic (e.g. "AI regulation", "Tesla", "RBI policy")
- Get the latest news via Google News RSS
- Click "Open" to read the full article, or copy the URL into Single Article mode

### Dashboard
- Session stats: total articles analyzed, preferred mode, top language
- Recent summary history for this session

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Streamlit |
| LLM | Llama 3.3 70B via Groq API |
| Scraping | Requests + BeautifulSoup4 |
| PDF | ReportLab |
| News Feed | Google News RSS |
| Secrets | Streamlit Secrets / python-dotenv |

---

## Notes

- Multi-article analysis may take 30–60 seconds depending on article length and Groq response time.
- URL fetching works for most public news sites. Paywalled or JS-heavy sites may not extract correctly — use "Paste Article Text" as fallback.
- All analysis is AI-generated and intended for research and informational purposes only. Always verify critical claims with primary sources.

---

*ArticleIQ — AI Research Intelligence Platform*