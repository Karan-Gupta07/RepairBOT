# RepairBOT

Take a photo of a broken object (e.g. office chair with a broken wheel) and get brief repair info plus links to find or buy parts and tools.

## What it does

- **Analyzes the image** with Google Gemini and returns:
  - Repairability (low / medium / high)
  - Difficulty level (easy / moderate / hard)
  - Estimated cost and time
  - Step-by-step repair instructions
  - Lists of suggested **parts** and **tools**
- **Product links** – By default, each part/tool gets a **Google Shopping search link** (no API key). Optionally, you can connect **your Shopify store** to show direct product links from your catalog instead (with automatic per-item fallback to Google Shopping).
- **App Clip** – Optional iOS App Clip experience via Reactiv ClipKit Lab (see `clip/` directory).

## Setup

1. **Python 3.10+** and **Node.js 18+**.

2. **Install backend dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Build the frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. **Environment variables**
   Copy `.env.example` to `.env` and set at least:
   - **GEMINI_API_KEY** – from [Google AI Studio](https://aistudio.google.com/apikey) (required for analysis)

   **Optional – Shopify:** To show product links from your own store instead of Google Shopping, also set:
   - **SHOPIFY_STORE_DOMAIN** – e.g. `mystore.myshopify.com`
   - **SHOPIFY_STOREFRONT_ACCESS_TOKEN** – from Shopify Admin → Develop apps → your app → Storefront API token

5. **Run the app**
   ```bash
   uvicorn backend.main:app --reload
   ```

6. Open **http://localhost:8000**, upload a photo of the broken item, and click **Analyze repair**.

### Frontend development

For hot-reload during frontend development, run the Vite dev server (proxies `/analyze` to the FastAPI backend):

```bash
cd frontend
npm run dev
```

Then open **http://localhost:5173**.

## Project structure

```
RepairBOT/
├── backend/
│   ├── main.py              # FastAPI app, /analyze endpoint, static serving
│   ├── gemini_service.py    # Gemini image analysis with retry
│   ├── shopify_service.py   # Product links (Shopify + Google Shopping fallback)
│   ├── config.py            # Environment config
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── package.json         # React + Vite
│   ├── vite.config.js       # Dev proxy + build config
│   ├── index.html           # Vite entry point
│   └── src/
│       ├── main.jsx         # React entry
│       ├── App.jsx          # Shell: routing, fetch, state
│       ├── App.css          # All styles (dark theme)
│       └── components/
│           ├── Landing.jsx      # Landing page
│           ├── UploadCard.jsx   # Image upload + preview
│           └── ResultsCard.jsx  # Analysis results display
├── clip/                    # iOS App Clip (Reactiv ClipKit Lab)
│   ├── README.md
│   └── RepairBOTClip/       # SwiftUI app
├── .env.example
└── PRD.md
```

## API

- **POST /analyze** – body: multipart form with `image` file (JPEG, PNG, or WebP; max 10 MB). Returns JSON with `repairability`, `difficulty`, `estimated_time`, `estimated_cost_usd`, `brief_description`, `repair_steps`, `parts_needed`, `tools_needed`, and `products: { parts, tools, source }`. `source` is `"shopify"` when at least one product came from Shopify, otherwise `"google_shopping"`.

## Notes

- **Without Shopify:** Links open a Google Shopping search for each part/tool so users can find products from any retailer. No extra API keys needed.
- **With Shopify:** Links point to products in your store (Storefront API). Items not in your catalog automatically fall back to Google Shopping links.
- Images are sent to Google Gemini for analysis and are not stored. Use in line with Google's API terms and privacy policy.
