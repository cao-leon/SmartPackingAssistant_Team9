import os
import httpx
from fastapi import HTTPException
from openai import OpenAI

# ✅ API Key NICHT im Code speichern!
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("FEHLER: OPENAI_API_KEY ist nicht gesetzt. Bitte Umgebungsvariable setzen!")

client = OpenAI(api_key=OPENAI_API_KEY)

WEATHER_URL = os.getenv("WEATHER_URL", "http://weather-service:8090")

async def generate_chat_response(message: str, profile: str):
    """
    Fragt ein OpenAI-Modell (GPT-4 / GPT-4o-mini / GPT-3.5 abhängig vom Key) und gibt die Textantwort zurück.
    """

    prompt = f"""
Du bist ein hilfreicher Smart Packing Assistant.

Profil des Nutzers: {profile}

Aufgabe:
- Antworte kurz, klar und freundlich.
- Wenn möglich: gib konkrete Empfehlungen zum Einpacken.
- Wenn der Nutzer unklar fragt, stelle 1 Rückfrage.

Nachricht vom Nutzer:
"{message}"

Antwort:
"""

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }

    body = {
        "model": "gpt-4o-mini",   # funktioniert mit jedem PROJ-Key
        "messages": [
            {"role": "system", "content": "Du bist ein hilfreicher Reise-Packassistent."},
            {"role": "user", "content": prompt}
        ]
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=headers, json=body)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Fehler bei Anfrage: " + response.text)

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
