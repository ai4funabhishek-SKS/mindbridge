-- Core Relational Document Store
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    asset_title TEXT,
    format TEXT NOT NULL,
    topic TEXT NOT NULL,
    problem_solved TEXT,
    workability TEXT,
    rating REAL,
    tags TEXT,
    size_kb REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chunked Text Store for RAG
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    token_count INTEGER,
    FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- SQLite FTS5 Full-Text Search Virtual Table
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    chunk_text,
    asset_title UNINDEXED,
    topic UNINDEXED,
    file_name UNINDEXED,
    tokenize = 'porter unicode61'
);

-- Knowledge Graph Nodes (Entities)
CREATE TABLE IF NOT EXISTS kg_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT UNIQUE NOT NULL,
    node_type TEXT NOT NULL, -- Domain | Tool | Framework | Protocol | Workflow
    details TEXT,
    count INTEGER DEFAULT 1
);

-- Knowledge Graph Edges (Relationships)
CREATE TABLE IF NOT EXISTS kg_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    relationship TEXT NOT NULL, -- IMPLEMENTS | USES | BELONGS_TO | ORCHESTRATES
    weight REAL DEFAULT 1.0,
    FOREIGN KEY (source_id) REFERENCES kg_nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES kg_nodes(id) ON DELETE CASCADE
);
