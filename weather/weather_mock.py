import os, json
from fastapi import FastAPI
from pydantic import BaseModel
from dateutil.parser import isoparse

app = FastAPI(title="Weather Mock")
DATA_PATH = os.getenv("WEATHER_DATA_PATH", "data/weather_dummy.json")

class WxOut(BaseModel):
    city: str; start: str; end: str
    summary: str; avg_tmin: float; avg_tmax: float; rain_prob: float
    uncertainty: str

def _bucket(tmax: float) -> str:
    return "warm" if tmax >= 26 else ("cold" if tmax <= 10 else "mild")

@app.get("/health")
def health(): return {"ok": True}

@app.get("/v1/weather", response_model=WxOut)
def weather(city: str, start: str, end: str):
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    s = isoparse(start).date(); e = isoparse(end).date()
    months = list({s.month, e.month}) if s.month != e.month else [s.month]
    if city in db:
        m = db[city]["monthly"]
        tmins = [m[f"{mm:02d}"]["tmin"] for mm in months]
        tmaxs = [m[f"{mm:02d}"]["tmax"] for mm in months]
        rains = [m[f"{mm:02d}"]["rain"] for mm in months]
        avg_tmin = round(sum(tmins)/len(tmins), 1)
        avg_tmax = round(sum(tmaxs)/len(tmaxs), 1)
        rain = round(sum(rains)/len(rains), 2)
        return {"city": city, "start": str(s), "end": str(e),
                "summary": _bucket(avg_tmax), "avg_tmin": avg_tmin,
                "avg_tmax": avg_tmax, "rain_prob": rain,
                "uncertainty": "Dummy-Klimadaten (Monatsmittel)"}
    mm = s.month
    summary = "warm" if 6 <= mm <= 9 else ("cold" if mm in (12,1,2) else "mild")
    return {"city": city, "start": str(s), "end": str(e),
            "summary": summary, "avg_tmin": 0.0, "avg_tmax": 0.0,
            "rain_prob": 0.30, "uncertainty": "Stadt nicht in Dummy-Daten – generischer Saison-Bucket"}
