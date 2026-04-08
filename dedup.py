"""URL deduplication using seen_urls.json."""

import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

SEEN_URLS_FILE = Path(__file__).parent / "data" / "seen_urls.json"


def _hash_url(url: str) -> str:
    """Generate hash of URL."""
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def load_seen_urls() -> set[str]:
    """Load previously seen URLs from file."""
    if not SEEN_URLS_FILE.exists():
        return set()

    try:
        with open(SEEN_URLS_FILE) as f:
            data = json.load(f)
        return set(data.get("urls", []))
    except Exception as e:
        logger.error(f"Error loading seen_urls.json: {e}")
        return set()


def save_seen_url(url: str) -> bool:
    """Add URL to seen list and save to file."""
    try:
        data = {
            "urls": list(load_seen_urls()) + [_hash_url(url)],
            "last_updated": datetime.now().isoformat(),
            "retention_days": 90,
        }

        # Cleanup old entries (keep last 90 days)
        data["urls"] = data["urls"][-1000:]  # Keep max 1000 entries

        with open(SEEN_URLS_FILE, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Added URL to dedup: {url[:50]}...")
        return True

    except Exception as e:
        logger.error(f"Error saving seen URL: {e}")
        return False


def is_duplicate(url: str) -> bool:
    """Check if URL has been seen before."""
    seen = load_seen_urls()
    url_hash = _hash_url(url)
    return url_hash in seen
