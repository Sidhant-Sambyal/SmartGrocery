"""Quantity-and-unit parser for the grocery list app.

Takes a free-text item like "2 kg rice" or "500 ml milk", pulls out the
number and unit, normalizes it to a base unit (grams or millilitres), and
turns that into a shade value between 0.0 and 1.0 so the UI can pick a
darker badge for bigger quantities.

This module ships with the front end. It is pure and has no LLM calls.
"""

import re

# Conversion factors into base units. Weight normalizes to grams, volume to ml.
UNIT_FACTORS = {
    "g": 1,
    "kg": 1000,
    "mg": 0.001,
    "ml": 1,
    "l": 100,
    "cl": 10,
}

# Anything at or above this (in base units) is treated as a "big" quantity
# and gets the darkest shade.
SHADE_CEILING = 2000.0

# Cache of parsed results so we do not re-run the regex for repeated items.
_parse_cache = {}


def parse_quantity(text):
    """Parse a string like '2 kg rice' into (amount, unit, base_amount).

    Returns None if no leading number-and-unit is found.
    base_amount is the quantity converted into base units (g or ml).
    """
    if text in _parse_cache:
        return _parse_cache[text]

    match = re.match(r"\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)", text)
    if not match:
        _parse_cache[text] = None
        return None

    amount = float(match.group(1))
    unit = match.group(2).lower()

    if unit not in UNIT_FACTORS:
        _parse_cache[text] = None
        return None

    base_amount = amount * UNIT_FACTORS[unit]
    result = (amount, unit, base_amount)
    _parse_cache[text] = result
    return result


def shade_for(text):
    """Return a shade float in [0.0, 1.0] for the given item text.

    0.0 is the lightest badge, 1.0 is the darkest. The shade always stays
    inside the range, so callers never have to clamp it themselves.
    """
    parsed = parse_quantity(text)
    if parsed is None:
        return 0.0

    _, _, base_amount = parsed
    shade = base_amount / SHADE_CEILING
    return shade
