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
    order = np.argsort(-sims)[:actual_limit]
    elapsed = time.time() - t0

    results = [(int(chunk_ids[i]), float(sims[i])) for i in order]
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
        order = np.argsort(-sims)[:pool]
        sem_ranks = [int(chunk_ids[i]) for i in order]
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

    top = sorted(fused.items(), key=lambda kv: -kv[1])[:actual_limit]
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



