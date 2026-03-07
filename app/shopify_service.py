"""Search public Shopify stores using SerpAPI and fetch products via public JSON endpoints."""
import httpx
import urllib.parse
from typing import Any
import re

from app.config import SERPAPI_API_KEY

def _search_shopify_stores(query: str) -> list[str]:
    """Use SerpAPI to find Shopify stores selling the product. Return list of store domains."""
    if not SERPAPI_API_KEY or not query.strip():
        return []
    
    try:
        with httpx.Client(timeout=15.0) as client:
            # Search for the product on Shopify stores
            search_query = f"site:myshopify.com {query}"
            params = {
                "q": search_query,
                "api_key": SERPAPI_API_KEY,
                "engine": "google",
                "num": 10,
            }
            r = client.get("https://serpapi.com/search", params=params, timeout=15.0)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return []
    
    # Extract unique store domains from results
    stores = set()
    organic_results = data.get("organic_results", [])
    for result in organic_results:
        link = result.get("link", "")
        # Extract domain from links like https://store.myshopify.com/products/...
        match = re.search(r"https?://([^/]+\.myshopify\.com)", link)
        if match:
            stores.add(match.group(1))
    
    return list(stores)[:5]  # Limit to 5 stores per product


def _fetch_products_from_store(store_domain: str, product_name: str) -> list[dict[str, Any]]:
    """Fetch products from a Shopify store's public JSON endpoint. Return list of {title, url, price, image, source}."""
    if not store_domain or not product_name.strip():
        return []
    
    try:
        with httpx.Client(timeout=10.0) as client:
            # Try to get /products.json (lists all products)
            url = f"https://{store_domain}/products.json"
            r = client.get(url, timeout=10.0)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return []
    
    products = data.get("products", [])
    results = []
    product_name_lower = product_name.lower()
    
    for product in products[:20]:  # Limit results
        title = product.get("title", "")
        # Simple matching - check if product name is in title
        if product_name_lower not in title.lower():
            continue
        
        handle = product.get("handle", "")
        product_url = f"https://{store_domain}/products/{handle}"
        
        # Get first image
        images = product.get("images", [])
        image_url = images[0].get("src") if images else None
        
        # Get price from first variant
        variants = product.get("variants", [])
        price = None
        if variants:
            price = variants[0].get("price")
        
        results.append({
            "title": title,
            "url": product_url,
            "store": store_domain,
            "price": price,
            "image": image_url,
            "product_id": product.get("id"),
            "source": "shopify",
        })
    
    return results


def _google_shopping_link(query: str) -> dict[str, Any]:
    """Return a Google Shopping search link. Result format: {title, url, store, source}."""
    if not query.strip():
        return None
    url = "https://www.google.com/search?tbm=shop&q=" + urllib.parse.quote_plus(query)
    return {
        "title": query,
        "url": url,
        "store": "Google Shopping",
        "price": None,
        "image": None,
        "source": "google_shopping",
    }


def find_parts_and_tools(parts: list[str], tools: list[str]) -> dict[str, list[dict]]:
    """Search for parts and tools across public Shopify stores using SerpAPI.
    Fallback to Google Shopping if not found on Shopify.
    
    Return {parts: [...], tools: [...]} where each item is:
    {title, url, store, price, image, source: "shopify" or "google_shopping"}
    """
    parts = [p for p in (parts or []) if (p or "").strip()]
    tools = [t for t in (tools or []) if (t or "").strip()]
    
    out_parts: list[dict] = []
    for term in parts:
        # Search for Shopify stores selling this part
        stores = _search_shopify_stores(term)
        found = False
        for store in stores:
            products = _fetch_products_from_store(store, term)
            if products:
                out_parts.append(products[0])  # Take first match
                found = True
                break
        if not found:
            # Fallback to Google Shopping
            out_parts.append(_google_shopping_link(term))
    
    out_tools: list[dict] = []
    for term in tools:
        # Search for Shopify stores selling this tool
        stores = _search_shopify_stores(term)
        found = False
        for store in stores:
            products = _fetch_products_from_store(store, term)
            if products:
                out_tools.append(products[0])  # Take first match
                found = True
                break
        if not found:
            # Fallback to Google Shopping
            out_tools.append(_google_shopping_link(term))
    
    return {"parts": out_parts, "tools": out_tools}
