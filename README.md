# SmartGrocery

AI-powered grocery classification & list builder, using Gemini to automatically sort items into aisles.

**Live Demo (Vercel):** [https://smartgrocery-YOUR_DEPLOY_ID.vercel.app](https://smartgrocery-YOUR_DEPLOY_ID.vercel.app) *(Replace with actual URL)*  
**Public Repository:** [https://github.com/yourusername/SmartGrocery](https://github.com/yourusername/SmartGrocery) *(Replace with actual repo)*  

## How to Run Locally

1. **Install dependencies:**
   ```bash
   python -m venv .venv
   # On Windows: .venv\Scripts\activate
   # On Mac/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables:**
   Ensure you have a `.env` file in the root directory containing your Gemini API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Run the Development Server:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Open the App:**
   Navigate to [http://localhost:8000](http://localhost:8000) in your browser. *(Note: You must log in using an `@company.com` email address).*

---

## Badge Contrast Ratios (WCAG AA Compliance)

All badge text must remain readable as background colours change. The **measured** badge uses a dynamic blue ramp—light blue (#ADD8E6) for tiny quantities through to dark navy (#003366) for large ones. The text colour (black or white) is selected automatically via WCAG 2.x relative-luminance contrast calculation, guaranteeing the highest possible ratio at every shade.

### Measured badge ramp (dynamic)

Quantities are normalised to grams before computing shade (`1 kg = 1000 g`, `1 l = 1000 ml`, etc.), so `1 kg` correctly produces a darker badge than `999 g`.

| Shade | Background | Text    | Contrast Ratio | WCAG AA |
|------:|-----------:|--------:|---------------:|--------:|
|  0.0  | `#ADD8E6`  | `#000`  |       **13.74** | ✅ PASS |
|  0.1  | `#9BC7D9`  | `#000`  |       **11.57** | ✅ PASS |
|  0.2  | `#8AB7CC`  | `#000`  |        **9.73** | ✅ PASS |
|  0.3  | `#79A6BF`  | `#000`  |        **8.02** | ✅ PASS |
|  0.4  | `#6796B2`  | `#000`  |        **6.58** | ✅ PASS |
|  0.5  | `#5685A6`  | `#000`  |        **5.30** | ✅ PASS |
|  0.6  | `#457599`  | `#FFF`  |        **4.93** | ✅ PASS |
|  0.7  | `#33648C`  | `#FFF`  |        **6.28** | ✅ PASS |
|  0.8  | `#22547F`  | `#FFF`  |        **7.95** | ✅ PASS |
|  0.9  | `#114372`  | `#FFF`  |       **10.15** | ✅ PASS |
|  1.0  | `#003366`  | `#FFF`  |       **12.61** | ✅ PASS |

- **Lightest badge** (shade 0.0, e.g. `1 g`): `#ADD8E6` bg + `#000000` text → **13.74 : 1**
- **Darkest badge** (shade 1.0, e.g. `2 kg`): `#003366` bg + `#FFFFFF` text → **12.61 : 1**
- **Worst-case crossover** (shade 0.5, e.g. `1 kg`): `#5685A6` bg + `#000000` text → **5.30 : 1**

All ratios exceed the WCAG AA threshold of **4.5 : 1** for normal text.

### Real-world examples

| Item           | Base (g) | Shade | Background | Text    | Ratio    | AA   |
|---------------:|---------:|------:|-----------:|--------:|---------:|-----:|
| 1 g sugar      |        1 |  0.00 | `#ACD7E5`  | `#000`  | **13.61**| PASS |
| 100 g pasta    |      100 |  0.05 | `#A4CFDF`  | `#000`  | **12.57**| PASS |
| 250 g butter   |      250 |  0.12 | `#97C3D6`  | `#000`  | **11.09**| PASS |
| 500 g flour    |      500 |  0.25 | `#81AEC6`  | `#000`  |  **8.80**| PASS |
| 1 kg rice      |     1000 |  0.50 | `#5685A6`  | `#000`  |  **5.30**| PASS |
| 1.5 kg chicken |     1500 |  0.75 | `#2B5C86`  | `#FFF`  |  **7.05**| PASS |
| 2 kg potatoes  |     2000 |  1.00 | `#003366`  | `#FFF`  | **12.61**| PASS |
| 5 kg bag       |     5000 |  1.00 | `#003366`  | `#FFF`  | **12.61**| PASS |

### Static aisle badges

These badges use the aisle colour as text on the dark page background (`#0d0f17`).

| Aisle     | Text Hex  | Contrast vs `#0d0f17` | WCAG AA |
|----------:|----------:|----------------------:|--------:|
| Produce   | `#4CAF50` |              **6.88** | ✅ PASS |
| Dairy     | `#2196F3` |              **6.12** | ✅ PASS |
| Bakery    | `#FF9800` |              **8.88** | ✅ PASS |
| Frozen    | `#00BCD4` |              **8.33** | ✅ PASS |
| Household | `#CE93D8` |              **8.01** | ✅ PASS |
| Staple    | `#808080` |              **4.84** | ✅ PASS |

> **Methodology:** Ratios computed with WCAG 2.x relative-luminance formula  
> (`(L1 + 0.05) / (L2 + 0.05)`), implemented in  
> [`color_utils.py`](app/utils/color_utils.py). Reproducible via  
> `python scripts/measure_contrast.py`.

---

## How it works

1. **Quantity + Unit** → parsed, normalised to grams/ml, shade computed, dynamic badge colour generated
2. **Pantry Staple** → matched against known set (salt, sugar, flour, rice, oil)
3. **LLM Classification** → Gemini classifies remaining items into aisles (produce, dairy, bakery, frozen, household)
