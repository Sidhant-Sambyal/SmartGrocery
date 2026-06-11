import re

UNIT_FACTORS = {
    "g": 1,
    "kg": 1000,
    "mg": 0.001,
    "ml": 1,
    "l": 1000,
    "cl": 10,
}

SHADE_CEILING = 2000.0


# Cache of parsed results so we do not re-run the regex for repeated items.
_parse_cache = {}


def parse_quantity(text: str):
    """
    Parse a string like '500g milk' or '2 kg rice'.

    Returns (amount, unit, base_amount, item_name) or None.
    item_name is the text after the quantity+unit portion.
    """
    
    if text in _parse_cache:
        return _parse_cache[text]

    match = re.match(
        r"\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\b\s*(.*)",
        text
    )

    if not match:
        _parse_cache[text] = None
        return None

    amount = float(match.group(1))
    unit = match.group(2).lower()

    if unit not in UNIT_FACTORS:
        _parse_cache[text] = None
        return None

    item_name = match.group(3).strip()

    # If there's no item name after the unit, this is
    # just a bare number+unit like "500g" with no item
    if not item_name:
        _parse_cache[text] = None
        return None

    base_amount = amount * UNIT_FACTORS[unit]

    result = (amount, unit, base_amount, item_name)
    _parse_cache[text] = result
    return result


def calculate_shade(base_amount: float):

    shade = base_amount / SHADE_CEILING

    return min(shade, 1.0)