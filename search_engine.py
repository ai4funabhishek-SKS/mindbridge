import re
import sys
import sqlite3
import argparse
from pathlib import Path

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Second Brain Search Engine (Linear FTS5 & Knowledge Graph)")
    parser.add_argument("query", type=str, help="Search terms or entity name")
    parser.add_argument("--mode", type=str, choices=["linear", "graph"], default="linear", help="Search mode")
    parser.add_argument("--limit", type=int, default=6, help="Maximum results to return")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
        
    args = parser.parse_args()
    if args.mode == "linear":
        search_linear(args.query, args.limit)
    elif args.mode == "graph":
        search_graph(args.query)

