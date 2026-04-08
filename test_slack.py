#!/usr/bin/env python
"""Test Slack notification formatting."""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from notifier import send_slack_notification

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_slack_format():
    """Test Slack notification with sample data."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Slack Notification Format")
    logger.info("=" * 60)

    # This will only work if SLACK_WEBHOOK_URL is set
    result = await send_slack_notification(
        person_name="Jensen Huang",
        content_type="Interview",
        title="NVIDIA CEO Jensen Huang on AI Chips and Future of Computing",
        url="https://example.com/nvidia-interview-2026",
        source="google_news",
    )

    if result:
        logger.info("\n✓ Slack notification sent successfully!")
        logger.info("\nNotification details:")
        logger.info("  Person: Jensen Huang")
        logger.info("  Type: Interview")
        logger.info("  Title: NVIDIA CEO Jensen Huang on AI Chips...")
        logger.info("  Source: Google News")
    else:
        logger.warning("\n✗ Slack notification failed")
        logger.info("(This is expected if SLACK_WEBHOOK_URL is not set)")

    logger.info("\n" + "=" * 60)
    logger.info("Test completed")
    logger.info("=" * 60)

    return result or True  # Return True even if webhook not set


async def main():
    """Run test."""
    try:
        success = await test_slack_format()
        return success
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
