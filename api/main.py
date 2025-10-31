import os, re, random
import httpx
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from dateutil.parser import isoparse
from rapidfuzz import fuzz
from api.loader import load_json
from api.rules import weather_to_bucket, quantities, activity_items

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

def best_intent(msg: str):
    cand = []
    for intent in INTENTS["intents"]:
        for pat in intent.get("patterns", []):
            cand.append((fuzz.token_set_ratio(msg.lower(), pat.lower()), intent))
    return max(cand, key=lambda x: x[0]) if cand else (0, None)

def extract_slots(text: str):
    city = None; days = None; season = None
    m = re.search(r"(?:nach|in)\s+([A-ZÄÖÜ][\wÄÖÜäöüß\-]+)", text)
    if m: city = m.group(1)
    m2 = re.search(r"(\d+)\s*(?:tage|tag|nächte)", text, re.I)
    if m2: days = int(m2.group(1))
    for s in ["Frühling", "Sommer", "Herbst", "Winter"]:
        if s.lower() in text.lower(): season = s
    return city, days, season

@app.post("/v1/chat")
def chat(inp: ChatIn):
    score, intent = best_intent(inp.message)
    if intent and score >= intent.get("threshold", 70):
        reply = random.choice(intent.get("reply_variants", [""]))
        note  = " " + random.choice(intent.get("notes", [])) if intent.get("notes") else ""
        return {"reply": (reply + note).strip()}
    if "packliste" in inp.message.lower() or "einpacken" in inp.message.lower():
        city, days, season = extract_slots(inp.message)
        if not city or not days:
            return {"reply": "Bitte nenne Stadt und Tage (z. B. „Packliste für Barcelona, 4 Tage, im Sommer“)."}
        bucket = {"Sommer": "warm", "Winter": "cold"}.get(season, "mild")
        factor = float(PROFILES.get(inp.profile or "minimal", 1.0))
        q = quantities(days, bucket, factor)
        items = [
            {"name": "Reisepass/ID", "qty": 1, "critical": True},
            {"name": "T-Shirts", "qty": q["tshirts"]},
            {"name": "Unterwäsche", "qty": q["underwear"]},
            {"name": "Socken", "qty": q["socks"]},
            {"name": "Leichte Jacke", "qty": q["jacket"]},
            {"name": "Sonnencreme", "qty": 1}
        ]
        return {"city": city, "days": days, "weather": bucket,
                "items": items, "uncertainty": "Saisonbasiert; ohne Dummy-Wetterdetails."}
    return {"reply": "Dazu habe ich keine Vorlage. Frag nach Packliste oder Handgepäck-Regeln."}

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
