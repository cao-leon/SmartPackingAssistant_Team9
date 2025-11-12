import random

def get_weather(city: str) -> str:
    """
    Liefert eine einfache simulierte Wetterbeschreibung.
    """
    forecasts = [
        "sonnig und warm",
        "leicht bewölkt",
        "Regenschauer möglich",
        "bewölkt und kühl",
        "starker Regen",
        "heiß und trocken"
        "leichte schnee"
        "Starke schnee"
    ]

    random.seed(city.lower())  # Stadt → deterministisches Ergebnis
    return forecasts[random.randint(0, len(forecasts) - 1)]


def get_weather_forecast():
    return None