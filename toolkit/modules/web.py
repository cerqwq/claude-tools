"""Web Knowledge - Search, scrape, and fetch web content."""

import re
import json

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_WEB = True
except ImportError:
    HAS_WEB = False

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def fetch(url, timeout=15):
    """Fetch a URL and return text content."""
    if not HAS_WEB:
        return None, "requests not installed"
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.text, None
    except Exception as e:
        return None, str(e)


def fetch_json(url, timeout=15):
    """Fetch a JSON API endpoint."""
    if not HAS_WEB:
        return None, "requests not installed"
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)


def scrape_text(url, selector=None):
    """Scrape text from a webpage. Optionally filter by CSS selector."""
    if not HAS_WEB:
        return None, "requests/bs4 not installed"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Remove scripts and styles
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        if selector:
            elements = soup.select(selector)
            text = "\n".join(el.get_text(strip=True) for el in elements)
        else:
            text = soup.get_text(separator="\n", strip=True)

        return text[:10000], None  # Cap at 10k chars
    except Exception as e:
        return None, str(e)


def scrape_links(url):
    """Extract all links from a page."""
    if not HAS_WEB:
        return None, "requests/bs4 not installed"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            links.append({"text": a.get_text(strip=True), "href": a["href"]})
        return links, None
    except Exception as e:
        return None, str(e)


def search_ddg(query, num_results=5):
    """Search via DuckDuckGo HTML (no API key needed)."""
    if not HAS_WEB:
        return None, "requests not installed"
    try:
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        results = []
        for result in soup.select(".result__body")[:num_results]:
            title_el = result.select_one(".result__title a")
            snippet_el = result.select_one(".result__snippet")
            if title_el:
                results.append({
                    "title": title_el.get_text(strip=True),
                    "url": title_el.get("href", ""),
                    "snippet": snippet_el.get_text(strip=True) if snippet_el else ""
                })
        return results, None
    except Exception as e:
        return None, str(e)


def fetch_js_page(url, wait_ms=3000):
    """Fetch a JS-rendered page using Playwright."""
    if not HAS_PLAYWRIGHT:
        return None, "Playwright not installed"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(wait_ms)
            content = page.content()
            browser.close()

            soup = BeautifulSoup(content, "html.parser")
            for tag in soup(["script", "style"]):
                tag.decompose()
            return soup.get_text(separator="\n", strip=True)[:10000], None
    except Exception as e:
        return None, str(e)
