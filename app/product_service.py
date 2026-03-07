"""Product discovery: SerpAPI finds Shopify stores, then Shopify search suggest returns product details."""
import urllib.parse
from typing import Any

import httpx

from app.config import SERPAPI_API_KEY

GOOGLE_SHOPPING_BASE = "https://www.google.com/search?tbm=shop&q="


def _serpapi_shopping_search(query: str, num: int = 5) -> list[dict[str, Any]]:
    """Search Google Shopping via SerpAPI, filtered to Shopify stores.
    Returns list of {title, price, link, thumbnail, source, store_domain}.
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
    Returns list of {title, price, url, image, store}.
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
        # Shopify returns price in cents-string like "1999" or formatted "19.99"
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
        })
    return results


def _google_shopping_link(term: str) -> dict[str, Any]:
    """Fallback: plain Google Shopping search link."""
    return {
        "title": term,
        "price": None,
        "url": GOOGLE_SHOPPING_BASE + urllib.parse.quote_plus(term),
        "image": None,
        "store": "Google Shopping",
    }


def search_product(term: str) -> dict[str, Any]:
    """Search for a single product term. Tries SerpAPI → Shopify suggest → Google Shopping fallback."""
    term = (term or "").strip()
    if not term:
        return _google_shopping_link(term)

    # Step 1: SerpAPI discovers Shopify stores selling this product
    serp_results = _serpapi_shopping_search(term, num=5)

    # Step 2: For stores found on Shopify, get richer product details
    for result in serp_results:
        domain = result.get("store_domain")
        if domain:
            suggest = _shopify_search_suggest(domain, term, limit=1)
            if suggest:
                return suggest[0]

    # Step 3: If SerpAPI found results but no Shopify domains, use the best SerpAPI result
    if serp_results:
        best = serp_results[0]
        return {
            "title": best.get("title") or term,
            "price": best.get("price"),
            "url": best.get("link") or (GOOGLE_SHOPPING_BASE + urllib.parse.quote_plus(term)),
            "image": best.get("thumbnail"),
            "store": best.get("source") or "Online",
        }

    # Step 4: Fallback to plain Google Shopping link
    return _google_shopping_link(term)


def find_parts_and_tools(parts: list[str], tools: list[str]) -> dict[str, Any]:
    """Search for all parts and tools. Returns {parts: [...], tools: [...], source: ...}."""
    parts = [p for p in (parts or []) if (p or "").strip()]
    tools = [t for t in (tools or []) if (t or "").strip()]

    out_parts = [search_product(term) for term in parts]
    out_tools = [search_product(term) for term in tools]

    # Determine source based on what we found
    has_shopify = any(
        "myshopify.com" in (p.get("store") or "")
        for p in out_parts + out_tools
    )

    return {
        "parts": out_parts,
        "tools": out_tools,
        "source": "shopify" if has_shopify else ("serpapi" if SERPAPI_API_KEY else "google_shopping"),
    }
