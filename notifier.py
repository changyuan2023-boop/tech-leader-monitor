"""Slack webhook notifications."""

import logging
import os
import requests

logger = logging.getLogger(__name__)


async def send_slack_notification(
    person_name: str,
    content_type: str,
    title: str,
    url: str,
    source: str,
) -> bool:
    """
    Send Slack notification about new content.

    Args:
        person_name: Person name
        content_type: Type (blog, interview, speech, etc.)
        title: Content title
        url: Content URL
        source: Source name (rss, youtube, google_news)

    Returns:
        True if successful
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logger.error("SLACK_WEBHOOK_URL not set")
        return False

    # Build action URL for manual trigger
    repo_url = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    repo_name = os.getenv("GITHUB_REPOSITORY", "user/repo")
    generate_url = f"{repo_url}/{repo_name}/actions/workflows/generate.yml"

    # Build notification text content
    notification_text = f"""🎙 新内容发现

人物：{person_name}
类型：{content_type}
标题：{title}
来源：{source}
链接：{url}

👉 点此生成中文资讯：{generate_url}"""

    # Format message according to custom webhook schema
    message = {
        "tech_leader_monitor": notification_text
    }

    try:
        response = requests.post(webhook_url, json=message, timeout=10,
                                headers={"Content-Type": "application/json"})
        response.raise_for_status()
        logger.info(f"Sent Slack notification for {person_name}: {title}")
        return True

    except Exception as e:
        logger.error(f"Error sending Slack notification: {e}")
        return False
