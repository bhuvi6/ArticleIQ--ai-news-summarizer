"""
ArticleIQ — Topic Intelligence Feed
Fetches latest news via RSS/web for user-specified topics and auto-summarizes.
"""

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re
from urllib.parse import quote_plus


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ArticleIQ/1.0; +https://articleiq.app)"
    )
}

# RSS sources by topic fallback
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"


def fetch_topic_news(topic: str, max_articles: int = 5) -> list[dict]:
    """
    Fetch latest news articles for a given topic using Google News RSS.

    Returns list of dicts with: title, url, published, source, snippet
    """
    if not topic or not topic.strip():
        return []

    topic = topic.strip()
    encoded = quote_plus(topic)
    feed_url = GOOGLE_NEWS_RSS.format(query=encoded)

    try:
        response = requests.get(feed_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        articles = _parse_rss(response.text)
        return articles[:max_articles]
    except Exception as e:
        return [{"error": str(e), "title": f"Failed to fetch news for '{topic}'", "url": "", "published": "", "source": "", "snippet": ""}]


def _parse_rss(xml_text: str) -> list[dict]:
    """Parse RSS XML and extract article metadata."""
    articles = []
    try:
        root = ET.fromstring(xml_text)
        channel = root.find("channel")
        if channel is None:
            return []

        for item in channel.findall("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            pub_el = item.find("pubDate")
            desc_el = item.find("description")
            source_el = item.find("source")

            title = title_el.text.strip() if title_el is not None and title_el.text else "No title"
            url = link_el.text.strip() if link_el is not None and link_el.text else ""
            published = pub_el.text.strip() if pub_el is not None and pub_el.text else ""
            source = source_el.text.strip() if source_el is not None and source_el.text else _extract_source(title)
            snippet = _clean_html(desc_el.text or "") if desc_el is not None else ""

            # Clean Google News source from title
            title = _clean_google_title(title)

            if url:
                articles.append({
                    "title": title,
                    "url": url,
                    "published": _format_date(published),
                    "source": source,
                    "snippet": snippet[:200],
                    "error": None,
                })
    except ET.ParseError:
        pass

    return articles


def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def _clean_google_title(title: str) -> str:
    # Google News appends " - Source Name" to titles
    return re.sub(r"\s-\s[^-]+$", "", title).strip()


def _extract_source(title: str) -> str:
    match = re.search(r"\s-\s([^-]+)$", title)
    return match.group(1).strip() if match else "Unknown"


def _format_date(raw: str) -> str:
    """Simplify RSS date strings."""
    try:
        from datetime import datetime
        # RFC 822 format: Mon, 01 Jan 2024 12:00:00 +0000
        dt = datetime.strptime(raw[:25].strip(), "%a, %d %b %Y %H:%M:%S")
        return dt.strftime("%b %d, %Y %H:%M")
    except Exception:
        return raw[:20] if raw else "Unknown date"
