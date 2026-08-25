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
MIN_ANCHOR_CHARS = 30

# Bulk-import filler that carries no document-specific meaning. Anchors built
# from these cluster into an identical "empty shell" vector (~0.5 similarity
# to everything) and poison blended rankings, so they must be stripped.
FILLER_PROBLEM_VALUES = {
    "knowledge asset storage",
}
FILLER_TIER_VALUES = {
    "reference knowledge",
    "sensitive (private vault)",
    "half-baked idea (r&d mine)",
    "must keep - high reusability",
}
_EXT_TOKENS = {"json", "md", "pdf", "docx", "txt", "xlsx", "sql", "csv",
               "html", "yml", "yaml", "pptx"}


def _clean_tags(tags: str) -> str:
    """Drops format-extension noise tokens from the tags field."""
    kept = []
    for tok in (t.strip() for t in tags.split(",")):
        if not tok or tok.lower() in _EXT_TOKENS or tok.startswith("."):
            continue
        kept.append(tok)
    return ", ".join(kept)


def build_anchor_text(row: dict) -> str:
    """Composes the compact fingerprint text for one document."""
    problem = (row.get("problem_solved") or "").strip()
    if problem.lower() in FILLER_PROBLEM_VALUES:
        problem = ""
    tier = (row.get("rating_tier") or "").strip()
    if tier.lower() in FILLER_TIER_VALUES:
        tier = ""
    parts = [
        (row.get("asset_title") or "").strip(),
        problem,
        _clean_tags(row.get("tags") or ""),
        tier,
        (row.get("topic") or "").strip(),
    ]
    text = " | ".join(p for p in parts if p)
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
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true",
                    help="delete existing anchors for the model and rebuild")
    args = ap.parse_args()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS doc_anchors (
                   doc_id INTEGER PRIMARY KEY,
                   model TEXT NOT NULL,
                   embedding BLOB NOT NULL)"""
        )
        if args.force:
            n = conn.execute(
                "DELETE FROM doc_anchors WHERE model=?", (EMBED_MODEL,)
            ).rowcount
            conn.commit()
            print(f"--force: deleted {n} existing anchors")

        docs = conn.execute(
            """SELECT id, asset_title, problem_solved, tags, rating AS rating_tier, topic
               FROM documents ORDER BY id"""
        ).fetchall()
        done = {
            rid for (rid,) in conn.execute(
                "SELECT doc_id FROM doc_anchors WHERE model=?", (EMBED_MODEL,)
            )
        }
        colnames = ("asset_title", "problem_solved", "tags", "rating_tier", "topic")
        pending = []
        hollow = 0
        for d in docs:
            rid = d[0]
            if rid in done:
                continue
            row = dict(zip(colnames, d[1:]))
            text = build_anchor_text(row)
            if len(text) < MIN_ANCHOR_CHARS:
                # Hollow metadata: store a zero vector so rankings are not
                # poisoned by an "empty shell" fingerprint.
                pending.append((rid, None))
                hollow += 1
            else:
                pending.append((rid, text))

        total = len(docs)
        to_embed = len(pending) - hollow
        print(f"{total} documents | {len(done)} already anchored | "
              f"{len(pending)} to build ({hollow} hollow -> zero vector)")
        t0 = time.time()

        def _commit(batch, blobs):
            conn.executemany(
                "INSERT OR REPLACE INTO doc_anchors (doc_id, model, embedding) VALUES (?, ?, ?)",
                [(batch[j][0], EMBED_MODEL, blobs[j]) for j in range(len(batch))],
            )
            conn.commit()

        real = [(rid, txt) for rid, txt in pending if txt is not None]
        for i in range(0, len(real), BATCH_SIZE):
            batch = real[i:i + BATCH_SIZE]
            blobs = _embed_batch([txt for _, txt in batch])
            _commit(batch, blobs)
            print(f"  embedded [{min(i + len(batch), len(real))}/{len(real)}] "
                  f"+{time.time() - t0:.0f}s", flush=True)

        if hollow:
            zero_blob = np.zeros(768, dtype=np.float32).tobytes()
            _commit([(rid, None) for rid, txt in pending if txt is None],
                    [zero_blob] * hollow)

        print(f"DONE: {len(real)} embedded + {hollow} hollow zero-vectors, "
              f"{total} total anchors.")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
