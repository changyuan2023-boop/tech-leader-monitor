"""Content relevance classification using Claude Haiku."""

import logging
import os
from anthropic import Anthropic

logger = logging.getLogger(__name__)


async def classify_relevance(
    person_name: str,
    title: str,
    summary: str,
) -> dict:
    """
    Classify if content is relevant (first-hand statement vs. news mention).

    Args:
        person_name: Target person name
        title: Content title
        summary: Content summary/snippet

    Returns:
        Dict with is_relevant (bool) and reason
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not set")
        return {"is_relevant": False, "reason": "API key not set"}

    client = Anthropic()

    prompt = f"""Judge if this content is a first-hand statement (speech, interview, blog post, opinion piece)
by {person_name}, not just a news article mentioning them.

Person: {person_name}
Title: {title}
Summary: {summary}

Respond with JSON:
{{"is_relevant": true/false, "reason": "brief reason"}}"""

    try:
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=100,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text
        # Parse JSON response
        import json
        result = json.loads(response_text)
        return result

    except Exception as e:
        logger.error(f"Error classifying content: {e}")
        return {"is_relevant": False, "reason": f"Classification error: {e}"}
