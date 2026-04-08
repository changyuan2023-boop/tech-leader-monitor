#!/usr/bin/env python
"""Test full monitoring workflow with mock Slack."""

import asyncio
import logging
import sys
import os
from pathlib import Path
from unittest.mock import patch, AsyncMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from monitors.main import load_config, monitor_person, process_entries

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_full_workflow():
    """Test full monitoring workflow."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Full Monitoring Workflow")
    logger.info("=" * 60)

    # Mock Slack and classifier
    with patch("monitors.main.send_slack_notification") as mock_slack, \
         patch("monitors.main.classify_relevance") as mock_classifier:

        # Setup mocks
        mock_slack.return_value = True
        mock_classifier.return_value = {
            "is_relevant": True,
            "reason": "First-hand interview"
        }

        # Load config
        config = load_config()
        people = config.get("people", [])

        if not people:
            logger.error("No people configured")
            return False

        logger.info(f"Loaded {len(people)} people from config")

        # Monitor first 2 people only (for testing)
        all_entries = []
        for person_config in people[:2]:
            try:
                logger.info(f"\nMonitoring {person_config.get('name')}...")
                entries = await monitor_person(person_config)
                logger.info(f"  Found {len(entries)} entries")
                all_entries.extend(entries)
            except Exception as e:
                logger.error(f"Error monitoring {person_config.get('name')}: {e}")
                continue

        logger.info(f"\nTotal entries: {len(all_entries)}")

        if not all_entries:
            logger.warning("No entries found to process")
            return True

        # Process entries (this will call mocked functions)
        logger.info("\nProcessing entries...")

        # Process only first 5 entries for quick testing
        test_entries = all_entries[:5]
        processed = await process_entries(test_entries)

        logger.info(f"\nProcessed {processed} entries")

        # Show mock calls
        logger.info(f"\nMock Slack calls: {mock_slack.call_count}")
        logger.info(f"Mock Classifier calls: {mock_classifier.call_count}")

        if mock_slack.call_count > 0:
            logger.info("\nLast Slack notification call:")
            call_args = mock_slack.call_args
            if call_args:
                kwargs = call_args[1] if call_args[1] else call_args[0]
                logger.info(f"  Person: {kwargs.get('person_name', 'N/A')}")
                logger.info(f"  Title: {kwargs.get('title', 'N/A')[:80]}")
                logger.info(f"  Type: {kwargs.get('content_type', 'N/A')}")

        logger.info("\n" + "=" * 60)
        logger.info("Test completed successfully!")
        logger.info("=" * 60)

        return True


async def main():
    """Run test."""
    try:
        success = await test_full_workflow()
        return success
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
