"""Main monitor entry point."""

import asyncio
import logging
import sys
from pathlib import Path
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from monitors.rss_monitor import monitor_rss_feeds
from monitors.google_news import monitor_google_news
from classifier import classify_relevance
from dedup import is_duplicate, save_seen_url
from notifier import send_slack_notification

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config/people.yaml") -> dict:
    """Load people configuration."""
    try:
        with open(config_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {"people": []}


async def monitor_person(person_config: dict) -> list[dict]:
    """Monitor a single person across all sources."""
    person_name = person_config["name"]
    sources = person_config["sources"]
    entries = []

    logger.info(f"Monitoring {person_name}...")

    # RSS feeds
    if "rss" in sources:
        logger.info(f"  → Checking {len(sources['rss'])} RSS feeds")
        rss_entries = await monitor_rss_feeds(sources["rss"])
        for entry in rss_entries:
            entry["person"] = person_name
        entries.extend(rss_entries)

    # Google News
    if "google_news_query" in sources:
        logger.info(f"  → Checking Google News")
        news_entries = await monitor_google_news(
            person_name,
            sources["google_news_query"]
        )
        entries.extend(news_entries)

    # TODO: YouTube monitoring (Step 3)

    return entries


async def process_entries(entries: list[dict]) -> int:
    """
    Filter, deduplicate, classify, and notify about entries.

    Returns:
        Number of new relevant entries processed
    """
    processed = 0

    for entry in entries:
        url = entry.get("link") or entry.get("url")
        if not url:
            logger.warning(f"Entry has no URL: {entry.get('title')}")
            continue

        # Check for duplicates
        if is_duplicate(url):
            logger.info(f"Duplicate: {entry.get('title', url)[:50]}")
            continue

        person_name = entry.get("person", "Unknown")
        title = entry.get("title", "")
        summary = entry.get("summary", "")

        logger.info(f"Classifying: {title[:60]}...")

        # Classify relevance with Haiku
        classification = await classify_relevance(person_name, title, summary)

        if not classification.get("is_relevant", False):
            logger.info(f"  ✗ Not relevant: {classification.get('reason', 'unknown')}")
            # Still mark as seen to avoid re-processing
            save_seen_url(url)
            continue

        logger.info(f"  ✓ Relevant: {classification.get('reason', 'relevant')}")

        # Determine content type
        content_type = "Article"
        if entry.get("source") == "youtube":
            content_type = "Video"
        elif "interview" in title.lower():
            content_type = "Interview"
        elif "speech" in title.lower():
            content_type = "Speech"

        # Send Slack notification
        source = entry.get("source", "unknown")
        await send_slack_notification(
            person_name=person_name,
            content_type=content_type,
            title=title,
            url=url,
            source=source,
        )

        # Mark as seen
        save_seen_url(url)
        processed += 1

    return processed


async def main():
    """Run monitoring workflow."""
    logger.info("=" * 60)
    logger.info("Starting content monitoring...")
    logger.info("=" * 60)

    # Load config
    config = load_config()
    people = config.get("people", [])

    if not people:
        logger.error("No people configured")
        return False

    # Monitor each person
    all_entries = []
    for person_config in people:
        try:
            entries = await monitor_person(person_config)
            all_entries.extend(entries)
        except Exception as e:
            logger.error(f"Error monitoring {person_config.get('name')}: {e}")
            continue

    logger.info(f"Found {len(all_entries)} total entries")

    # Process entries (filter, classify, deduplicate, notify)
    processed = await process_entries(all_entries)

    logger.info("=" * 60)
    logger.info(f"Monitoring completed: {processed} new entries processed")
    logger.info("=" * 60)

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
