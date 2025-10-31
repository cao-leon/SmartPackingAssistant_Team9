from typing import List, Dict

def weather_to_bucket(summary: str) -> str:
    s = (summary or "").lower()
    if "warm" in s or "hot" in s or "heiß" in s:
        return "warm"
    if "cold" in s or "kalt" in s or "winter" in s:
        return "cold"
    return "mild"

def quantities(days: int, bucket: str, factor: float = 1.0) -> Dict[str, int]:
    base = max(2, min(6, days))
    tshirts = base + (1 if bucket == "warm" else 0)
    underwear = days
    socks = days
    jacket = 0 if bucket == "warm" else 1
    def f(x: int) -> int: return max(1, int(round(x * factor)))
    return {"tshirts": f(tshirts), "underwear": f(underwear), "socks": f(socks), "jacket": f(jacket)}

def activity_items(activities: List[str]) -> List[dict]:
    acts = set(a.lower() for a in (activities or []))
    extra = []
    if "beach" in acts or "strand" in acts:
        extra += [{"name": "Badesachen", "qty": 1}, {"name": "Flip-Flops", "qty": 1}]
    if "hiking" in acts or "wandern" in acts:
        extra += [{"name": "Wanderschuhe", "qty": 1}, {"name": "Regenhülle Rucksack", "qty": 1}]
    if "business" in acts or "arbeit" in acts:
        extra += [{"name": "Business-Outfit", "qty": 1}, {"name": "Ladegeräte/Laptop", "qty": 1}]
    return extra
