"""RSS feed monitoring."""

import feedparser
import logging
from concurrent.futures import ThreadPoolExecutor
import asyncio

logger = logging.getLogger(__name__)


def _fetch_feed(url: str) -> tuple[str, list[dict]]:
    """Fetch single RSS feed (sync function for thread pool)."""
    entries = []

    try:
        logger.info(f"Fetching RSS from {url}")
        feed = feedparser.parse(url)

        if feed.get("bozo"):
            logger.warning(f"Feed parsing issue for {url}: {feed.bozo_exception}")

        for entry in feed.entries[:15]:  # Get latest 15 entries per feed
            entries.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "source": "rss",
                "source_url": url,
            })
    except Exception as e:
        logger.error(f"Error fetching RSS from {url}: {e}")

    return url, entries


async def monitor_rss_feeds(rss_urls: list[str]) -> list[dict]:
    """
    Monitor RSS feeds and return new entries.

    Args:
        rss_urls: List of RSS feed URLs

    Returns:
        List of entries with title, link, published date
    """
    if not rss_urls:
        return []

    entries = []

    # Use thread pool for concurrent feed fetching
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [
            loop.run_in_executor(executor, _fetch_feed, url)
            for url in rss_urls
        ]
        results = await asyncio.gather(*tasks)

    for url, feed_entries in results:
        entries.extend(feed_entries)

    logger.info(f"RSS feeds: fetched {len(entries)} entries from {len(rss_urls)} feeds")
    return entries
