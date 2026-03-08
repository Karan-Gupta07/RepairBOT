"""Search public Shopify stores using SerpAPI and fetch products via public JSON endpoints."""
import httpx
import urllib.parse
from typing import Any
import re

from app.config import SERPAPI_API_KEY


def _serpapi_shopping_search(query: str, num: int = 5) -> list[dict[str, Any]]:
    """Search Google Shopping via SerpAPI, filtered to Shopify stores.
    Returns list of {title, price, link, thumbnail, source, store_domain}.
    Prioritized path for discovering Shopify products.
    """
    if not SERPAPI_API_KEY:
        return []

    params = {
        "engine": "google_shopping",
        "q": f"{query} site:myshopify.com",
        "api_key": SERPAPI_API_KEY,
        "num": num,
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get("https://serpapi.com/search.json", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return []

    results = []
    for item in (data.get("shopping_results") or [])[:num]:
        link = item.get("link") or item.get("product_link") or ""
        store_domain = _extract_shopify_domain(link)
        results.append({
            "title": item.get("title") or query,
            "price": item.get("extracted_price") or item.get("price") or None,
            "link": link,
            "thumbnail": item.get("thumbnail") or None,
            "source": item.get("source") or "",
            "store_domain": store_domain,
        })
    return results


def _extract_shopify_domain(url: str) -> str | None:
    """Extract the myshopify.com domain from a URL, if present."""
    try:
        host = urllib.parse.urlparse(url).hostname or ""
        if "myshopify.com" in host:
            return host
    except Exception:
        pass
    return None


def _shopify_search_suggest(store_domain: str, query: str, limit: int = 3) -> list[dict[str, Any]]:
    """Search a Shopify store using the public search suggest endpoint.
    Returns list of {title, price, url, image, store, source}.
    """
    if not store_domain:
        return []

    suggest_url = f"https://{store_domain}/search/suggest.json"
    params = {
        "q": query,
        "resources[type]": "product",
        "resources[limit]": limit,
    }
    try:
        with httpx.Client(timeout=8.0) as client:
            r = client.get(suggest_url, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return []

    products = (
        (data.get("resources") or {}).get("results") or {}
    ).get("products") or []

    results = []
    for p in products:
        price = p.get("price") or ""
        if price and "." not in str(price):
            try:
                price = f"${float(price) / 100:.2f}"
            except (ValueError, TypeError):
                price = f"${price}"
        elif price:
            price = f"${price}"

        image = p.get("image") or p.get("featured_image", {}).get("url") or None
        if image and image.startswith("//"):
            image = "https:" + image

        results.append({
            "title": p.get("title") or query,
            "price": price or None,
            "url": f"https://{store_domain}{p.get('url', '')}",
            "image": image,
            "store": store_domain,
            "source": "shopify",
        })
    return results


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


def _search_single_product(term: str) -> dict[str, Any]:
    """Search for a single product. Prioritizes Shopify via SerpAPI, then fallbacks."""
    term = (term or "").strip()
    if not term:
        return _google_shopping_link(term)

    # Step 1: SerpAPI google_shopping (prioritized) - discover Shopify products directly
    serp_results = _serpapi_shopping_search(term, num=5)

    # Step 2: For Shopify domains found, enrich with Shopify search suggest
    for result in serp_results:
        domain = result.get("store_domain")
        if domain:
            suggest = _shopify_search_suggest(domain, term, limit=1)
            if suggest:
                return suggest[0]

    # Step 3: If SerpAPI found Shopify results but no suggest match, use best SerpAPI result
    shopify_serp = [r for r in serp_results if r.get("store_domain")]
    if shopify_serp:
        best = shopify_serp[0]
        return {
            "title": best.get("title") or term,
            "price": best.get("price"),
            "url": best.get("link") or "",
            "image": best.get("thumbnail"),
            "store": best.get("store_domain") or best.get("source") or "Shopify",
            "source": "shopify",
        }

    # Step 4: If SerpAPI found any results, use best one
    if serp_results:
        best = serp_results[0]
        return {
            "title": best.get("title") or term,
            "price": best.get("price"),
            "url": best.get("link") or "https://www.google.com/search?tbm=shop&q=" + urllib.parse.quote_plus(term),
            "image": best.get("thumbnail"),
            "store": best.get("source") or "Online",
            "source": "serpapi",
        }

    # Step 5: Fallback - SerpAPI organic search + products.json
    stores = _search_shopify_stores(term)
    for store in stores:
        products = _fetch_products_from_store(store, term)
        if products:
            return products[0]

    # Step 6: Final fallback - Google Shopping link
    return _google_shopping_link(term)


def find_parts_and_tools(parts: list[str], tools: list[str]) -> dict[str, list[dict]]:
    """Search for parts and tools. Prioritizes Shopify via SerpAPI (google_shopping), then fallbacks.
    
    Return {parts: [...], tools: [...]} where each item is:
    {title, url, store, price, image, source: "shopify" | "serpapi" | "google_shopping"}
    """
    parts = [p for p in (parts or []) if (p or "").strip()]
    tools = [t for t in (tools or []) if (t or "").strip()]

    out_parts = [_search_single_product(term) for term in parts]
    out_tools = [_search_single_product(term) for term in tools]

    return {"parts": out_parts, "tools": out_tools}
