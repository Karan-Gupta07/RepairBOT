# RepairBOT

Take a photo of a broken object (e.g. office chair with a broken wheel) and get brief repair info plus direct links to find and buy parts and tools from Shopify stores.

## What it does

- **Analyzes the image** with Google Gemini and returns:
  - Repairability (low / medium / high)
  - Estimated cost (e.g. $50)
  - Short description of the damage and repair
  - Lists of suggested **parts** and **tools**
- **Product links** – Searches across your configured Shopify stores to find parts and tools. Shows direct links to products in your stores.

## Setup

1. **Python 3.10+** and a terminal in the project folder.

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment variables**  
   Copy `.env.example` to `.env` and set at least:
   - **GEMINI_API_KEY** – from [Google AI Studio](https://aistudio.google.com/apikey) (required for image analysis)

   **Shopify Configuration:** Connect one or more Shopify stores:
   - **Option A (Multiple stores - recommended):** Set `SHOPIFY_STORES` with comma-separated entries:
     ```
     SHOPIFY_STORES=store1.myshopify.com|token1,store2.myshopify.com|token2
     ```
   - **Option B (Single store - legacy):** Set `SHOPIFY_STORE_DOMAIN` and `SHOPIFY_STOREFRONT_ACCESS_TOKEN`

   To get a Shopify Storefront API token:
   - Go to Shopify Admin → Settings → Apps and sales channels → Develop apps
   - Create an app or use an existing one
   - Enable `read:products` scope
   - Generate and copy the Storefront API access token

4. **Run the app**
   ```bash
   uvicorn app.main:app --reload
   ```

5. Open **http://localhost:8000**, upload a photo of the broken item, and click **Analyze repair**.

## API

- **POST /analyze** – body: multipart form with `image` (file). Returns JSON with `repairability`, `estimated_cost_usd`, `brief_description`, `repair_steps`, `parts_needed`, `tools_needed`, and `products: { parts, tools, source }`. 
  - `products.parts` and `products.tools` are arrays of `{title, url, store}`
  - `url` is null if the item wasn't found in any configured store
  - `source` is always `"shopify"`

## Notes

- Products are searched across all configured Shopify stores
- If a part or tool isn't found in any store, it's still shown in the repair summary but without a link
- Images are sent to Google Gemini for analysis; use in line with Google's API terms and privacy policy
- Shopify API calls use your configured Storefront API tokens
