#!/usr/bin/env python3
"""M5b: build the semantic (vector) index for the Second Brain.

Embeds every chunk in my_rag_data.db using the local free Ollama model
'nomic-embed-text' (768 dims) into a new chunk_embeddings table.

Crash-safe: fully resumable — already-embedded chunks are skipped, progress
commits after every batch. Safe to interrupt and re-run at any time.
"""
import json
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "Processed_Assets" / "my_rag_data.db"
MODEL = "nomic-embed-text"
DIM = 768
BATCH = 64
OLLAMA_URL = "http://localhost:11434/api/embed"


def embed_batch(texts):
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps({"model": MODEL, "input": texts}).encode(),
        headers={"Content-Type": "application/json"},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read())
            embs = d.get("embeddings")
            if embs:
                return embs
        except Exception as e:
            wait = 2 ** attempt
            print(f"    [warn] embed call failed ({e}); retry in {wait}s", flush=True)
            time.sleep(wait)
    raise RuntimeError("embedding failed after retries")


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS chunk_embeddings (
               chunk_id INTEGER PRIMARY KEY,
               model TEXT NOT NULL,
               dim INTEGER NOT NULL,
               embedding BLOB NOT NULL
           )"""
    )
    conn.commit()

    done = {
        r[0]
        for r in conn.execute("SELECT chunk_id FROM chunk_embeddings WHERE model=?", (MODEL,))
    }
    total_rows = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    todo = total_rows - len(done)
    print(f"chunks: {total_rows} | already embedded: {len(done)} | remaining: {todo}")
    if todo == 0:
        print("Semantic index is complete. Nothing to do.")
        return

    cur = conn.execute("SELECT id, chunk_text FROM chunks ORDER BY id")
    t0 = time.time()
    processed = 0
    buffer_texts, buffer_ids = [], []

    def flush():
        nonlocal buffer_texts, buffer_ids, processed
        if not buffer_ids:
            return
        embs = embed_batch(buffer_texts)
        arr = np.asarray(embs, dtype=np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        arr = arr / norms
        conn.executemany(
            "INSERT OR REPLACE INTO chunk_embeddings VALUES (?,?,?,?)",
            [
                (cid, MODEL, DIM, row.astype(np.float32).tobytes())
                for cid, row in zip(buffer_ids, arr)
            ],
        )
        conn.commit()
        processed += len(buffer_ids)
        rate = processed / max(time.time() - t0, 0.001)
        eta = (todo - processed) / max(rate, 0.001) / 60.0
        print(f"  [{len(done)+processed}/{total_rows}] embedded | {rate:.1f}/s | ETA {eta:.1f} min", flush=True)
        buffer_texts, buffer_ids = [], []

    for cid, text in cur:
        if cid in done:
            continue
        buffer_ids.append(cid)
        buffer_texts.append(text[:8000])
        if len(buffer_ids) >= BATCH:
            flush()
    flush()
    conn.close()
    print(f"DONE. embedded {processed} new chunks this run.")


if __name__ == "__main__":
    main()
