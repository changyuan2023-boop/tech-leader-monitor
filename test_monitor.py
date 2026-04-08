#!/usr/bin/env python
"""Test monitor locally without GitHub Actions."""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from monitors.rss_monitor import monitor_rss_feeds
from monitors.google_news import monitor_google_news

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_rss_feeds():
    """Test RSS feed monitoring."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing RSS Feeds")
    logger.info("=" * 60)

    # Test with a few real feeds
    test_urls = [
        "https://xai.com/feed",
        "https://blogs.nvidia.com/feed",
    ]

    for url in test_urls:
        logger.info(f"\nTesting: {url}")
        entries = await monitor_rss_feeds([url])
        logger.info(f"  Found {len(entries)} entries")

        if entries:
            entry = entries[0]
            logger.info(f"  Sample: {entry.get('title', 'N/A')[:80]}")


async def test_google_news():
    """Test Google News monitoring."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Google News")
    logger.info("=" * 60)

    test_queries = [
        ("Jensen Huang", "interview OR speech OR podcast"),
        ("Sam Altman", "interview OR speech"),
    ]

    for person, query in test_queries:
        logger.info(f"\nTesting: {person}")
        entries = await monitor_google_news(person, query)
        logger.info(f"  Found {len(entries)} entries")

        if entries:
            entry = entries[0]
            logger.info(f"  Sample: {entry.get('title', 'N/A')[:80]}")


async def main():
    """Run tests."""
    logger.info("Starting monitoring tests...")

    try:
        await test_rss_feeds()
        await test_google_news()

        logger.info("\n" + "=" * 60)
        logger.info("Tests completed successfully!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
