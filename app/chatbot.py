import os, sys, json, re, requests
from textwrap import fill
from openai import OpenAI

OPENAI_API_KEY = (os.environ.get("OPENAI_API_KEY") or "").strip() or "PLEASE_SET_OR_USE_ENV"
QDRANT_URL     = (os.environ.get("QDRANT_URL") or "").strip() or "http://qdrant:6333"
COLLECTION     = (os.environ.get("QDRANT_COLLECTION") or "").strip() or "thema_ki"
EMBED_MODEL    = (os.environ.get("EMBED_MODEL") or "").strip() or "text-embedding-3-small"
TOP_K          = int((os.environ.get("TOP_K") or "").strip() or 5)
MIN_SCORE      = float((os.environ.get("MIN_SCORE") or "").strip() or 0.65)
WRAP_COLS      = int((os.environ.get("WRAP_COLS") or "").strip() or 100)

def fatal(msg: str, code: int = 2):
    print(f"Fehler: {msg}", file=sys.stderr); sys.exit(code)

def embed_query(client: OpenAI, text: str):
    resp = client.embeddings.create(model=EMBED_MODEL, input=[text])
    return resp.data[0].embedding

def qdrant_search(vector):
    import json, requests
    url = f"{QDRANT_URL}/collections/{COLLECTION}/points/search"
    body = {"vector": vector, "limit": TOP_K, "with_payload": True, "with_vector": False}
    r = requests.post(url, headers={"Content-Type":"application/json"}, data=json.dumps(body), timeout=60)
    if r.status_code >= 400: fatal(f"Qdrant-Suche fehlgeschlagen ({r.status_code}): {r.text}", 3)
    return r.json().get("result", [])

def answer_from_hits(hits):
    if not hits: return "Ich weiß es nicht auf Basis der vorhandenen Daten."
    if hits[0].get("score",0.0) < MIN_SCORE: return "Ich weiß es nicht auf Basis der vorhandenen Daten."
    lines=[]
    for i,h in enumerate(hits,1):
        p=h.get("payload",{}) or {}; s=h.get("score",0.0)
        title=p.get("title", f"Treffer {i}"); content=p.get("content","")
        source=p.get("source","unbekannt"); doc=p.get("doc_id","-"); cid=p.get("chunk_id","-")
        lines.append(f"[{i}] {title} (score={s:.3f})")
        if content: lines.append(fill(content, width=WRAP_COLS))
        lines.append(f"Quelle: {source} | doc_id={doc} | chunk={cid}"); lines.append("")
    return "\n".join(lines).strip()

def startup_check():
    import requests
    try:
        r = requests.get(f"{QDRANT_URL}/collections/{COLLECTION}", timeout=5)
        return r.status_code == 200
    except Exception: return False

def main():
    if not OPENAI_API_KEY or OPENAI_API_KEY == "PLEASE_SET_OR_USE_ENV":
        fatal("OPENAI_API_KEY fehlt. Bitte Secret/ENV setzen oder in chatbot.py eintragen.", 2)
    client = OpenAI(api_key=OPENAI_API_KEY)

    print("Console-Chatbot (Qdrant, nur Datenbankinhalte).")
    print("Frage eingeben und Enter drücken. Mit ':exit' beenden.")
    print(f"Collection: {COLLECTION} @ {QDRANT_URL}")
    print(f"Schwellwert (MIN_SCORE): {MIN_SCORE} | Top-K: {TOP_K}")
    if not startup_check(): print("Hinweis: Konnte Collection nicht sicher prüfen. Fahre dennoch fort.", file=sys.stderr)
    print("-"*60)

    try:
        while True:
            try: q = input("> ").strip()
            except (EOFError, KeyboardInterrupt): print("\nTschüss."); break
            if not q: continue
            if q.lower() in {":exit","exit","quit",":q"}: print("Tschüss."); break
            try:
                vec = embed_query(client, q)
            except Exception as e:
                print(f"Embedding-Fehler: {e}", file=sys.stderr); continue
            try:
                hits = qdrant_search(vec)
            except Exception as e:
                print(f"Qdrant-Fehler: {e}", file=sys.stderr); continue
            try:
                print("Top-Scores:", [ round(h.get("score",0.0),3) for h in hits ])
            except Exception: pass
            print(); print(answer_from_hits(hits)); print("-"*60)
    except Exception as e: fatal(f"Unerwarteter Fehler: {e}", 1)

if __name__ == "__main__": main()
