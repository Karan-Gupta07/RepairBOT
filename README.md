# RepairBOT

Take a photo of a broken object (e.g. office chair with a broken wheel) and get brief repair info plus links to find or buy parts and tools.

## What it does

- **Analyzes the image** with Google Gemini and returns:
  - Repairability (low / medium / high)
  - Estimated cost (e.g. $50)
  - Short description of the damage and repair
  - Lists of suggested **parts** and **tools**
- **Product links** – By default, each part/tool gets a **Google Shopping search link** (no API key). Optionally, you can connect **your Shopify store** to show direct product links from your catalog instead.

## Setup

1. **Python 3.10+** and a terminal in the project folder.

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment variables**  
   Copy `.env.example` to `.env` and set at least:
   - **GEMINI_API_KEY** – from [Google AI Studio](https://aistudio.google.com/apikey) (required for analysis)

   **Optional – Shopify:** To show product links from your own store instead of Google Shopping, also set:
   - **SHOPIFY_STORE_DOMAIN** – e.g. `mystore.myshopify.com`
   - **SHOPIFY_STOREFRONT_ACCESS_TOKEN** – from Shopify Admin → Develop apps → your app → Storefront API token

4. **Run the app**
   ```bash
   uvicorn app.main:app --reload
   ```

5. Open **http://localhost:8000**, upload a photo of the broken item, and click **Analyze repair**.

## API

- **POST /analyze** – body: multipart form with `image` (file). Returns JSON with `repairability`, `estimated_cost_usd`, `brief_description`, `parts_needed`, `tools_needed`, and `products: { parts, tools, source }`. `source` is `"google_shopping"` or `"shopify"`.

## Notes

- **Without Shopify:** Links open a Google Shopping search for each part/tool so users can find products from any retailer. No extra API keys needed.
- **With Shopify:** Links point to products in your store (Storefront API). If something isn’t in your catalog, that item won’t have a store link; the repair summary is still returned.
- Images are sent to Google Gemini for analysis; use in line with Google’s API terms and privacy policy.
