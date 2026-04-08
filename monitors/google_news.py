"""Google News RSS monitoring."""

import feedparser
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)

GOOGLE_NEWS_BASE = "https://news.google.com/rss/search"


async def monitor_google_news(person_name: str, query_suffix: str) -> list[dict]:
    """
    Monitor Google News RSS for a person.

    Args:
        person_name: Target person name
        query_suffix: Query string (e.g., 'interview OR speech OR podcast OR opinion')

    Returns:
        List of news entries
    """
    # Build query URL
    query = f'"{person_name}" {query_suffix}'
    encoded_query = quote(query)
    url = f"{GOOGLE_NEWS_BASE}?q={encoded_query}&hl=en"

    entries = []

    try:
        logger.info(f"Fetching Google News for {person_name}")
        feed = feedparser.parse(url)

        if feed.get("bozo"):
            logger.warning(f"Feed parsing issue for {person_name}: {feed.bozo_exception}")

        for entry in feed.entries[:25]:  # Get latest 25 entries
            entries.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "source": "google_news",
                "person": person_name,
            })

        logger.info(f"Google News: {len(entries)} entries for {person_name}")

    except Exception as e:
        logger.error(f"Error fetching Google News for {person_name}: {e}")

    return entries
