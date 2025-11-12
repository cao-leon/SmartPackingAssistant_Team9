import os, re, random
import httpx
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from dateutil.parser import isoparse
from rapidfuzz import fuzz
from loader import load_json
from rules import weather_to_bucket, quantities, activity_items
from ai_service import generate_chat_response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="Smart Packing Assistant API", version="0.2.0")
WEATHER_URL = os.getenv("WEATHER_URL", "http://127.0.0.1:8090")

# JSON-Daten laden
INTENTS = load_json("intents.json", required=False) or {"intents": []}
PROFILES = load_json("profiles.json", required=False) or {"minimal": 1.0, "komfort": 1.2, "familie": 1.4}

class PackReq(BaseModel):
    city: str
    start: str
    end: str
    activities: List[str] = []
    profile: str = "minimal"

class ChatIn(BaseModel):
    message: str
    profile: Optional[str] = "minimal"

@app.get("/health")
def health():
    return {"ok": True, "service": "api"}


# -------------------------
# ✅ NEUE KI CHAT LOGIK
# -------------------------
@app.post("/v1/chat")
async def chat(inp: ChatIn):
    reply = await generate_chat_response(inp.message, inp.profile)
    return {"reply": reply}


async def fetch_weather(city: str, start: str, end: str):
    async with httpx.AsyncClient(timeout=3.0) as c:
        r = await c.get(f"{WEATHER_URL}/v1/weather", params={"city": city, "start": start, "end": end})
        r.raise_for_status()
        return r.json()


@app.post("/v1/packlist")
async def packlist(req: PackReq):
    try:
        s = isoparse(req.start).date(); e = isoparse(req.end).date()
        days = max(1, (e - s).days or 1)
    except Exception:
        return {"error": "Ungültiges Datum. Format YYYY-MM-DD."}

    try:
        wx = await fetch_weather(req.city, req.start, req.end)
    except Exception:
        wx = None

    if not wx:
        bucket = "mild"; avg_tmax = None; rain = None
        uncertainty = "Wetterdienst nicht erreichbar – generischer Bucket."
    else:
        bucket = weather_to_bucket(wx.get("summary", "mild"))
        avg_tmax = wx.get("avg_tmax"); rain = wx.get("rain_prob")
        uncertainty = wx.get("uncertainty", "—")

    factor = float(PROFILES.get(req.profile, 1.0))
    q = quantities(days, bucket, factor)
    items = [
        {"name": "Reisepass/ID", "qty": 1, "critical": True},
        {"name": "T-Shirts", "qty": q["tshirts"]},
        {"name": "Unterwäsche", "qty": q["underwear"]},
        {"name": "Socken", "qty": q["socks"]},
        {"name": "Leichte Jacke", "qty": q["jacket"]},
        {"name": "Sonnencreme", "qty": 1}
    ] + activity_items(req.activities)

    if avg_tmax is not None and avg_tmax <= 10:
        items += [{"name": "Warme Jacke", "qty": 1}, {"name": "Mütze/Handschuhe", "qty": 1}]
    if rain is not None and rain >= 0.4:
        items += [{"name": "Regenjacke", "qty": 1}, {"name": "Regenhülle Rucksack", "qty": 1}]

    return {"city": req.city, "days": days, "profile": req.profile,
            "weather": {"bucket": bucket, "avg_tmax": avg_tmax, "rain_prob": rain},
            "items": items, "uncertainty": uncertainty}

# ✅ STATIC FILES (UI)
# ✅ STATIC FILES (UI)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/chat")
def chat_page():
    return FileResponse(os.path.join("static", "chat.html"))

@app.get("/v1/packlist")
async def packlist_get(
        city: str,
        start: str,
        end: str,
        activities: str = "",
        profile: str = "minimal",
):
    req = PackReq(
        city=city,
        start=start,
        end=end,
        activities=[a for a in activities.split(",") if a],
        profile=profile,
    )
    return await packlist(req)
