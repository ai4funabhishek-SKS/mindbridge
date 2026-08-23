import os
import sys
import json
import sqlite3
import re
from pathlib import Path
import fitz # PyMuPDF
import docx

BASE_DIR = Path(r"C:\KnowledgeBase_Staging")
if not BASE_DIR.exists():
    BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "Raw_copies"
TOPICS_DIR = BASE_DIR / "03_Topics_and_Projects"
ASSETS_DIR = BASE_DIR / "02_Assets_Library"
DB_PATH = BASE_DIR / "Processed_Assets" / "my_rag_data.db"
OUTPUT_DIR = BASE_DIR / "00_Index_and_Dashboards"
KG_HTML_PATH = OUTPUT_DIR / "Interactive_Knowledge_Graph.html"

CANONICAL_DOMAINS = [
    "01_AI_Agents_and_Autonomous_Systems",
    "02_Workflow_Automations_n8n",
    "03_Prompt_Engineering_and_Frameworks",
    "04_Mobile_and_Android_Ecosystem",
    "05_Code_Snippets_and_Dev_Tools",
    "06_Quantitative_Finance_and_Trading",
    "07_Content_Creation_and_Media_Engines",
    "08_Business_Operations_and_Subbroking",
    "09_LLM_Conversations_and_Syntheses",
    "10_R_and_D_Incubator_Half_Baked_Ideas"
]

