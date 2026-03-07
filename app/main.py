from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.gemini_service import analyze_image
from app.shopify_service import find_parts_and_tools
from app.config import SHOPIFY_STORE_DOMAIN, SHOPIFY_STOREFRONT_TOKEN

app = FastAPI(title="RepairBOT")

# Serve frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def root():
    index = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(index):
        return FileResponse(index)
    return {"message": "RepairBOT API. Use POST /analyze with an image."}


@app.post("/analyze")
async def analyze_repair(image: UploadFile = File(...)):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image (e.g. image/jpeg, image/png)")
    contents = await image.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, "Image too large (max 10MB)")
    mime = image.content_type or "image/jpeg"
    try:
        repair = analyze_image(contents, mime)
    except ValueError as e:
        raise HTTPException(500, str(e))
    except Exception as e:
        msg = str(e).lower()
        if "429" in msg or "resource exhausted" in msg or "quota" in msg:
            raise HTTPException(
                503,
                "Gemini rate limit reached. Please wait a minute or two and try again. "
                "Free-tier quotas reset over time.",
            )
        raise HTTPException(500, f"Analysis failed: {e}")
    parts = repair.get("parts_needed") or []
    tools = repair.get("tools_needed") or []
    products = find_parts_and_tools(parts, tools)
    products["source"] = "shopify" if (SHOPIFY_STORE_DOMAIN and SHOPIFY_STOREFRONT_TOKEN) else "google_shopping"
    return {
        "repairability": repair.get("repairability"),
        "difficulty": repair.get("difficulty"),
        "estimated_time": repair.get("estimated_time"),
        "estimated_cost_usd": repair.get("estimated_cost_usd"),
        "brief_description": repair.get("brief_description"),
        "repair_steps": repair.get("repair_steps") or [],
        "parts_needed": parts,
        "tools_needed": tools,
        "products": products,
    }
