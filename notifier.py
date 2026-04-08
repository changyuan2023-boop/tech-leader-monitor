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

    message = {
        "text": f"🎙 New Content: {person_name}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎙 New Content Found",
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Person:*\n{person_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Type:*\n{content_type}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Source:*\n{source}"
                    },
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Title:*\n{title}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Content"
                        },
                        "url": url,
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Generate Article"
                        },
                        "url": generate_url,
                        "style": "danger"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        response.raise_for_status()
        logger.info(f"Sent Slack notification for {person_name}: {title}")
        return True

    except Exception as e:
        logger.error(f"Error sending Slack notification: {e}")
        return False
