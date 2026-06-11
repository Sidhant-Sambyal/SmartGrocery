# AI Usage Log

## AI Tools Used
- Gemini 3.1 Pro (via Antigravity IDE)

## Prompts that Moved the Work Forward

**Prompt 1 (Rule 1 Parsing):**
> "Write a Python regular expression to parse a grocery list item. It needs to extract the numeric quantity, the unit (kg, g, l, ml, etc.), and the actual item name. For example, for '2 kg salt', it should extract (2, 'kg', 'salt'). Make it robust to different spacing."

**Prompt 2 (Accessibility/Contrast):**
> "Write a Python function to calculate the WCAG 2.x contrast ratio between a background hex color and a text hex color. The output should be a float representing the ratio (e.g., 4.5)."

**Prompt 3 (LLM Integration):**
> "Write an async Python function using the google-generativeai SDK. It takes a grocery item string and returns exactly one of these five categories: produce, dairy, bakery, frozen, household. Ensure the prompt strictly instructs the model to return ONLY the category name."

## Mistakes the AI Made and How They Were Fixed

**Mistake 1: Contrast Ratio Formula**
When I asked the AI to write the contrast ratio calculator, it initially provided a simple lightness difference calculation instead of the official WCAG relative luminance formula (which requires transforming the RGB values into linear sRGB space before applying the `0.2126 * R + 0.7152 * G + 0.0722 * B` weights). 
* **How I fixed it:** I noticed the outputs were incorrect when testing known color pairs (like black and white not returning 21:1). I prompted the AI again: "That formula is incorrect. You need to use the exact WCAG 2.0 relative luminance formula, including the sRGB piecewise conversion." It then generated the correct math, which I verified using a web contrast tool.

**Mistake 2: Regex Over-matching**
For the quantity parser, the AI generated the regex `^([\d.]+)\s*([a-zA-Z]+)\s*(.*)$`. This successfully parsed "2 kg salt", but it also incorrectly parsed "5 apple" by assuming "apple" was the unit. 
* **How I fixed it:** I realized we needed a strict whitelist of known units rather than matching any alphabetic string. I refactored the regex to `^([\d.]+)\s*(kg|g|l|ml)\b\s*(.*)$` to explicitly restrict the allowed units to our measured system.

**Mistake 3: LLM Output Formatting**
When implementing Rule 3, the AI's prompt for the LLM occasionally caused the model to return conversational text like "The item belongs in the **produce** aisle." instead of just the literal string "produce", breaking the frontend routing.
* **How I fixed it:** I had to iteratively refine the prompt instructions sent to the LLM, eventually adding a strict system instruction: "Return ONLY the category word. No punctuation, no markdown, no explanation." and handling `.strip().lower()` on the backend.
