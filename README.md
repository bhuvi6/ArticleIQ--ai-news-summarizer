```md
<p align="center">
  <a href="https://articleiq-ai-news.streamlit.app/">
    <img src="https://img.shields.io/badge/🚀%20Live%20Demo-ArticleIQ-success?style=for-the-badge">
  </a>
</p>
```





# 🧠 ArticleIQ — AI News Article Summarizer

> **Multilingual AI-powered news summarization platform built using Streamlit + Groq + Llama 3.3 70B**

**ArticleIQ** helps users quickly understand lengthy news articles without reading the full content. Paste an article or fetch content directly from a URL and instantly receive **headline summaries, paragraph briefs, key takeaways, AI insights, and factual accuracy analysis** in multiple languages.

---

## 🚀 Features

### 📰 Multi-Level Summarization

Generate structured summaries in **three levels**:

* **Headline Summary** → One-line quick understanding
* **Paragraph Summary** → Concise factual overview
* **Key Takeaways** → Important insights in bullet points

---

### ⚡ Real Summary Modes

Choose how detailed the summary should be:

| Mode        | Description                           |
| ----------- | ------------------------------------- |
| ⚡ Quick     | Short summary + 3 concise takeaways   |
| 📄 Standard | Balanced summary + 5 takeaways        |
| 🔍 Detailed | Richer explanation + 7 deep takeaways |

---

### 🌍 Multilingual Support

Generate summaries in:

* 🇬🇧 English
* 🇮🇳 Telugu
* 🇮🇳 Hindi
* 🇮🇳 Tamil
* 🇫🇷 French

The system preserves:

✅ Names
✅ Dates
✅ Numbers
✅ Facts
✅ Original meaning

while translating naturally.

---

### 🔗 URL-Based Article Fetching

Instead of manually copy-pasting articles:

Paste a URL like:

```txt
https://newswebsite.com/article
```

**ArticleIQ** automatically:

1. Fetches article content
2. Extracts readable text
3. Generates an AI summary instantly

---

### 🧠 AI Article Insights

Get deeper intelligence about articles:

### Tone Detection

Examples:

* Informative
* Serious
* Casual
* Analytical

### Sentiment Analysis

* Positive
* Neutral
* Negative

### Complexity Detection

* Beginner
* Intermediate
* Advanced

### Target Audience Identification

Examples:

* Students
* Researchers
* Professionals
* General Readers

---

### 📊 Accuracy Score

Ensures summaries preserve factual information.

Checks:

* Numbers
* Dates
* Named Entities

Example:

```txt
Accuracy Score: 92%
```

with detailed breakdown.

---

### 📋 Copy Summary Buttons

Instantly copy:

* Headline Summary
* Paragraph Summary
* Key Takeaways

with one click.

---

### 📄 PDF Export

Download generated summaries as PDF including:

* Summary
* Key Takeaways
* Metadata
* AI Insights
* Accuracy Score

---

### 🕘 Summary History

View and reload previously generated summaries instantly from the sidebar.

---

### 🎨 Professional UI

Modern white + green interface with:

* Premium card design
* Metadata dashboard
* AI insights section
* Responsive layout
* Clean typography

```md
## 🌐 Live Demo

Try ArticleIQ live here:

🔗 https://articleiq-ai-news.streamlit.app/
```

---

## 🛠 Tech Stack

### Frontend

* **Streamlit**
* Custom Internal CSS

### Backend

* **Python**

### AI Model

* **Groq API**
* **Llama 3.3 70B Versatile**

### Libraries Used

* `streamlit`
* `groq`
* `python-dotenv`
* `reportlab`
* `requests`
* `beautifulsoup4`

---

## 📂 Project Structure

```txt
ArticleIQ/
│── app.py
│── .env
│── .gitignore
│── requirements.txt
│── README.md
│── summarization_rules.json
│
├── utils/
│   ├── summarizer.py
│   ├── metadata.py
│   ├── article_insights.py
│   ├── accuracy_checker.py
│   ├── history_manager.py
│   └── pdf_export.py
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Bhuvi-123/articleiq-ai-news-summarizer.git
```

### 2️⃣ Move Into Project Folder

```bash
cd articleiq-ai-news-summarizer
```

### 3️⃣ Install Requirements

```bash
pip install -r requirements.txt
```

### 4️⃣ Install PDF Support

```bash
pip install reportlab
```

### 5️⃣ Add API Key

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

The application will automatically open in your browser.

---

## 📸 Screenshots

### Home Interface

*Add screenshot here*

### Generated Summary

*Add screenshot here*

### AI Insights Dashboard

*Add screenshot here*

---

## 👨‍💻 Team Members

| Name                   | Role                 |
| ---------------------- | -------------------- |
| **V. Prasanna**        | Prompt Engineering   |
| **A. Kedareswara Rao** | Data & Rules         |
| **V. Bhuvaneswari**    | Backend / API        |
| **K. Sai Tejesh**      | Testing & Deployment |
| **S. Veera Mallesh**   | UI / Frontend        |

---

## 🔮 Future Improvements

* 🎙 Voice Summary
* 🌙 Dark Mode
* 📰 Compare Multiple Articles
* 🛡 Fake News Risk Detection
* 📈 Trending Topics Dashboard
* 🔍 Bias Detection

---

## 💡 Why ArticleIQ?

**ArticleIQ** transforms lengthy, information-heavy articles into **fast, factual, multilingual summaries** — helping users consume news smarter, faster, and more efficiently.

Whether you're a student, researcher, working professional, or casual reader, ArticleIQ helps you stay informed without spending time reading entire articles.

---

## ⭐ Support the Project

If you found this project useful, consider giving it a **star ⭐ on GitHub**.
