"""
ArticleIQ — Article Fetcher
Fetches and extracts clean article text from URLs using BeautifulSoup.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT = 12  # seconds


def fetch_article(url: str) -> dict:
    """
    Fetch and clean article content from a URL.

    Returns dict with:
        success (bool), content (str), title (str), url (str), error (str or None)
    """
    if not url or not url.startswith("http"):
        return _fail(url, "Invalid URL. Must start with http:// or https://")

    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return _fail(url, "Request timed out. The website may be slow or unavailable.")
    except requests.exceptions.ConnectionError:
        return _fail(url, "Could not connect to the URL. Check the address and try again.")
    except requests.exceptions.HTTPError as e:
        return _fail(url, f"HTTP {response.status_code}: {str(e)[:100]}")
    except Exception as e:
        return _fail(url, f"Fetch error: {str(e)[:150]}")

    try:
        soup = BeautifulSoup(response.content, "html.parser")

        # Remove noise elements
        for tag in soup(["script", "style", "nav", "header", "footer",
                         "aside", "form", "iframe", "advertisement",
                         "noscript", "figure"]):
            tag.decompose()

        # Extract title
        title = ""
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
        elif soup.title:
            title = soup.title.get_text(strip=True)

        # Try article-specific containers first
        content = ""
        for selector in ["article", "main", ".article-body", ".story-body",
                          ".post-content", ".entry-content", ".content", "#content"]:
            container = soup.select_one(selector)
            if container:
                paragraphs = container.find_all("p")
                if paragraphs:
                    content = " ".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)
                    if len(content) > 300:
                        break

        # Fallback: all <p> tags
        if len(content) < 300:
            paragraphs = soup.find_all("p")
            content = " ".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)

        # Clean up whitespace
        content = re.sub(r"\s{2,}", " ", content).strip()

        if len(content) < 150:
            return _fail(url, "Could not extract sufficient article content. The page may require JavaScript or a login.")

        return {
            "success": True,
            "content": content,
            "title": title or _domain_from_url(url),
            "url": url,
            "word_count": len(content.split()),
            "error": None,
        }

    except Exception as e:
        return _fail(url, f"Parsing error: {str(e)[:150]}")


def fetch_multiple_articles(urls: list[str]) -> list[dict]:
    """Fetch multiple articles. Returns list of fetch result dicts."""
    results = []
    for url in urls[:5]:  # cap at 5
        url = url.strip()
        if url:
            results.append(fetch_article(url))
    return results


def _fail(url: str, reason: str) -> dict:
    return {
        "success": False,
        "content": "",
        "title": "",
        "url": url,
        "word_count": 0,
        "error": reason,
    }


def _domain_from_url(url: str) -> str:
    try:
        return urlparse(url).netloc.lstrip("www.")
    except Exception:
        return url
