from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class WeatherRequest(BaseModel):
    city: str
    days: int = 3  # Default-Wert

def generate_weather(city: str, days: int):

    forecast_map = {
        "berlin": "bewölkt und kühl",
        "amsterdam": "windig und feucht",
        "dubai": "sehr heiß und sonnig",
        "oslo": "kalt mit leichtem Schnee",
        "madrid": "warm und sonnig"
    }

    city_lower = city.lower()
    forecast = forecast_map.get(city_lower, "wechselhaft")

    packing_list = []

    if "kalt" in forecast or "schnee" in forecast:
        packing_list += ["Winterjacke", "Handschuhe", "Schal", "Wärmende Schuhe"]

    if "heiß" in forecast or "sonnig" in forecast:
        packing_list += ["Sonnencreme", "Sonnenbrille", "Leichte Kleidung", "Trinkflasche"]

    if "windig" in forecast or "feucht" in forecast:
        packing_list += ["Windjacke", "Wasserdichte Schuhe"]

    packing_list.append(f"Kleidung für {days} Tage")

    return {
        "city": city,
        "forecast": forecast,
        "recommendations": packing_list
    }


# POST - JSON Body
@app.post("/weather")
def weather_post(request: WeatherRequest):
    return generate_weather(request.city, request.days)


# GET - Query Parameter (days optional)
@app.get("/weather")
def weather_get(city: str, days: int = 3):
    return generate_weather(city, days)
