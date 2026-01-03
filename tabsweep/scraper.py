"""Web scraping utilities for extracting page metadata."""

import httpx
from bs4 import BeautifulSoup


def scrape_metadata(url: str, timeout: int = 5) -> tuple[str | None, str | None]:
    """
    Scrape title and meta description from a URL.

    Args:
        url: The URL to scrape
        timeout: Request timeout in seconds

    Returns:
        (title, description) or (None, None) if scraping fails
    """
    try:
        response = httpx.get(
            url,
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; TabSweep/0.1)"}
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Extract title
        title = None
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text().strip()

        # Extract meta description
        description = None
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc.get("content").strip()

        return title, description

    except (httpx.HTTPError, httpx.TimeoutException, Exception):
        # Return None for any failure (403, timeout, SSL errors, etc.)
        return None, None
