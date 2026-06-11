# Reverse Code Review: `quantity_shade.py`

Here is my review of the `quantity_shade.py` parser. I noticed a few critical bugs and some areas for improvement that could cause issues in production.

## 1. Incorrect Conversion Factor for Litres (Bug)
**Location:** `UNIT_FACTORS` dictionary, line 19.
**Problem:** The conversion factor for liters (`"l"`) is set to `100`, but it should be `1000` (1 liter = 1000 ml).
**Impact:** A "1 l milk" item will be normalized to 100 ml, causing its shade to be incorrectly lighter than a "500 ml" item. 
**Fix:** Change `"l": 100` to `"l": 1000`.

## 2. Missing Value Clamp in `shade_for` (Bug)
**Location:** `shade_for()` function, line 69.
**Problem:** The docstring explicitly guarantees that "The shade always stays inside the range, so callers never have to clamp it themselves," returning a float in `[0.0, 1.0]`. However, the calculation is simply `shade = base_amount / SHADE_CEILING`. If the quantity exceeds `SHADE_CEILING` (e.g. "5 kg potatoes"), the shade will be `2.5`.
**Impact:** Unclamped values > 1.0 will likely break the UI color scaling functions (e.g. throwing CSS RGB hex conversion errors or breaking out-of-bounds UI elements).
**Fix:** Update the return statement to clamp the value: `return min(shade, 1.0)`.

## 3. Unbounded Memory Leak in Cache (Production Warning)
**Location:** `_parse_cache = {}`, line 28.
**Problem:** The script implements its own caching mechanism using a global dictionary that grows indefinitely. Every unique string parsed will be stored forever.
**Impact:** While perhaps acceptable if this code only runs transiently in a frontend browser session, if this code ever runs on a long-lived backend process, it will cause a memory leak over time.
**Fix:** Remove the manual dictionary and use Python's built-in `functools.lru_cache(maxsize=128)` decorator on `parse_quantity`, which automatically handles cache eviction.

## 4. Discarding the Item Name (Design Improvement)
**Location:** `parse_quantity()` function, lines 40-55.
**Problem:** The regex `\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)` successfully captures the quantity and the unit, but completely ignores the rest of the string (the actual item name, like "rice" in "2 kg rice").
**Impact:** While not strictly a bug against the current docstring, throwing away the item name means downstream rules (like Rule 2 staple matching or Rule 3 LLM classification) will have to either accept the string with the quantity prepended to it or re-parse the string to strip the quantity out.
**Fix:** Update the regex to capture the remainder of the string `r"^\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s+(.*)"` and return the isolated item name alongside the amount and unit.
