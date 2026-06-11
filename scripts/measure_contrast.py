"""
Measure WCAG contrast ratios for the SmartGrocery measured-badge colour ramp.

The measured badge background goes from light blue to dark blue
as the shade value goes from 0.0 to 1.0.  We need to verify that
the chosen text colour on each badge meets WCAG AA (>= 4.5 : 1).

This script:
  1. Computes background hex at every 0.1 shade step.
  2. Computes the auto-selected text color via luminance contrast.
  3. Prints measured contrast ratios.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.utils.color_utils import (
    shade_to_hex,
    get_text_color_for_bg,
    contrast_ratio,
)
from app.services.quantity_service import calculate_shade

# ── Badge colour ramp ───────────────────────────────────────
print("=" * 68)
print("  WCAG Contrast Ratio Audit - SmartGrocery Measured Badge")
print("=" * 68)
print()
print(f"{'Shade':>7}  {'Background':>10}  {'Text':>10}  {'Ratio':>7}  {'WCAG AA':>8}")
print("-" * 68)

all_pass = True

for i in range(0, 11):
    shade = i / 10.0
    bg = shade_to_hex(shade)
    fg = get_text_color_for_bg(bg)
    ratio = contrast_ratio(bg, fg)
    passed = ratio >= 4.5
    if not passed:
        all_pass = False
    status = "PASS" if passed else "FAIL"
    print(f"{shade:>7.1f}  {bg:>10}  {fg:>10}  {ratio:>7.2f}  {status:>8}")

print("-" * 68)
print()

# ── Real-world examples ─────────────────────────────────────
print("Real-world examples:")
print(f"{'Input':>20}  {'Base(g)':>8}  {'Shade':>6}  {'BG':>10}  {'Text':>10}  {'Ratio':>7}  {'AA':>6}")
print("-" * 68)

examples = [
    ("1g sugar",    1),
    ("100g pasta",  100),
    ("250g butter", 250),
    ("500g flour",  500),
    ("1kg rice",    1000),
    ("1.5kg chicken", 1500),
    ("2kg potatoes", 2000),
    ("5kg bag",     5000),
]

for label, base in examples:
    shade = calculate_shade(base)
    bg = shade_to_hex(shade)
    fg = get_text_color_for_bg(bg)
    ratio = contrast_ratio(bg, fg)
    status = "PASS" if ratio >= 4.5 else "FAIL"
    print(f"{label:>20}  {base:>8}  {shade:>6.2f}  {bg:>10}  {fg:>10}  {ratio:>7.2f}  {status:>6}")

print("-" * 68)
print()

# ── Also measure the static aisle badges ────────────────────
AISLE_COLORS = {
    "Produce":   "#4CAF50",
    "Dairy":     "#2196F3",
    "Bakery":    "#FF9800",
    "Frozen":    "#00BCD4",
    "Household": "#CE93D8",
    "Staple":    "#808080",
}

print("Static aisle badges (text = badge color on dark bg #0d0f17):")
print(f"{'Aisle':>12}  {'Text Hex':>10}  {'vs #0d0f17':>10}  {'Ratio':>7}  {'AA':>6}")
print("-" * 68)

for name, color in AISLE_COLORS.items():
    ratio = contrast_ratio("#0d0f17", color)
    status = "PASS" if ratio >= 4.5 else "FAIL"
    print(f"{name:>12}  {color:>10}  {'#0d0f17':>10}  {ratio:>7.2f}  {status:>6}")

print("-" * 68)
print()

if all_pass:
    print("All measured badge states pass WCAG AA (>= 4.5:1)")
else:
    print("Some measured badge states FAIL WCAG AA (>= 4.5:1)")
