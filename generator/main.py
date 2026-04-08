"""Generate article from URL via workflow_dispatch."""

import asyncio
import logging
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fetchers.web_fetcher import fetch_web_content
from fetchers.youtube_fetcher import fetch_youtube_transcript
from generator import generate_article
from notifier import send_slack_notification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Generate article from provided URL."""
    url = os.getenv("CONTENT_URL")

    if not url:
        logger.error("CONTENT_URL environment variable not set")
        return False

    logger.info(f"Generating article from: {url}")

    # Fetch content
    content = None
    if "youtube.com" in url or "youtu.be" in url:
        content = await fetch_youtube_transcript(url)
    else:
        content = await fetch_web_content(url)

    if not content:
        logger.error(f"Failed to fetch content from {url}")
        # Send error notification
        await send_slack_notification(
            person_name="Unknown",
            content_type="Error",
            title=f"Failed to fetch content: {url}",
            url=url,
            source="generator",
        )
        return False

    # TODO: Detect person name from content or URL
    person_name = "TBD"

    # Generate article
    article = await generate_article(
        person_name=person_name,
        source_content=content.get("content", ""),
        source_url=url,
    )

    if not article:
        logger.error("Failed to generate article")
        return False

    # Save article
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    article_path = output_dir / "article.md"

    with open(article_path, "w") as f:
        f.write(article)

    logger.info(f"Article saved to {article_path}")

    # Send Slack notification with draft
    await send_slack_notification(
        person_name=person_name,
        content_type="Generated Draft",
        title=f"Article draft ready for review",
        url=str(article_path),
        source="generator",
    )

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
