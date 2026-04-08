"""Content relevance classification using Aliyun DashScope API."""

import logging
import os
import json
from openai import OpenAI

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
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        logger.error("DASHSCOPE_API_KEY not set")
        return {"is_relevant": False, "reason": "API key not set"}

    api_url = os.getenv("DASHSCOPE_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model = os.getenv("DASHSCOPE_MODEL_CLASSIFY", "qwen-plus")

    client = OpenAI(
        api_key=api_key,
        base_url=api_url
    )

    prompt = f"""Judge if this content is a first-hand statement (speech, interview, blog post, opinion piece)
by {person_name}, not just a news article mentioning them.

Person: {person_name}
Title: {title}
Summary: {summary}

Respond with JSON:
{{"is_relevant": true/false, "reason": "brief reason"}}"""

    try:
        message = client.chat.completions.create(
            model=model,
            max_tokens=100,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.choices[0].message.content
        # Parse JSON response
        result = json.loads(response_text)
        return result

    except Exception as e:
        logger.error(f"Error classifying content: {e}")
        return {"is_relevant": False, "reason": f"Classification error: {e}"}
