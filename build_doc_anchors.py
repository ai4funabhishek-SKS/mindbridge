#!/usr/bin/env python3
"""Build document-level anchor embeddings (title + purpose + tags + tier + topic).

Creates/refreshes the doc_anchors table in the RAG database:
    doc_anchors(doc_id INTEGER PRIMARY KEY, model TEXT, embedding BLOB)

Each anchor is an L2-normalised float32 vector over a compact text that
describes the whole document. Resumable and idempotent: documents that
already have an embedding for the current model are skipped.
"""
import json
import sqlite3
import sys
import time
import urllib.request

import numpy as np

BASE_DIR = __import__("pathlib").Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "Processed_Assets" / "my_rag_data.db"

EMBED_MODEL = "nomic-embed-text"
OLLAMA_URL = "http://localhost:11434/api/embed"
BATCH_SIZE = 32
ANCHOR_MAX_CHARS = 2000


def build_anchor_text(row: dict) -> str:
    """Composes the compact fingerprint text for one document."""
    parts = [
        row.get("asset_title") or "",
        row.get("problem_solved") or "",
        row.get("tags") or "",
        row.get("rating_tier") or "",
        row.get("topic") or "",
    ]
    text = " | ".join(p.strip() for p in parts if p and p.strip())
    return text[:ANCHOR_MAX_CHARS]


def _embed_batch(texts):
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps({"model": EMBED_MODEL, "input": texts}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read())
    embs = d.get("embeddings")
    if not embs or len(embs) != len(texts):
        raise RuntimeError(f"Ollama returned {len(embs or [])} embeddings for {len(texts)} inputs")
    out = []
    for e in embs:
        vec = np.asarray(e, dtype=np.float32)
        norm = np.linalg.norm(vec)
        out.append((vec / norm if norm > 0 else vec).tobytes())
    return out


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS doc_anchors (
                   doc_id INTEGER PRIMARY KEY,
                   model TEXT NOT NULL,
                   embedding BLOB NOT NULL)"""
        )
        docs = conn.execute(
            """SELECT id, asset_title, problem_solved, tags, rating AS rating_tier, topic
               FROM documents ORDER BY id"""
        ).fetchall()
        done = {
            rid for (rid,) in conn.execute(
                "SELECT doc_id FROM doc_anchors WHERE model=?", (EMBED_MODEL,)
            )
        }
        pending = [(rid, build_anchor_text(dict(
            zip(("asset_title", "problem_solved", "tags", "rating_tier", "topic"), vals[1:])
        ))) for rid, *vals in ((d[0],) + tuple(d[1:]) for d in docs) if rid not in done]

        total = len(docs)
        print(f"{total} documents | {len(done)} already anchored | {len(pending)} to embed")
        t0 = time.time()
        for i in range(0, len(pending), BATCH_SIZE):
            batch = pending[i:i + BATCH_SIZE]
            blobs = _embed_batch([txt for _, txt in batch])
            conn.executemany(
                "INSERT OR REPLACE INTO doc_anchors (doc_id, model, embedding) VALUES (?, ?, ?)",
                [(batch[j][0], EMBED_MODEL, blobs[j]) for j in range(len(batch))],
            )
            conn.commit()
            print(f"  [{min(i + len(batch), len(pending))}/{len(pending)}] "
                  f"+{time.time() - t0:.0f}s", flush=True)
        print(f"DONE: {total - len(done)} newly embedded, {total} total anchors.")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
