"""Product links: Shopify Storefront API (optional) or Google Shopping search links (no API key)."""
import logging
import urllib.parse
import httpx
from typing import Any

from backend.config import SHOPIFY_STORE_DOMAIN, SHOPIFY_STOREFRONT_TOKEN

logger = logging.getLogger(__name__)

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


def find_parts_and_tools(parts: list[str], tools: list[str], max_per_category: int = 3) -> dict[str, Any]:
    """Return {parts: [...], tools: [...], source: "shopify"|"google_shopping"}."""
    use_shopify = bool(SHOPIFY_STORE_DOMAIN and SHOPIFY_STOREFRONT_TOKEN)
    parts = [p for p in (parts or []) if (p or "").strip()]
    tools = [t for t in (tools or []) if (t or "").strip()]

    if not use_shopify:
        logger.info("Shopify not configured; using Google Shopping links for all terms")
        return {
            "parts": _google_shopping_links(parts),
            "tools": _google_shopping_links(tools),
            "source": "google_shopping",
        }

    shopify_hits = 0
    total_terms = 0

    out_parts: list[dict] = []
    for term in parts[:15]:
        total_terms += 1
        logger.info("Searching Shopify for part: %s", term)
        hits = search_products(term, first=1)
        if hits:
            logger.info("Shopify hit for part '%s': %s", term, hits[0].get("title"))
            shopify_hits += 1
            out_parts.append({"title": term, "url": hits[0]["url"]})
        else:
            logger.info("Shopify miss for part '%s', falling back to Google Shopping", term)
            out_parts.append({"title": term, "url": GOOGLE_SHOPPING_BASE + urllib.parse.quote_plus(term)})

    out_tools: list[dict] = []
    for term in tools[:15]:
        total_terms += 1
        logger.info("Searching Shopify for tool: %s", term)
        hits = search_products(term, first=1)
        if hits:
            logger.info("Shopify hit for tool '%s': %s", term, hits[0].get("title"))
            shopify_hits += 1
            out_tools.append({"title": term, "url": hits[0]["url"]})
        else:
            logger.info("Shopify miss for tool '%s', falling back to Google Shopping", term)
            out_tools.append({"title": term, "url": GOOGLE_SHOPPING_BASE + urllib.parse.quote_plus(term)})

    logger.info(
        "Shopify hits: %d/%d parts, %d/%d tools",
        sum(1 for p in out_parts if GOOGLE_SHOPPING_BASE not in p["url"]),
        len(out_parts),
        sum(1 for t in out_tools if GOOGLE_SHOPPING_BASE not in t["url"]),
        len(out_tools),
    )

    source = "shopify" if shopify_hits > 0 else "google_shopping"
    return {"parts": out_parts, "tools": out_tools, "source": source}
