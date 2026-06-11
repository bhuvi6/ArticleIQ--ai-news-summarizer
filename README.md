# 🧠 ArticleIQ — AI-Powered News Article Summarizer

> **Multilingual news summarization platform built with Streamlit · Groq · Llama 3.3 70B**

**ArticleIQ** transforms lengthy news articles into fast, factual, multilingual summaries — so you stay informed without reading everything. Paste any article or drop a URL to instantly get headline summaries, paragraph briefs, key takeaways, AI insights, and factual accuracy analysis.

🔗 **Live Demo:** [articleiq-ai-news.streamlit.app](https://articleiq-ai-news.streamlit.app/)
📦 **GitHub:** [github.com/Bhuvi-123/articleiq-ai-news-summarizer](https://github.com/Bhuvi-123/articleiq-ai-news-summarizer)

---

## ✨ Features

### 📰 Multi-Level Summarization
Three structured summary layers for every article:
- **Headline Summary** — One-line instant understanding
- **Paragraph Summary** — Concise, factual overview
- **Key Takeaways** — Most important points in bullet form

---

### ⚡ Summary Modes

| Mode | Description |
|------|-------------|
| ⚡ Quick | Short summary + 3 concise takeaways |
| 📄 Standard | Balanced summary + 5 takeaways |
| 🔍 Detailed | In-depth explanation + 7 deep takeaways |

---

### 🌍 Multilingual Support
Generate summaries in:

| Language | |
|----------|-|
| 🇬🇧 English | 🇮🇳 Telugu |
| 🇮🇳 Hindi | 🇮🇳 Tamil |
| 🇫🇷 French | |

All translations preserve **names, dates, numbers, facts, and original meaning**.

---

### 🔗 URL-Based Article Fetching
Skip the copy-paste. Just drop a URL:
```
https://newswebsite.com/article
```
ArticleIQ will automatically fetch the page, extract readable text, and generate a summary.

---

### 🧠 AI Article Insights
Get deeper intelligence beyond the summary:

- **Tone Detection** — Informative / Serious / Casual / Analytical
- **Sentiment Analysis** — Positive / Neutral / Negative
- **Complexity Level** — Beginner / Intermediate / Advanced
- **Target Audience** — Students / Researchers / Professionals / General Readers

---

### 📊 Accuracy Score
Verifies that summaries stay true to the original article by checking:
- Numbers & statistics
- Dates
- Named entities

> Example: **Accuracy Score: 92%** with a detailed breakdown

---

### 📋 One-Click Copy
Copy your **Headline Summary**, **Paragraph Summary**, or **Key Takeaways** to clipboard with a single button.

---

### 📄 PDF Export
Download a complete summary report as a PDF, including:
- Summary content
- Key takeaways
- Article metadata
- AI insights
- Accuracy score

---

### 🕘 Summary History
Previously generated summaries are saved in the sidebar — reload any of them instantly without re-summarizing.

---

### 🎨 Professional UI
Clean, modern interface featuring:
- White + green design system
- Premium card layout
- Metadata dashboard
- AI insights panel
- Responsive, readable typography

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit + Custom CSS |
| Backend | Python |
| AI Model | Groq API — Llama 3.3 70B Versatile |
| PDF Generation | ReportLab |
| Web Scraping | Requests + BeautifulSoup4 |

---

## 📂 Project Structure

```
ArticleIQ/
├── app.py
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── summarization_rules.json
└── utils/
    ├── summarizer.py
    ├── metadata.py
    ├── article_insights.py
    ├── accuracy_checker.py
    ├── history_manager.py
    └── pdf_export.py
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Bhuvi-123/articleiq-ai-news-summarizer.git
cd articleiq-ai-news-summarizer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
pip install reportlab
```

### 3. Add Your API Key
Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_api_key_here
```

### 4. Run the App
```bash
streamlit run app.py
```
The app will open automatically in your browser.

---

## 👨‍💻 Team

| Name | Role |
|------|------|
| V. Prasanna | Prompt Engineering |
| A. Kedareswara Rao | Data & Rules |
| V. Bhuvaneswari | Backend / API Integration |
| K. Sai Tejesh | Testing & Deployment |
| S. Veera Mallesh | UI / Frontend |

---

## 🔮 Roadmap

- [ ] 🎙 Voice Summary
- [ ] 🌙 Dark Mode
- [ ] 📰 Multi-Article Comparison
- [ ] 🛡 Fake News Risk Detection
- [ ] 📈 Trending Topics Dashboard
- [ ] 🔍 Bias Detection

---

## 💡 Why ArticleIQ?

News is overwhelming. ArticleIQ cuts through the noise — giving you the facts, fast, in your language. Whether you're a student, researcher, professional, or casual reader, ArticleIQ helps you stay informed without spending hours reading full articles.

---

## ⭐ Support the Project

If you found this useful, drop a ⭐ on [GitHub](https://github.com/Bhuvi-123/articleiq-ai-news-summarizer) — it really helps!