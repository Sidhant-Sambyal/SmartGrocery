import logging

from app.services.quantity_service import (
    parse_quantity,
    calculate_shade,
)

from app.services.staple_service import (
    is_staple,
)

from app.services.llm_service import (
    classify_aisle,
    NonGroceryItemError,
)

from app.core.constants import (
    AISLE_COLORS,
    STAPLE_COLOR,
)

from app.utils.color_utils import (
    shade_to_hex,
    get_text_color_for_bg,
)

logger = logging.getLogger(__name__)


async def process_item(item: str):
    """
    Process a grocery item according to the rule order:

    Rule 1:
        Quantity + Unit → measured badge
        (item name is validated via LLM / local fallback)

    Rule 2:
        Pantry staple → staple badge

    Rule 3:
        LLM classification → aisle badge
    """

    logger.info(
        "Processing grocery item: %s",
        item,
    )

    # -----------------------------
    # Rule 1: Quantity + Unit
    # -----------------------------
    parsed = parse_quantity(item)

    if parsed:
        amount, unit, base_amount, item_name = parsed

        import re
        # Validate the item name using regex instead of the LLM to save latency/cost.
        # Reject gibberish like "asasssss" (4+ repeated chars) or inputs with <2 letters.
        if re.search(r"(.)\1{3,}", item_name) or len(re.sub(r'[^a-zA-Z]', '', item_name)) < 2:
            logger.warning("Rejected gibberish item name via regex: %s", item_name)
            raise NonGroceryItemError(f"'{item_name}' does not look like a valid grocery item.")

        shade = calculate_shade(base_amount)
        badge_color = shade_to_hex(shade)
        text_color = get_text_color_for_bg(badge_color)

        logger.info(
            "Matched measured item rule: unit=%s base_amount=%s shade=%s color=%s text=%s",
            unit,
            base_amount,
            shade,
            badge_color,
            text_color,
        )

        return {
            "item": item,
            "tag_type": "measured",
            "color": badge_color,
            "text_color": text_color,
            "metadata": {
                "amount": amount,
                "unit": unit,
                "base_amount": base_amount,
                "shade": shade,
            },
        }

    # -----------------------------
    # Rule 2: Pantry Staple
    # -----------------------------
    if is_staple(item):

        logger.info(
            "Matched staple item rule"
        )

        return {
            "item": item,
            "tag_type": "staple",
            "color": STAPLE_COLOR,
            "metadata": {
                "source": "staple_rule",
            },
        }

    # -----------------------------
    # Rule 3: LLM Classification
    # -----------------------------
    aisle = await classify_aisle(item)

    logger.info(
        "Classified item with LLM: aisle=%s",
        aisle,
    )

    return {
        "item": item,
        "tag_type": aisle,
        "color": AISLE_COLORS.get(
            aisle,
            "#000000",
        ),
        "metadata": {
            "aisle": aisle,
            "source": "llm",
        },
    }