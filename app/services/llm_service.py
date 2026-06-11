import logging
from typing import Optional

from google import genai

from app.core.config import settings

logger = logging.getLogger(__name__)

client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)

VALID_AISLES = {
    "produce",
    "dairy",
    "bakery",
    "frozen",
    "household",
}


class NonGroceryItemError(ValueError):
    pass

class LLMLimitExceededError(Exception):
    pass


async def classify_aisle(item: str) -> str:

    prompt = f"""
You are a strict grocery item classification system. Your task is to classify the following item into EXACTLY one of the valid aisles below. 

Valid responses (must match exactly):
- produce
- dairy
- bakery
- frozen
- household
- not_grocery

Item: {item}

Guardrails:
1. If the item is not something typically bought at a grocery store, you MUST return "not_grocery".
2. You MUST return ONLY the exact word from the valid responses list.
3. DO NOT include any punctuation, markdown, capital letters, or conversational text. 
4. DO NOT explain your reasoning.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )
    except Exception:
        logger.warning(
            "Gemini aisle classification failed",
            exc_info=True,
        )
        raise LLMLimitExceededError(
            "LLM limit exceeded, try after sometime."
        )

    aisle = getattr(response, "text", "").strip().lower()

    if aisle == "not_grocery":
        raise NonGroceryItemError(
            "Item is not a grocery item."
        )

    if aisle not in VALID_AISLES:
        logger.warning(
            "Gemini returned invalid aisle: %s",
            aisle,
        )
        raise NonGroceryItemError(
            "Item is not a grocery item."
        )

    return aisle
