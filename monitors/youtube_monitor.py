"""YouTube channel monitoring."""

import logging
import os
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)


async def monitor_youtube_channels(channel_names: list[str]) -> list[dict]:
    """
    Monitor YouTube channels for new videos.

    Args:
        channel_names: List of channel names/IDs to monitor

    Returns:
        List of video entries with title, link, published date
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logger.warning("YOUTUBE_API_KEY not set, skipping YouTube monitoring")
        return []

    youtube = build("youtube", "v3", developerKey=api_key)
    entries = []

    for channel_name in channel_names:
        try:
            # TODO: Implement channel search and video retrieval
            # 1. Search for channel by name
            # 2. Get uploads playlist
            # 3. Fetch latest videos
            pass
        except Exception as e:
            logger.error(f"Error fetching YouTube channel {channel_name}: {e}")

    return entries
