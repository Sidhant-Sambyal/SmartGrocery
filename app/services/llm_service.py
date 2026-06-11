import logging

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

AISLE_KEYWORDS = {
    "produce": {
        "apple",
        "banana",
        "carrot",
        "lettuce",
        "onion",
        "orange",
        "potato",
        "tomato",
        "vegetable",
    },
    "dairy": {
        "butter",
        "cheese",
        "curd",
        "milk",
        "paneer",
        "yogurt",
    },
    "bakery": {
        "bagel",
        "bread",
        "bun",
        "cake",
        "croissant",
        "muffin",
    },
    "frozen": {
        "frozen",
        "ice cream",
        "nuggets",
        "peas",
    },
    "household": {
        "detergent",
        "soap",
        "tissue",
        "toilet",
        "trash",
    },
}


def classify_aisle_locally(item: str) -> str | None:
    normalized_item = item.strip().lower()

    for aisle, keywords in AISLE_KEYWORDS.items():
        if any(keyword in normalized_item for keyword in keywords):
            return aisle

    return None


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
        fallback_aisle = classify_aisle_locally(item)

        if fallback_aisle is None:
            logger.warning(
                "Gemini aisle classification failed and local fallback did not match a grocery item",
                exc_info=True,
            )
            raise NonGroceryItemError(
                "Item is not a grocery item."
            )

        logger.warning(
            "Gemini aisle classification failed; using local fallback: aisle=%s",
            fallback_aisle,
            exc_info=True,
        )

        return fallback_aisle

    aisle = getattr(response, "text", "").strip().lower()

    if aisle == "not_grocery":
        raise NonGroceryItemError(
            "Item is not a grocery item."
        )

    if aisle not in VALID_AISLES:
        fallback_aisle = classify_aisle_locally(item)

        if fallback_aisle is None:
            logger.warning(
                "Gemini returned invalid aisle and local fallback did not match a grocery item: %s",
                aisle,
            )
            raise NonGroceryItemError(
                "Item is not a grocery item."
            )

        logger.warning(
            "Gemini returned invalid aisle: %s",
            aisle,
        )
        return fallback_aisle

    return aisle
