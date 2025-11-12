import os, sys, json
from datetime import datetime, timezone
from slugify import slugify
from openai import OpenAI

EMBED_MODEL = (os.environ.get("EMBED_MODEL") or "").strip() or "text-embedding-3-small"
GEN_MODEL   = (os.environ.get("GEN_MODEL") or "").strip() or "gpt-4o-mini"

def utcnow_iso(): return datetime.now(timezone.utc).isoformat()

def gen_chunks(client: OpenAI, topic: str, max_chunks: int = 3):
    system = ("Erzeuge prägnante, faktenbasierte Textabschnitte (Chunks) für ein Thema. "
              "Jeder Chunk 2–4 Sätze, klare Sprache. Keine Aufzählungslisten, kein Marketing.")
    user = (f"Thema: {topic}\nErzeuge {max_chunks} Chunks. Gib ein JSON-Array zurück, "
            f"mit Objekten: title, content, tags (Array kurzer Stichworte).")
    resp = client.chat.completions.create(
        model=GEN_MODEL,
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        temperature=0.2, max_tokens=800
    )
    text = resp.choices[0].message.content.strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1: raise ValueError("Antwort enthält kein JSON-Array.")
    return json.loads(text[start:end+1])[:max_chunks]

def embed_texts(client: OpenAI, texts):
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in resp.data]

def main():
    topic = (os.environ.get("TOPIC") or "").strip() or "Grundlagen der künstlichen Intelligenz"
    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        print("Fehler: OPENAI_API_KEY fehlt.", file=sys.stderr); sys.exit(2)
    max_chunks = int((os.environ.get("MAX_CHUNKS") or "3").strip() or "3")
    out_dir = (os.environ.get("OUT_DIR") or "/data").strip() or "/data"

    client = OpenAI(api_key=api_key)
    print(f"Thema: {topic} | Chunks: {max_chunks} | Modell: {EMBED_MODEL}")
    chunks = gen_chunks(client, topic, max_chunks=max_chunks)
    contents = [c.get("content","") for c in chunks]
    vecs = embed_texts(client, contents)

    created_at = utcnow_iso()
    doc_id = f"doc-{slugify(topic) or 'topic'}"
    out_points = []
    for i, (chunk, vec) in enumerate(zip(chunks, vecs), start=1):
        out_points.append({
            "id": i,
            "vector": vec,
            "payload": {
                "title":   chunk.get("title", f"Chunk {i}"),
                "content": chunk.get("content",""),
                "tags":    chunk.get("tags", []),
                "language": "de",
                "source": f"generated:{doc_id}",
                "doc_id": doc_id,
                "chunk_id": i,
                "chunk_count": len(chunks),
                "created_at": created_at,
                "topic": topic
            }
        })

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "points.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"points": out_points}, f, ensure_ascii=False, indent=2)
    print("Fertig. Datei:", out_path, "| Punkte:", len(out_points))

if __name__ == "__main__": main()
