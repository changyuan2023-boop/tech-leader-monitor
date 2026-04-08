#!/usr/bin/env python
"""Test URL deduplication logic."""

import logging
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dedup import is_duplicate, save_seen_url, load_seen_urls

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_dedup():
    """Test deduplication logic."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing URL Deduplication")
    logger.info("=" * 60)

    # Test URLs
    test_urls = [
        "https://blogs.nvidia.com/blog/2026/04/08/ai-news/",
        "https://example.com/article-1",
        "https://example.com/article-2",
    ]

    # Test 1: Check initial state
    logger.info("\n1. Initial state:")
    seen_before = load_seen_urls()
    logger.info(f"   Previously seen: {len(seen_before)} URLs")

    # Test 2: Add URLs
    logger.info("\n2. Adding new URLs:")
    for url in test_urls:
        is_dup = is_duplicate(url)
        logger.info(f"   {url[:50]}...")
        logger.info(f"     Is duplicate? {is_dup}")

        if not is_dup:
            save_seen_url(url)
            logger.info(f"     ✓ Saved")
        else:
            logger.info(f"     ✗ Already seen")

    # Test 3: Verify duplicates are detected
    logger.info("\n3. Verifying duplicates:")
    for url in test_urls:
        is_dup = is_duplicate(url)
        status = "✓ Detected" if is_dup else "✗ Not detected"
        logger.info(f"   {url[:50]}... {status}")

    # Test 4: Check final state
    logger.info("\n4. Final state:")
    seen_now = load_seen_urls()
    logger.info(f"   Total seen URLs: {len(seen_now)}")

    # Show the dedup file content
    dedup_file = Path(__file__).parent / "data" / "seen_urls.json"
    if dedup_file.exists():
        with open(dedup_file) as f:
            data = json.load(f)
        logger.info(f"\n5. Dedup file content:")
        logger.info(f"   Total URLs: {len(data.get('urls', []))}")
        logger.info(f"   Last updated: {data.get('last_updated')}")
        logger.info(f"   Retention days: {data.get('retention_days')}")

    logger.info("\n" + "=" * 60)
    logger.info("Deduplication test completed")
    logger.info("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = test_dedup()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)
