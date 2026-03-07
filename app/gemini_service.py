"""Analyze repair images with Gemini and return structured repair info."""
import json
import os
import re
import time
from typing import Any

import google.generativeai as genai

from app.config import GEMINI_API_KEY

MAX_RETRIES = 3
RETRY_BACKOFF_SEC = [2, 6, 15]  # wait before retry 1, 2, 3

# Expect Gemini to return JSON including:
# "repair_steps": ["Step 1...", "Step 2..."] - detailed step-by-step instructions

SYSTEM_PROMPT = """You are a repair assistant. The user will send a photo of a broken object.
Analyze the image and respond with ONLY a valid JSON object (no markdown, no extra text) with these exact keys:
- "repairability": one of "low", "medium", "high"
- "difficulty": one of "easy", "moderate", "hard" (how hard for a DIYer to do the repair)
- "estimated_time": string estimate e.g. "15 min", "30-60 min", "1-2 hours", "half day". Be brief.
- "estimated_cost_usd": number or null if unknown
- "brief_description": 1-2 sentences about the damage and repair
- "repair_steps": array of 4-10 clear, numbered step-by-step repair instructions. Each step one short sentence. Order matters (safety first, then disassembly, replace/repair, reassembly, test). Be specific to what you see in the image.
- "parts_needed": array of 2-5 specific part names someone would search to buy (e.g. "office chair caster wheel", "replacement gas cylinder"). Use search-friendly phrases.
- "tools_needed": array of 2-5 tool names (e.g. "Phillips screwdriver", "adjustable wrench"). Use search-friendly phrases.

Important: repair_steps must be actionable steps a DIYer can follow. Always suggest concrete parts and tools when repairability is medium or high. Keep part and tool names short and searchable."""


def _is_rate_limit_error(e: Exception) -> bool:
    msg = (getattr(e, "message", "") or str(e)).lower()
    return "429" in msg or "resource exhausted" in msg or "quota" in msg or "rate limit" in msg


def analyze_image(image_bytes: bytes, mime_type: str) -> dict[str, Any]:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")
    genai.configure(api_key=GEMINI_API_KEY)
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    model = genai.GenerativeModel(model_name)
    image_part = {"inline_data": {"mime_type": mime_type, "data": image_bytes}}

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(
                [SYSTEM_PROMPT, image_part],
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                ),
            )
            text = (response.text or "").strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            return json.loads(text)
        except Exception as e:
            last_error = e
            if _is_rate_limit_error(e) and attempt < MAX_RETRIES - 1:
                delay = RETRY_BACKOFF_SEC[attempt] if attempt < len(RETRY_BACKOFF_SEC) else 15
                time.sleep(delay)
                continue
            raise

    raise last_error or RuntimeError("Analysis failed")
