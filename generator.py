"""Article generation using Claude Sonnet."""

import logging
import os
from anthropic import Anthropic

logger = logging.getLogger(__name__)


async def generate_article(
    person_name: str,
    source_content: str,
    source_url: str,
) -> str | None:
    """
    Generate Chinese financial news article from source content.

    Args:
        person_name: Target person name
        source_content: Full extracted content
        source_url: Original URL

    Returns:
        Generated article markdown or None if failed
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not set")
        return None

    client = Anthropic()

    prompt = f"""Generate a 2000-4000 word Chinese financial news article based on the following source content.

**Requirements:**
1. Opening: Background context for the topic
2. Core points: Key statements and positions
3. Heavy direct quotes: Use exact translations from the source (100% from original text)
4. Editorial commentary: Your analysis and implications
5. Closing: Summary and outlook

**Constraints:**
- ALL quotations must be directly translated from the source material
- Do NOT paraphrase or create new quotes
- Use Chinese financial journalism style (professional, analytical)
- Include source attribution and date

**Source Person:** {person_name}
**Source URL:** {source_url}

**Source Content:**
{source_content[:8000]}  # Truncate very long content

Please generate the article in Markdown format."""

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        article = message.content[0].text
        logger.info(f"Generated article for {person_name}")
        return article

    except Exception as e:
        logger.error(f"Error generating article: {e}")
        return None
