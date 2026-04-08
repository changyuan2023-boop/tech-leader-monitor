"""YouTube transcript extraction."""

import logging
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

logger = logging.getLogger(__name__)


def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from URL."""
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    elif "youtube.com/watch?v=" in url:
        return url.split("v=")[-1].split("&")[0]
    return None


async def fetch_youtube_transcript(url: str) -> dict | None:
    """
    Extract transcript from YouTube video.

    Args:
        url: YouTube video URL

    Returns:
        Dict with title, transcript, or None if extraction fails
    """
    try:
        video_id = extract_video_id(url)
        if not video_id:
            logger.warning(f"Invalid YouTube URL: {url}")
            return None

        logger.info(f"Fetching transcript for video {video_id}")

        # Try to get transcript
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        except NoTranscriptFound:
            logger.warning(f"No transcript found for {video_id}")
            return None
        except TranscriptsDisabled:
            logger.warning(f"Transcripts disabled for {video_id}")
            return None

        # Combine transcript chunks
        full_text = " ".join([item["text"] for item in transcript])

        return {
            "url": url,
            "video_id": video_id,
            "content": full_text,
            "source_type": "youtube",
        }

    except Exception as e:
        logger.error(f"Error fetching YouTube transcript from {url}: {e}")
        return None
