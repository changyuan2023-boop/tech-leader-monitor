"""Web article content extraction."""

import logging
import trafilatura

logger = logging.getLogger(__name__)


async def fetch_web_content(url: str) -> dict | None:
    """
    Extract article content from a web URL.

    Args:
        url: URL to fetch

    Returns:
        Dict with title, content, or None if extraction fails
    """
    try:
        logger.info(f"Fetching web content from {url}")
        downloaded = trafilatura.fetch_url(url)

        if downloaded is None:
            logger.warning(f"Failed to download {url}")
            return None

        # Extract main text content
        content = trafilatura.extract(
            downloaded,
            include_comments=False,
            favor_precision=True,
        )

        if content is None:
            logger.warning(f"Failed to extract content from {url}")
            return None

        # Try to get title
        extracted_content = trafilatura.extract(downloaded, output_format="python")
        title = extracted_content.get("title", "") if extracted_content else ""

        return {
            "url": url,
            "title": title,
            "content": content,
            "source_type": "web",
        }

    except Exception as e:
        logger.error(f"Error fetching web content from {url}: {e}")
        return None
