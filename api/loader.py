import os, json
DATA_DIR = os.getenv("DATA_DIR", "data")

def load_json(name: str, required: bool = True):
    path = os.path.join(DATA_DIR, name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if required:
            raise
        return None
