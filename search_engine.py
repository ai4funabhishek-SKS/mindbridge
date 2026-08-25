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
MANIFEST_PATH = BASE_DIR / "Processed_Assets" / "file_classification_manifest.json"

EMBED_MODEL = "nomic-embed-text"
OLLAMA_URL = "http://localhost:11434/api/embed"
RRF_K = 60  # standard reciprocal rank fusion constant
GEM_THRESHOLD = 8
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

def _resolve_topic_filter(topic_arg: str) -> set:
    """Doc-id set for documents whose topic contains topic_arg (case-insensitive)."""
    if not topic_arg:
        return set()
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT id FROM documents WHERE lower(topic) LIKE ?",
            (f"%{topic_arg.lower()}%",),
        ).fetchall()
    finally:
        conn.close()
    return {r[0] for r in rows}


_GEM_CACHE = {}  # manifest mtime -> {name_lower, ...}


def _load_gem_names() -> set:
    """Lower-cased raw file names whose manifest reusability_score >= GEM_THRESHOLD."""
    mtime = MANIFEST_PATH.stat().st_mtime
    cached = _GEM_CACHE.get(mtime)
    if cached is not None:
        return cached
    names = set()
    try:
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            for entry in json.load(f):
                score = entry.get("reusability_score")
                if isinstance(score, (int, float)) and score >= GEM_THRESHOLD:
                    names.add(Path(entry["raw_path"]).name.lower())
    except FileNotFoundError:
        pass
    _GEM_CACHE.clear()
    _GEM_CACHE[mtime] = names
    return names


def _load_gem_doc_ids() -> set:
    """Doc ids whose manifest reusability_score >= GEM_THRESHOLD."""
    gem_names = _load_gem_names()
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute("SELECT id, file_name FROM documents").fetchall()
    finally:
        conn.close()
    return {did for did, fname in rows if fname.lower() in gem_names}


def list_topics():
    """Prints every topic with its document count."""
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT topic, COUNT(*) FROM documents GROUP BY topic ORDER BY 2 DESC"
        ).fetchall()
    finally:
        conn.close()
    print(f"\n{'='*70}\n [TOPICS] {len(rows)} topics in the knowledge base\n{'='*70}\n")
    for topic, n in rows:
        print(f"  {n:>4} documents | {topic}")
    print(f"\nFilter any search with:  --topic \"<name or part of name>\"\n")


def search_linear(query: str, limit: int = 8, topic: str = None,
                  gem_only: bool = False):
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

    gem_names = _load_gem_names() if gem_only else None
    fetch_n = actual_limit * 15 if (topic or gem_only) else actual_limit

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
        cursor.execute(sql, (formatted_query, fetch_n))
        rows = cursor.fetchall()
        if topic:
            t = topic.lower()
            rows = [r for r in rows if t in (r[2] or "").lower()]
        if gem_only:
            rows = [r for r in rows if (r[1] or "").lower() in gem_names]
        rows = rows[:actual_limit]
        
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


def _allowed_doc_set(topic_doc_ids, gem_doc_ids):
    """Intersection of active filters, or None when nothing is filtered."""
    sets = [s for s in (topic_doc_ids, gem_doc_ids) if s is not None]
    if not sets:
        return None
    allow = set.intersection(*sets) if len(sets) > 1 else set(sets[0])
    return allow or set([-1])  # empty filter must match nothing


def search_semantic(query: str, limit: int = 8,
                    topic_doc_ids=None, gem_doc_ids=None):
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
    allow = _allowed_doc_set(topic_doc_ids, gem_doc_ids)
    chunk_doc_map = _load_chunk_doc_map()
    if allow is not None:
        keep = np.array([chunk_doc_map.get(int(c), -1) in allow for c in chunk_ids])
        sims = np.where(keep, sims, -np.inf)
    row_doc_ids = [chunk_doc_map.get(int(cid)) for cid in chunk_ids]
    scores = fuse_chunk_anchor_scores(sims, row_doc_ids, _anchor_rank_map(qvec))
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


def search_hybrid(query: str, limit: int = 8,
                  topic_doc_ids=None, gem_doc_ids=None):
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
    allow = _allowed_doc_set(topic_doc_ids, gem_doc_ids)
    chunk_doc_map = _load_chunk_doc_map()

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
            if allow is not None:
                bm25_ranks = [c for c in bm25_ranks
                              if chunk_doc_map.get(int(c), -1) in allow]
        except Exception:
            pass
        finally:
            conn.close()

    # --- Leg 2: semantic ranks ---
    try:
        qvec = _embed_query(query)
        chunk_ids, matrix = _load_embedding_matrix()
        sims = matrix @ qvec
        if allow is not None:
            keep = np.array([chunk_doc_map.get(int(c), -1) in allow for c in chunk_ids])
            sims = np.where(keep, sims, -np.inf)
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
    parser.add_argument("--topics", action="store_true",
                        help="list all topics with document counts, then exit")
    parser.add_argument("--topic", type=str, default=None,
                        help="restrict results to one topic (partial match ok)")
    parser.add_argument("--gems", action="store_true",
                        help="only show assets rated 8+ (reusability gems)")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.topics:
        list_topics()
        sys.exit(0)

    topic_ids = _resolve_topic_filter(args.topic) if args.topic else None
    gem_ids = _load_gem_doc_ids() if args.gems else None

    if args.mode == "linear":
        search_linear(args.query, args.limit, topic=args.topic, gem_only=args.gems)
    elif args.mode == "graph":
        search_graph(args.query)
    elif args.mode == "semantic":
        search_semantic(args.query, args.limit,
                        topic_doc_ids=topic_ids, gem_doc_ids=gem_ids)
    elif args.mode == "hybrid":
        search_hybrid(args.query, args.limit,
                      topic_doc_ids=topic_ids, gem_doc_ids=gem_ids)



