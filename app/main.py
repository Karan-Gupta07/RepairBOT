from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.gemini_service import analyze_image
from app.shopify_service import find_parts_and_tools

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
    # Validate file type
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image (e.g. image/jpeg, image/png)")

    contents = await image.read()

    # Validate file size
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, "Image too large (max 10MB)")

    mime = image.content_type or "image/jpeg"

    # Analyze image with Gemini
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

    # Validate and coerce Gemini response
    repairability = repair.get("repairability", "medium")
    if repairability not in ("low", "medium", "high"):
        repairability = "medium"

    difficulty = repair.get("difficulty", "moderate")
    if difficulty not in ("easy", "moderate", "hard"):
        difficulty = "moderate"

    parts = repair.get("parts_needed") or []
    tools = repair.get("tools_needed") or []
    repair_steps = repair.get("repair_steps") or []

    if not isinstance(parts, list):
        parts = []
    if not isinstance(tools, list):
        tools = []
    if not isinstance(repair_steps, list):
        repair_steps = []

    # Search for products
    products = find_parts_and_tools(parts, tools)
    
    # Calculate actual cost from Shopify products
    shopify_items = []
    for part in products.get("parts", []):
        if part.get("source") == "shopify" and part.get("price"):
            shopify_items.append(float(part.get("price", 0)))
    for tool in products.get("tools", []):
        if tool.get("source") == "shopify" and tool.get("price"):
            shopify_items.append(float(tool.get("price", 0)))
    
    actual_cost = round(sum(shopify_items), 2) if shopify_items else None
    cost_estimate_note = None
    if actual_cost is not None:
        cost_estimate_note = f"Based on {len(shopify_items)} Shopify products found"
    
    return {
        "repairability": repairability,
        "difficulty": difficulty,
        "estimated_time": repair.get("estimated_time"),
        "estimated_cost_usd": actual_cost,  # Use actual Shopify prices instead of Gemini estimate
        "cost_estimate_note": cost_estimate_note,
        "brief_description": repair.get("brief_description"),
        "repair_steps": repair_steps,
        "parts_needed": parts,
        "tools_needed": tools,
        "products": products,
    }
