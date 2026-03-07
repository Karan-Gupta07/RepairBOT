from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.gemini_service import analyze_image
from app.shopify_service import find_parts_and_tools

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

app = FastAPI(title="RepairBOT")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
DIST_DIR = os.path.join(FRONTEND_DIR, "dist")


@app.get("/")
async def root():
    dist_index = os.path.join(DIST_DIR, "index.html")
    if os.path.isfile(dist_index):
        return FileResponse(dist_index)
    fallback = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(fallback):
        return FileResponse(fallback)
    return {"message": "RepairBOT API. Use POST /analyze with an image."}


@app.post("/analyze")
async def analyze_repair(image: UploadFile = File(...)):
    if not image.content_type or image.content_type not in ALLOWED_MIME_TYPES:
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


# Static files mount — must be after all route definitions.
# Prefer built React app (frontend/dist/), fall back to raw frontend/ dir.
if os.path.isdir(DIST_DIR):
    app.mount("/", StaticFiles(directory=DIST_DIR), name="spa")
elif os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
