# SmartGrocery

AI-powered grocery classification & list builder, using Gemini to automatically sort items into aisles.

**Live Demo (Vercel):** [https://smart-grocery-gules.vercel.app](https://smart-grocery-gules.vercel.app)


**Public Repository:** [https://github.com/Sidhant-Sambyal/SmartGrocery](https://github.com/Sidhant-Sambyal/SmartGrocery)  

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
   Navigate to [http://localhost:8000](http://localhost:8000) in your browser.

---


## How it works

1. **Quantity + Unit** → parsed, normalised to grams/ml, shade computed, dynamic badge colour generated
2. **Pantry Staple** → matched against known set (salt, sugar, flour, rice, oil)
3. **LLM Classification** → Gemini classifies remaining items into aisles (produce, dairy, bakery, frozen, household)
