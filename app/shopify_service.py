"""Product links: Shopify Storefront API (optional) or Google Shopping search links (no API key)."""
import urllib.parse
import httpx
from typing import Any

from app.config import SHOPIFY_STORE_DOMAIN, SHOPIFY_STOREFRONT_TOKEN

GOOGLE_SHOPPING_BASE = "https://www.google.com/search?tbm=shop&q="

def _graphql_url() -> str:
    if not SHOPIFY_STORE_DOMAIN:
        return ""
    return f"https://{SHOPIFY_STORE_DOMAIN}/api/2024-01/graphql.json"

SEARCH_QUERY = """
query searchProducts($query: String!, $first: Int) {
  search(query: $query, first: $first, types: PRODUCT) {
    nodes {
      ... on Product {
        title
        handle
        onlineStoreUrl
        variants(first: 1) {
          nodes {
            id
          }
        }
      }
    }
  }
}
"""


def search_products(query: str, first: int = 5) -> list[dict[str, Any]]:
    """Return list of {title, url} for products matching query."""
    if not SHOPIFY_STORE_DOMAIN or not SHOPIFY_STOREFRONT_TOKEN:
        return []
    url = _graphql_url()
    if not url:
        return []
    payload = {"query": SEARCH_QUERY, "variables": {"query": query, "first": first}}
    headers = {"X-Shopify-Storefront-Access-Token": SHOPIFY_STOREFRONT_TOKEN, "Content-Type": "application/json"}
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return []
    nodes = (data.get("data") or {}).get("search", {}).get("nodes") or []
    base = f"https://{SHOPIFY_STORE_DOMAIN}"
    results = []
    for node in nodes:
        title = node.get("title") or "Product"
        handle = node.get("handle")
        online_url = node.get("onlineStoreUrl")
        url = online_url if online_url else (f"{base}/products/{handle}" if handle else None)
        if url:
            results.append({"title": title, "url": url})
    return results


def _google_shopping_links(terms: list[str]) -> list[dict[str, Any]]:
    """Return one search link per term (no API key)."""
    out = []
    for term in terms:
        term = (term or "").strip()
        if not term:
            continue
        url = GOOGLE_SHOPPING_BASE + urllib.parse.quote_plus(term)
        out.append({"title": term, "url": url})
    return out


def find_parts_and_tools(parts: list[str], tools: list[str], max_per_category: int = 3) -> dict[str, list[dict]]:
    """Return {parts: [...], tools: [...]} — exactly one link per part and one per tool (title + url)."""
    use_shopify = bool(SHOPIFY_STORE_DOMAIN and SHOPIFY_STOREFRONT_TOKEN)
    parts = [p for p in (parts or []) if (p or "").strip()]
    tools = [t for t in (tools or []) if (t or "").strip()]

    if use_shopify:
        out_parts: list[dict] = []
        for term in parts[:15]:
            hits = search_products(term, first=1)
            out_parts.append({"title": term, "url": hits[0]["url"]} if hits else {"title": term, "url": GOOGLE_SHOPPING_BASE + urllib.parse.quote_plus(term)})
        out_tools: list[dict] = []
        for term in tools[:15]:
            hits = search_products(term, first=1)
            out_tools.append({"title": term, "url": hits[0]["url"]} if hits else {"title": term, "url": GOOGLE_SHOPPING_BASE + urllib.parse.quote_plus(term)})
        return {"parts": out_parts, "tools": out_tools}

    # One Google Shopping link per part and per tool
    return {
        "parts": _google_shopping_links(parts),
        "tools": _google_shopping_links(tools),
    }
