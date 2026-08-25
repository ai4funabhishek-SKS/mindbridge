import re
import sys
import json
import time
import sqlite3
import argparse
import urllib.request
from pathlib import Path

import numpy as np

# Ensure UTF-8 output on Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = Path(r"C:\KnowledgeBase_Staging")
if not BASE_DIR.exists():
    BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "Processed_Assets" / "my_rag_data.db"

EMBED_MODEL = "nomic-embed-text"
OLLAMA_URL = "http://localhost:11434/api/embed"
RRF_K = 60  # standard reciprocal rank fusion constant
ANCHOR_WEIGHT = 1.0  # weight of document-anchor rank bonus vs chunk rank
MAX_PER_DOC = 2      # result slots any single document may occupy


def diverse_top(indices, chunk_ids, chunk_doc_map, limit,
                max_per_doc=MAX_PER_DOC):
    """Walks ranked chunk indices, capping how many slots one document takes."""
    out = []
    counts = {}
    for i in indices:
        did = chunk_doc_map.get(int(chunk_ids[i]))
        if counts.get(did, 0) >= max_per_doc:
            continue
        counts[did] = counts.get(did, 0) + 1
        out.append(int(i))
        if len(out) >= limit:
            break
    return out

def sanitize_fts5_query(query: str) -> str:
    """Extracts valid alphanumeric search tokens and formats for FTS5 prefix matching."""
    if not query:
        return ""
    # Extract alphanumeric tokens, ignoring punctuation/FTS5 operators that cause syntax errors
    tokens = re.findall(r'[a-zA-Z0-9_\u00C0-\u017F]+', query)
    if not tokens:
        return ""
    return " ".join([f'"{tok}"*' for tok in tokens])