def init_database(conn: sqlite3.Connection):
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS chunks_fts;")
    cursor.execute("DROP TABLE IF EXISTS chunks;")
    cursor.execute("DROP TABLE IF EXISTS documents;")
    cursor.execute("DROP TABLE IF EXISTS kg_edges;")
    cursor.execute("DROP TABLE IF EXISTS kg_nodes;")
    
    # 1. Documents Table
    cursor.execute("""
    CREATE TABLE documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT,
        relative_path TEXT UNIQUE,
        asset_title TEXT,
        format TEXT,
        topic TEXT,
        problem_solved TEXT,
        workability TEXT,
        rating TEXT,
        tags TEXT,
        size_kb REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 2. Text Chunks Table
    cursor.execute("""
    CREATE TABLE chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id INTEGER,
        chunk_index INTEGER,
        chunk_text TEXT,
        char_count INTEGER,
        FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE CASCADE
    );
    """)
    
    # 3. FTS5 Full-Text Search Virtual Table for Linear Search
    cursor.execute("""
    CREATE VIRTUAL TABLE chunks_fts USING fts5(
        chunk_text,
        asset_title UNINDEXED,
        topic UNINDEXED,
        problem_solved UNINDEXED,
        file_name UNINDEXED,
        tokenize = 'porter unicode61'
    );
    """)
    
    # 4. Knowledge Graph Nodes Table
    cursor.execute("""
    CREATE TABLE kg_nodes (
        id TEXT PRIMARY KEY,
        label TEXT,
        node_type TEXT,
        details TEXT,
        count INTEGER DEFAULT 1
    );
    """)
    
    # 5. Knowledge Graph Edges (Relationships) Table
    cursor.execute("""
    CREATE TABLE kg_edges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id TEXT,
        target_id TEXT,
        relationship TEXT,
        weight REAL DEFAULT 1.0,
        FOREIGN KEY (source_id) REFERENCES kg_nodes(id),
        FOREIGN KEY (target_id) REFERENCES kg_nodes(id)
    );
    """)
    
    conn.commit()
    print("SQLite Knowledge Store Schema initialized successfully!")

def extract_full_text(file_path: Path, ext: str) -> str:
    text = ""
    try:
        if ext in ['.md', '.txt', '.py', '.json', '.env', '.yaml', '.yml', '.csv', '.sql']:
            text = file_path.read_text(encoding='utf-8', errors='ignore')
        elif ext == '.pdf':
            doc = fitz.open(file_path)
            pages_text = []
            for page in doc:
                try:
                    pages_text.append(page.get_text())
                except Exception:
                    pass
            doc.close()
            text = "\n".join(pages_text)
        elif ext in ['.docx', '.doc']:
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception as e:
        text = f"Extraction note: {str(e)}"
    return text.strip()

def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def extract_yaml_frontmatter(content: str):
    if not content.startswith("---"):
        return None, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content
    fm_raw = parts[1].strip()
    body = parts[2].strip()
    
    parsed = {}
    current_list_key = None
    for line in fm_raw.splitlines():
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue
        if ":" in line_str and not line_str.startswith("-"):
            key, val = line_str.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                items = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
                parsed[key] = items
                current_list_key = None
            elif val == "":
                parsed[key] = []
                current_list_key = key
            else:
                val = val.strip("'\"")
                if val.isdigit():
                    val = int(val)
                parsed[key] = val
                current_list_key = None
        elif line_str.startswith("-") and current_list_key:
            item = line_str[1:].strip().strip("'\"")
            if isinstance(parsed.get(current_list_key), list):
                parsed[current_list_key].append(item)
    return parsed, body

def populate_knowledge_store():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    init_database(conn)
    cursor = conn.cursor()
    
    print(f"Ingesting corpus into {DB_PATH}...")
    
    # 1. Predefined Technology Entities
    tech_keywords = {
        "n8n": ("Tool", "Workflow Automation Platform"),
        "OpenAI": ("AI Provider", "LLM APIs (GPT-4, ChatGPT)"),
        "Pinecone": ("Vector DB", "Vector Database for RAG"),
        "DeepSeek": ("AI Model", "DeepSeek Reasoner & Coder"),
        "Google Gemini": ("AI Provider", "Google Multi-modal LLMs"),
        "TradingView": ("Platform", "Charting & Trading Platform"),
        "Python": ("Language", "Core Scripting Language"),
        "YouTube": ("Media Platform", "Video & Audio Content Platform"),
        "Playwright": ("Tool", "Browser Automation Engine"),
        "SQLite": ("Database", "Local Relational & Vector Storage"),
        "Telegram": ("Communication", "Bot API & Messenger"),
        "WhatsApp": ("Communication", "Messaging Integration"),
        "Gmail": ("Communication", "Email Automation"),
        "Subbroking": ("Domain", "Financial Subbroking Business"),
        "Options Trading": ("Domain", "Derivatives & Quant Trading"),
        "Prompt Engineering": ("Discipline", "System Prompt Design")
    }
    
    for tech, (ntype, desc) in tech_keywords.items():
        cursor.execute("INSERT OR REPLACE INTO kg_nodes (id, label, node_type, details) VALUES (?, ?, ?, ?)",
                       (tech.lower().replace(" ", "_"), tech, ntype, desc))
                       
    # 2. Canonical Domain Hubs
    for domain in CANONICAL_DOMAINS:
        dom_id = domain.lower()
        dom_label = domain.replace("_", " ")
        cursor.execute("INSERT OR REPLACE INTO kg_nodes (id, label, node_type, details) VALUES (?, ?, ?, ?)",
                       (dom_id, dom_label, "Domain Hub", f"Canonical Domain Taxonomy: {domain}"))
    
    file_count = 0
    total_chunks = 0
    
    # Ingest Raw Assets
    for root, _, files in os.walk(RAW_DIR):
        for f in files:
            file_path = Path(root) / f
            ext = file_path.suffix.lower()
            size_kb = round(file_path.stat().st_size / 1024, 2)
            rel_path = str(file_path.relative_to(BASE_DIR)).replace('\\', '/')
            
            title = file_path.stem
            topic = "General Knowledge"
            problem_solved = "Knowledge asset storage"
            workability = "Reference Documentation"
            rating = "Reference Knowledge"
            tags = [ext]
            
            fn_lower = file_path.name.lower()
            if ext == '.json':
                topic = "AI & Automation"
                workability = "Deployable Template"
                rating = "Must Keep - High Reusability"
                tags.append("n8n" if "node" in fn_lower or "workflow" in fn_lower or "agent" in fn_lower else "JSON")
            elif ext == '.pdf':
                if any(k in fn_lower for k in ["statement", "bank", "account"]):
                    topic = "Personal Finance"
                    workability = "Private Data"
                    rating = "Sensitive (Private Vault)"
                else:
                    topic = "Reference Documentation"
                    workability = "Whitepaper"
                    rating = "Must Keep - High Reusability"
            elif ext in ['.md', '.txt']:
                if "prompt" in fn_lower:
                    topic = "Prompt Engineering"
                    workability = "Deployable Prompt Template"
                    rating = "Must Keep - High Reusability"
                elif any(k in fn_lower for k in ["trade", "equity", "finance"]):
                    topic = "Trading & Financial Systems"
                    workability = "Algorithmic Rules"
                    rating = "Must Keep - High Reusability"
                elif any(k in fn_lower for k in ["inbox", "idea", "concept"]):
                    topic = "Ideas & Half-Baked Concepts"
                    workability = "Conceptual R&D"
                    rating = "Half-Baked Idea (R&D Mine)"
            
            cursor.execute("""
            INSERT OR REPLACE INTO documents (file_name, relative_path, asset_title, format, topic, problem_solved, workability, rating, tags, size_kb)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (file_path.name, rel_path, title, ext, topic, problem_solved, workability, rating, ", ".join(tags), size_kb))
            
            doc_id = cursor.lastrowid
            file_count += 1
            
            doc_node_id = f"doc_{doc_id}"
            cursor.execute("INSERT OR REPLACE INTO kg_nodes (id, label, node_type, details) VALUES (?, ?, ?, ?)",
                           (doc_node_id, title[:28], "Document", f"Format: {ext} | Topic: {topic}"))
            
            full_text = extract_full_text(file_path, ext)
            chunks = chunk_text(full_text)
            
            for idx, c_text in enumerate(chunks):
                total_chunks += 1
                cursor.execute("INSERT INTO chunks (doc_id, chunk_index, chunk_text, char_count) VALUES (?, ?, ?, ?)",
                               (doc_id, idx, c_text, len(c_text)))
                cursor.execute("""
                INSERT INTO chunks_fts (chunk_text, asset_title, topic, problem_solved, file_name)
                VALUES (?, ?, ?, ?, ?)
                """, (c_text, title, topic, problem_solved, file_path.name))
                
            combined_sample = (file_path.name + " " + full_text[:4000]).lower()
            for tech, (ntype, _) in tech_keywords.items():
                if tech.lower() in combined_sample:
                    tech_id = tech.lower().replace(" ", "_")
                    cursor.execute("""
                    INSERT INTO kg_edges (source_id, target_id, relationship, weight)
                    VALUES (?, ?, ?, ?)
                    """, (doc_node_id, tech_id, "USES_OR_REFERENCES", 1.0))

    # Ingest Synthesized Golden Master Playbooks (03_Topics_and_Projects/)
    if TOPICS_DIR.exists():
        for root, _, files in os.walk(TOPICS_DIR):
            for f in files:
                if not f.endswith(".md"):
                    continue
                file_path = Path(root) / f
                ext = ".md"
                size_kb = round(file_path.stat().st_size / 1024, 2)
                rel_path = str(file_path.relative_to(BASE_DIR)).replace('\\', '/')
                
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                fm, body = extract_yaml_frontmatter(content)
                
                title = fm.get("title", file_path.stem) if fm else file_path.stem
                topic = fm.get("domain", file_path.parent.name) if fm else file_path.parent.name
                workability = fm.get("workability_status", "Production-Ready") if fm else "Production-Ready"
                rating = "Must Keep - High Reusability"
                tags_list = fm.get("tags", ["Golden Master", "Playbook"]) if fm else ["Golden Master"]
                tags_str = ", ".join(tags_list) if isinstance(tags_list, list) else str(tags_list)
                problem_solved = f"Institutional Golden Master Playbook for {topic}"
                
                cursor.execute("""
                INSERT OR REPLACE INTO documents (file_name, relative_path, asset_title, format, topic, problem_solved, workability, rating, tags, size_kb)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (file_path.name, rel_path, title, "Golden Master Playbook", topic, problem_solved, workability, rating, tags_str, size_kb))
                
                doc_id = cursor.lastrowid
                file_count += 1
                
                gm_node_id = f"gm_{file_path.stem.lower()}"
                cursor.execute("INSERT OR REPLACE INTO kg_nodes (id, label, node_type, details) VALUES (?, ?, ?, ?)",
                               (gm_node_id, title[:30], "Golden Master Playbook", f"Domain: {topic} | Status: {workability}"))
                               
                # Connect to Domain Hub
                dom_hub_id = topic.lower()
                cursor.execute("""
                INSERT INTO kg_edges (source_id, target_id, relationship, weight)
                VALUES (?, ?, ?, ?)
                """, (gm_node_id, dom_hub_id, "BELONGS_TO_DOMAIN", 2.0))
                
                chunks = chunk_text(content)
                for idx, c_text in enumerate(chunks):
                    total_chunks += 1
                    cursor.execute("INSERT INTO chunks (doc_id, chunk_index, chunk_text, char_count) VALUES (?, ?, ?, ?)",
                                   (doc_id, idx, c_text, len(c_text)))
                    cursor.execute("""
                    INSERT INTO chunks_fts (chunk_text, asset_title, topic, problem_solved, file_name)
                    VALUES (?, ?, ?, ?, ?)
                    """, (c_text, title, topic, problem_solved, file_path.name))
                    
                # Link to technologies
                combined_sample = content[:4000].lower()
                for tech, (ntype, _) in tech_keywords.items():
                    if tech.lower() in combined_sample:
                        tech_id = tech.lower().replace(" ", "_")
                        cursor.execute("""
                        INSERT INTO kg_edges (source_id, target_id, relationship, weight)
                        VALUES (?, ?, ?, ?)
                        """, (gm_node_id, tech_id, "USES_OR_REFERENCES", 1.0))
                        
    conn.commit()
    print(f"\nKnowledge Store successfully loaded! Ingested {file_count} documents and {total_chunks} search chunks into {DB_PATH}.")
    conn.close()

if __name__ == "__main__":
    populate_knowledge_store()