def search_linear(query: str, limit: int = 8):
    """Executes SQLite FTS5 Full-Text Search (Linear / BM25)."""
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        return
    
    if limit == 0:
        print(f"\n{'='*70}")
        print(f" [SEARCH] LINEAR FTS5 RESULTS FOR: '{query}' (0 matches)")
        print(f"{'='*70}\n")
        print("No matching records found. Try broader keywords.")
        return
    
    actual_limit = limit if limit > 0 else 50
    formatted_query = sanitize_fts5_query(query)
    
    if not formatted_query:
        print(f"\n{'='*70}")
        print(f" [SEARCH] LINEAR FTS5 RESULTS FOR: '{query}' (0 matches)")
        print(f"{'='*70}\n")
        print("No matching records found. Try broader keywords.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    sql = """
    SELECT 
        asset_title,
        file_name,
        topic,
        problem_solved,
        snippet(chunks_fts, 0, '>>> ', ' <<<', '...', 25) as snippet_text,
        bm25(chunks_fts) as rank
    FROM chunks_fts
    WHERE chunks_fts MATCH ?
    ORDER BY rank
    LIMIT ?;
    """
    
    try:
        cursor.execute(sql, (formatted_query, actual_limit))
        rows = cursor.fetchall()
        
        print(f"\n{'='*70}")
        print(f" [SEARCH] LINEAR FTS5 RESULTS FOR: '{query}' ({len(rows)} matches)")
        print(f"{'='*70}\n")
        
        if not rows:
            print("No matching records found. Try broader keywords.")
            return
            
        for i, r in enumerate(rows, 1):
            title, fname, topic, problem, snippet, rank = r
            print(f"[{i}] {title} ({fname})")
            print(f"    Topic: {topic} | Rank Score: {abs(round(rank, 3))}")
            print(f"    Problem Solved: {problem}")
            print(f"    Excerpt: {snippet.strip()}")
            print(f"{'-'*70}")
    except Exception as e:
        print(f"Search query completed with notice: {e}")
        print("No matching records found. Try broader keywords.")
    finally:
        conn.close()

def search_graph(entity: str):
    """Inspects Knowledge Graph connections for a specific entity, tool, or document."""
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    clean_entity = entity.strip()
    if not clean_entity:
        print(f"\n{'='*70}")
        print(f" [GRAPH] KNOWLEDGE GRAPH CONNECTIONS FOR: '{entity}'")
        print(f"{'='*70}\n")
        print(f"Entity '{entity}' not found in Knowledge Graph nodes.")
        conn.close()
        return
        
    node_query = f"%{clean_entity.lower().replace(' ', '_')}%"
    cursor.execute("""
    SELECT id, label, node_type, details FROM kg_nodes WHERE id LIKE ? OR label LIKE ?;
    """, (node_query, f"%{clean_entity}%"))
    nodes = cursor.fetchall()
    
    print(f"\n{'='*70}")
    print(f" [GRAPH] KNOWLEDGE GRAPH CONNECTIONS FOR: '{entity}'")
    print(f"{'='*70}\n")
    
    if not nodes:
        print(f"Entity '{entity}' not found in Knowledge Graph nodes.")
        conn.close()
        return
        
    for nid, label, ntype, details in nodes:
        print(f"* Node: {label} [Type: {ntype}]")
        print(f"  Details: {details}")
        
        cursor.execute("""
        SELECT e.relationship, n.label, n.node_type
        FROM kg_edges e
        JOIN kg_nodes n ON e.source_id = n.id
        WHERE e.target_id = ?
        LIMIT 10;
        """, (nid,))
        inbound = cursor.fetchall()
        
        cursor.execute("""
        SELECT e.relationship, n.label, n.node_type
        FROM kg_edges e
        JOIN kg_nodes n ON e.target_id = n.id
        WHERE e.source_id = ?
        LIMIT 10;
        """, (nid,))
        outbound = cursor.fetchall()
        
        if inbound:
            print("  Inbound References (Assets using this):")
            for rel, src_label, src_type in inbound:
                print(f"     <- [{rel}] {src_label} ({src_type})")
        if outbound:
            print("  Connects to:")
            for rel, tgt_label, tgt_type in outbound:
                print(f"     -> [{rel}] {tgt_label} ({tgt_type})")
        print(f"{'-'*70}")
        
    conn.close()

def _embed_query(query: str) -> np.ndarray:
    """Embeds a single query string via local Ollama; returns L2-normalised float32 vector."""
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps({"model": EMBED_MODEL, "input": [query[:8000]]}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read())
    embs = d.get("embeddings")
    if not embs:
        raise RuntimeError("Ollama returned no embedding for the query.")
    vec = np.asarray(embs[0], dtype=np.float32)
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


_EMBED_CACHE = {}  # module-level cache: (db_mtime) -> (chunk_ids, matrix)


def _load_embedding_matrix():
    """Loads all chunk embeddings into a numpy matrix, cached per DB modification time."""
    mtime = DB_PATH.stat().st_mtime
    cached = _EMBED_CACHE.get(mtime)
    if cached is not None:
        return cached
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT chunk_id, embedding FROM chunk_embeddings WHERE model=?",
            (EMBED_MODEL,),
        ).fetchall()
    finally:
        conn.close()
    chunk_ids = np.array([r[0] for r in rows], dtype=np.int64)
    matrix = np.frombuffer(b"".join(r[1] for r in rows), dtype=np.float32).reshape(
        len(rows), -1
    )
    result = (chunk_ids, matrix)
    _EMBED_CACHE.clear()
    _EMBED_CACHE[mtime] = result
    return result


def _fetch_chunk_metadata(chunk_ids):
    """Returns {chunk_id: (title, fname, topic, problem, excerpt)} for the given ids."""
    if not chunk_ids:
        return {}
    conn = sqlite3.connect(DB_PATH)
    try:
        out = {}
        for cid in chunk_ids:
            cur = conn.execute(
                """
                SELECT d.asset_title, d.file_name, d.topic, d.problem_solved,
                       substr(c.chunk_text, 1, 220)
                FROM chunks c JOIN documents d ON c.doc_id = d.id
                WHERE c.id = ?
                """,
                (cid,),
            )
            row = cur.fetchone()
            if row:
                out[cid] = row
        return out
    finally:
        conn.close()


def blend_scores(chunk_sims: np.ndarray, anchor_sims: np.ndarray,
                 weight: float = ANCHOR_WEIGHT) -> np.ndarray:
    """Blends chunk-level and document-anchor similarity scores."""
    if chunk_sims.shape != anchor_sims.shape:
        raise ValueError("chunk_sims and anchor_sims must have the same shape")
    return (1.0 - weight) * chunk_sims + weight * anchor_sims


def fuse_chunk_anchor_scores(chunk_sims: np.ndarray, chunk_doc_ids,
                             anchor_rank_map: dict,
                             weight: float = ANCHOR_WEIGHT, k: int = RRF_K) -> np.ndarray:
    """Rank-fusion of chunk similarity with document-anchor identity.

    Every row gets a reciprocal-rank score from its chunk position, plus a
    weighted reciprocal-rank bonus from where its parent document sits in
    the document-anchor ranking. Rank-based fusion amplifies meaningful
    ordering instead of tiny raw-score deltas.
    """
    n = len(chunk_sims)
    order = np.argsort(-chunk_sims)
    out = np.empty(n, dtype=np.float64)
    out[order] = 1.0 / (k + np.arange(1, n + 1))
    for i, did in enumerate(chunk_doc_ids):
        r = anchor_rank_map.get(int(did)) if did is not None else None
        if r:
            out[i] += weight / (k + r)
    return out


_ANCHOR_CACHE = {}   # (db_mtime) -> (doc_ids, matrix) | (None, None)
_CHUNKDOC_CACHE = {}  # (db_mtime) -> {chunk_id: doc_id}


def _load_anchor_matrix():
    """Loads document anchor embeddings; returns (doc_ids, matrix) or (None, None)."""
    mtime = DB_PATH.stat().st_mtime
    cached = _ANCHOR_CACHE.get(mtime)
    if cached is not None:
        return cached
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT doc_id, embedding FROM doc_anchors WHERE model=?",
            (EMBED_MODEL,),
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
    finally:
        conn.close()
    if not rows:
        result = (None, None)
    else:
        doc_ids = np.array([r[0] for r in rows], dtype=np.int64)
        matrix = np.frombuffer(b"".join(r[1] for r in rows), dtype=np.float32).reshape(
            len(rows), -1
        )
        result = (doc_ids, matrix)
    _ANCHOR_CACHE.clear()
    _ANCHOR_CACHE[mtime] = result
    return result


def _load_chunk_doc_map():
    """Returns {chunk_id: doc_id} for every chunk in the database."""
    mtime = DB_PATH.stat().st_mtime
    cached = _CHUNKDOC_CACHE.get(mtime)
    if cached is not None:
        return cached
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute("SELECT id, doc_id FROM chunks").fetchall()
    finally:
        conn.close()
    mapping = {int(cid): int(did) for cid, did in rows}
    _CHUNKDOC_CACHE.clear()
    _CHUNKDOC_CACHE[mtime] = mapping
    return mapping


def _anchor_sims_for_chunks(chunk_ids: np.ndarray, qvec: np.ndarray) -> np.ndarray:
    """Per-chunk document-anchor similarity (0 where no anchor exists)."""
    doc_ids, doc_matrix = _load_anchor_matrix()
    n = len(chunk_ids)
    out = np.zeros(n, dtype=np.float32)
    if doc_ids is None or not len(doc_ids):
        return out
    doc_pos = {int(d): i for i, d in enumerate(doc_ids)}
    chunk_doc = _load_chunk_doc_map()
    idx = np.full(n, -1, dtype=np.int64)
    for i, cid in enumerate(chunk_ids):
        did = chunk_doc.get(int(cid))
        if did is not None:
            pos = doc_pos.get(did)
            if pos is not None:
                idx[i] = pos
    mask = idx >= 0
    if mask.any():
        out[mask] = doc_matrix[idx[mask]] @ qvec
    return out


def _anchor_rank_map(qvec: np.ndarray) -> dict:
    """{doc_id: 1-based rank} of all anchored documents for this query."""
    doc_ids, doc_matrix = _load_anchor_matrix()
    if doc_ids is None or not len(doc_ids):
        return {}
    sims = doc_matrix @ qvec
    order = np.argsort(-sims)
    return {int(doc_ids[i]): pos + 1 for pos, i in enumerate(order)}


def search_semantic(query: str, limit: int = 8):
    """Cosine similarity search over pre-computed chunk embeddings."""
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        return

    print_header = lambda n: (
        f"\n{'='*70}\n [SEARCH] SEMANTIC RESULTS FOR: '{query}' ({n} matches)\n{'='*70}\n"
    )

    if limit == 0 or not query.strip():
        print(print_header(0))
        print("No matching records found. Try broader keywords.")
        return

    actual_limit = limit if limit > 0 else 50

    t0 = time.time()
    try:
        qvec = _embed_query(query)
    except Exception as e:
        print(f"\n[!] Semantic mode needs local Ollama running ({e}).")
        print("    Start it with:  ollama serve   (or use --mode linear)")
        return

    try:
        chunk_ids, matrix = _load_embedding_matrix()
    except Exception as e:
        print(f"Error loading embeddings: {e}")
        return

    sims = matrix @ qvec
    chunk_doc_map = _load_chunk_doc_map()
    row_doc_ids = [chunk_doc_map.get(int(cid)) for cid in chunk_ids]
    scores = fuse_chunk_anchor_scores(
        sims, row_doc_ids, _anchor_rank_map(qvec)
    )
    order = np.argsort(-scores)
    picked = diverse_top(order, chunk_ids, chunk_doc_map, actual_limit)
    elapsed = time.time() - t0

    results = [(int(chunk_ids[i]), float(scores[i])) for i in picked]
    meta = _fetch_chunk_metadata([cid for cid, _ in results])

    print(f"{print_header(len(results))}")
    for i, (cid, score) in enumerate(results, 1):
        title, fname, topic, problem, excerpt = meta.get(cid, ("?", "?", "?", "?", ""))
        print(f"[{i}] {title} ({fname})")
        print(f"    Topic: {topic} | Similarity: {score:.3f}")
        print(f"    Problem Solved: {problem}")
        print(f"    Excerpt: {(excerpt or '').strip()}")
        print(f"{'-'*70}")
    print(f"(query embedded + ranked in {elapsed:.2f}s)")


def search_hybrid(query: str, limit: int = 8):
    """Reciprocal Rank Fusion of BM25 keyword ranks + semantic similarity ranks."""
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        return

    header = f"HYBRID (RRF) RESULTS FOR: '{query}'"
    if limit == 0 or not query.strip():
        print(f"\n{'='*70}\n [SEARCH] {header} (0 matches)\n{'='*70}\n")
        print("No matching records found. Try broader keywords.")
        return

    actual_limit = limit if limit > 0 else 50
    pool = max(actual_limit * 5, 50)

    t0 = time.time()

    # --- Leg 1: BM25 keyword ranks ---
    formatted_query = sanitize_fts5_query(query)
    bm25_ranks = []
    if formatted_query:
        conn = sqlite3.connect(DB_PATH)
        try:
            rows = conn.execute(
                "SELECT rowid FROM chunks_fts WHERE chunks_fts MATCH ? "
                "ORDER BY bm25(chunks_fts) LIMIT ?",
                (formatted_query, pool),
            ).fetchall()
            bm25_ranks = [r[0] for r in rows]
        except Exception:
            pass
        finally:
            conn.close()

    # --- Leg 2: semantic ranks ---
    try:
        qvec = _embed_query(query)
        chunk_ids, matrix = _load_embedding_matrix()
        sims = matrix @ qvec
        chunk_doc_map = _load_chunk_doc_map()
        row_doc_ids = [chunk_doc_map.get(int(cid)) for cid in chunk_ids]
        scores = fuse_chunk_anchor_scores(
            sims, row_doc_ids, _anchor_rank_map(qvec)
        )
        order = np.argsort(-scores)
        picked = diverse_top(order, chunk_ids, chunk_doc_map, pool)
        sem_ranks = [int(chunk_ids[i]) for i in picked]
    except Exception as e:
        print(f"\n[!] Semantic leg unavailable ({e}).")
        print("    Start Ollama with:  ollama serve   (or use --mode linear)")
        return

    # --- RRF fusion: score(d) = sum over legs of 1/(k + rank) ---
    fused = {}
    for rank, cid in enumerate(bm25_ranks, 1):
        fused[cid] = fused.get(cid, 0.0) + 1.0 / (RRF_K + rank)
    for rank, cid in enumerate(sem_ranks, 1):
        fused[cid] = fused.get(cid, 0.0) + 1.0 / (RRF_K + rank)

    ranked = sorted(fused.items(), key=lambda kv: -kv[1])
    chunk_doc_map = _load_chunk_doc_map()
    top = []
    seen_per_doc = {}
    for cid, sc in ranked:
        did = chunk_doc_map.get(int(cid))
        if seen_per_doc.get(did, 0) >= MAX_PER_DOC:
            continue
        seen_per_doc[did] = seen_per_doc.get(did, 0) + 1
        top.append((cid, sc))
        if len(top) >= actual_limit:
            break
    elapsed = time.time() - t0

    meta = _fetch_chunk_metadata([cid for cid, _ in top])

    print(f"\n{'='*70}")
    print(f" [SEARCH] {header} ({len(top)} matches)")
    print(f"{'='*70}\n")

    if not top:
        print("No matching records found. Try broader keywords.")
        return

    bm25_pos = {cid: i for i, cid in enumerate(bm25_ranks, 1)}
    sem_pos = {cid: i for i, cid in enumerate(sem_ranks, 1)}

    for i, (cid, score) in enumerate(top, 1):
        title, fname, topic, problem, excerpt = meta.get(cid, ("?", "?", "?", "?", ""))
        kw = f"kw#{bm25_pos[cid]}" if cid in bm25_pos else "kw--"
        sm = f"sem#{sem_pos[cid]}" if cid in sem_pos else "sem--"
        print(f"[{i}] {title} ({fname})")
        print(f"    Topic: {topic} | RRF Score: {score:.4f} | {kw} | {sm}")
        print(f"    Problem Solved: {problem}")
        print(f"    Excerpt: {(excerpt or '').strip()}")
        print(f"{'-'*70}")
    print(f"(fused in {elapsed:.2f}s)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Second Brain Search Engine (Linear FTS5, Semantic, Hybrid RRF & Knowledge Graph)"
    )
    parser.add_argument("query", type=str, nargs="?", default="", help="Search terms or entity name")
    parser.add_argument("--mode", type=str, choices=["linear", "graph", "semantic", "hybrid"],
                        default="linear", help="Search mode")
    parser.add_argument("--limit", type=int, default=6, help="Maximum results to return")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    if args.mode == "linear":
        search_linear(args.query, args.limit)
    elif args.mode == "graph":
        search_graph(args.query)
    elif args.mode == "semantic":
        search_semantic(args.query, args.limit)
    elif args.mode == "hybrid":
        search_hybrid(args.query, args.limit)



