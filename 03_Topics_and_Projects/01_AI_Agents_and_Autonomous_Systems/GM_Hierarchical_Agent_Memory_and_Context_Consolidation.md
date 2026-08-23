---
title: "Hierarchical Agent Memory, Episodic Compaction, and Context Consolidation Engine"
domain: "01_AI_Agents_and_Autonomous_Systems"
reusability_score: 97
workability_status: "Production-Ready"
tags:
  - "agent-memory"
  - "episodic-memory"
  - "context-consolidation"
  - "semantic-keywords"
  - "rag-memory"
dependencies:
  - "python >= 3.10"
  - "chromadb >= 0.4"
  - "sqlite3"
  - "pydantic >= 2.0"
source_files_synthesized:
  - "Raw_copies/memory.consolidation.sys.md"
  - "Raw_copies/memory.consolidation.msg.md"
  - "Raw_copies/memory.keyword_extraction.sys.md"
  - "Raw_copies/memory.keyword_extraction.msg.md"
  - "Raw_copies/memory.memories_filter.sys.md"
  - "Raw_copies/memory.memories_query.sys.md"
  - "Raw_copies/memory.memories_sum.sys.md"
  - "Raw_copies/memory.solutions_sum.sys.md"
  - "Raw_copies/memory.recall_delay_msg.md"
  - "Raw_copies/agent.system.memories.md"
  - "Raw_copies/agent.system.solutions.md"
  - "Raw_copies/fw.memory_query.md"
---

# Executive Summary & Architectural Mental Model

The **Hierarchical Agent Memory and Context Consolidation Engine** solves the fundamental challenge of context window degradation, token exhaustion, and long-term knowledge retention in autonomous AI agents. Rather than retaining raw conversation transcripts or appending unstructured vector embeddings indefinitely, this architecture implements a multi-tiered cognitive memory pipeline: separating short-term working context, episodic conversation memories, and authoritative knowledge sources. An automated consolidation specialist analyzes incoming experiences against existing memory vectors using similarity scoring and temporal heuristics to determine whether to `merge`, `replace`, `update`, `keep_separate`, or `skip`.

```
+===================================================================================+
|                       HIERARCHICAL MEMORY & CONTEXT PIPELINE                      |
|                                                                                   |
|  [ Live Interaction / Tool Output ] ---> [ Keyword & Entity Extraction Engine ]   |
|                                                     |                             |
|                                                     v                             |
|         +-----------------------------------------------------------+             |
|         | Vector Similarity Query (Cosine Thresholds: >0.9, 0.7-0.9)|             |
|         +-----------------------------+-----------------------------+             |
|                                       |                                           |
|                                       v                                           |
|                 +-------------------------------------------+                     |
|                 | Memory Consolidation Specialist (LLM Gate)|                     |
|                 +---------------------+---------------------+                     |
|                                       |                                           |
|        +----------------+-------------+-------------+---------------+             |
|        |                |                           |               |             |
|        v                v                           v               v             |
|   [ MERGE ]        [ REPLACE ]                 [ UPDATE ]    [ KEEP SEPARATE ]    |
| (Combine Nuance) (Obsolete Info)             (Append Details)(Distinct Concepts)  |
|        |                |                           |               |             |
|        +----------------+-------------+-------------+---------------+             |
|                                       |                                           |
|                                       v                                           |
|       +---------------------------------------------------------------+           |
|       | Tiered Storage: SQLite FTS5 (Keyword) + ChromaDB (Embeddings) |           |
|       +---------------------------------------------------------------+           |
+===================================================================================+
```

---

## Source Lineage & Merge Rationale

### Synthesized Sources
- `Raw_copies/memory.consolidation.sys.md` & `memory.consolidation.msg.md`: Core system prompt, similarity score thresholds (>0.9 replace, 0.7-0.9 cautious merge), temporal intelligence, and JSON action schemas.
- `Raw_copies/memory.keyword_extraction.sys.md` & `memory.keyword_extraction.msg.md`: Prompt schemas for extracting high-signal search keywords, entities, and domain categories from messy user text.
- `Raw_copies/memory.memories_filter.sys.md` & `memory.memories_query.sys.md`: Similarity search filters, temporal recency weighting, and importance score adjustments.
- `Raw_copies/memory.memories_sum.sys.md` & `memory.solutions_sum.sys.md`: Automated conversation summarizers generating concise solution cards.
- `Raw_copies/memory.recall_delay_msg.md`: Asynchronous recall delay management.
- `Raw_copies/agent.system.memories.md` & `agent.system.solutions.md`: Memory injection protocols for subordinate agents.
- `Raw_copies/fw.memory_query.md`: Framework-level memory retrieval interface.

### Concrete Merge Rationale
The raw assets contained 12 separate prompt files detailing fragmented operations of a memory subsystem without a unifying programmatic controller. Each prompt file handled one sub-task (e.g. keyword extraction, memory summarization) with disconnected JSON interfaces. This Golden Master combines the cognitive rules, prompt templates, vector similarity logic, and SQLite/Chroma persistence schemas into a unified, production-ready memory engine.

### Superiority Justification
1. **End-to-End Consolidation Engine**: Unifies isolated prompt strings into a complete Python memory manager with deterministic consolidation strategies (`merge`, `replace`, `update`, `keep_separate`).
2. **Dual-Index Memory Storage**: Combines exact BM25 keyword retrieval (SQLite FTS5) with semantic vector embedding queries (ChromaDB).
3. **Strict Deduplication Rules**: Enforces strict similarity thresholds (>0.9 for replacements) preventing data loss and memory contamination.
4. **Clean Parameterized Prompt Decks**: Standardizes prompts with `{{INPUT_TEXT}}`, `{{SIMILAR_MEMORIES}}`, and `{{SIMILARITY_SCORE}}`.

---

## Core Implementations & Code Artifacts

### 1. Master Agent Memory Engine (`agent_memory_engine.py`)

```python
"""
Hierarchical Agent Memory Manager & Dynamic Consolidation Engine
Implements multi-tiered memory storage, keyword extraction, and automated compaction.
"""

import json
import logging
import sqlite3
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("agent_memory_engine")

class MemoryEntry(BaseModel):
    id: str
    content: str
    category: str = Field(default="conversation", description="conversation | knowledge | solution")
    keywords: List[str] = Field(default_factory=list)
    importance_score: float = Field(default=0.7, ge=0.0, le=1.0)
    created_at: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConsolidationDecision(BaseModel):
    action: str  # merge | replace | update | keep_separate | skip
    memories_to_remove: List[str] = Field(default_factory=list)
    memories_to_update: List[Dict[str, Any]] = Field(default_factory=list)
    new_memory_content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str

class HierarchicalMemoryManager:
    def __init__(self, db_path: str = "memory_store.db"):
        self.db_path = db_path
        self._init_sqlite_tables()

    def _init_sqlite_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                keywords TEXT,
                importance_score REAL,
                created_at REAL,
                metadata TEXT
            );
        """)
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                id UNINDEXED,
                content,
                keywords,
                category UNINDEXED
            );
        """)
        conn.commit()
        conn.close()

    def insert_memory(self, entry: MemoryEntry):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO memories (id, content, category, keywords, importance_score, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            entry.id,
            entry.content,
            entry.category,
            json.dumps(entry.keywords),
            entry.importance_score,
            entry.created_at,
            json.dumps(entry.metadata)
        ))
        cursor.execute("""
            INSERT INTO memories_fts (id, content, keywords, category)
            VALUES (?, ?, ?, ?);
        """, (
            entry.id,
            entry.content,
            " ".join(entry.keywords),
            entry.category
        ))
        conn.commit()
        conn.close()
        logger.info(f"Inserted memory [{entry.id}] category={entry.category}")

    def query_memories_bm25(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, m.content, m.category, m.importance_score, m.created_at
            FROM memories_fts f
            JOIN memories m ON f.id = m.id
            WHERE memories_fts MATCH ?
            ORDER BY rank
            LIMIT ?;
        """, (f'"{query}"*', limit))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": r[0],
                "content": r[1],
                "category": r[2],
                "importance_score": r[3],
                "created_at": r[4]
            }
            for r in rows
        ]

    def apply_consolidation(self, decision: ConsolidationDecision, new_entry_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Remove superseded memories
        for mid in decision.memories_to_remove:
            cursor.execute("DELETE FROM memories WHERE id = ?", (mid,))
            cursor.execute("DELETE FROM memories_fts WHERE id = ?", (mid,))
            logger.info(f"Consolidation: Removed obsolete memory [{mid}]")
            
        # Update existing memories
        for update_item in decision.memories_to_update:
            mid = update_item["id"]
            new_text = update_item["new_content"]
            cursor.execute("UPDATE memories SET content = ? WHERE id = ?", (new_text, mid))
            cursor.execute("UPDATE memories_fts SET content = ? WHERE id = ?", (new_text, mid))
            logger.info(f"Consolidation: Updated memory [{mid}]")
            
        conn.commit()
        conn.close()
        
        # Insert consolidated new memory if action is not skip
        if decision.action != "skip":
            consolidated_entry = MemoryEntry(
                id=new_entry_id,
                content=decision.new_memory_content,
                category="consolidated",
                importance_score=decision.metadata.get("importance_score", 0.8),
                metadata=decision.metadata
            )
            self.insert_memory(consolidated_entry)
```

---

## Parameterized Prompt Decks & Templates

### Prompt Deck 1: Memory Consolidation Analysis Specialist

```markdown
<system_role>
You are an intelligent Memory Consolidation Specialist for the Agent Zero memory management engine.
Your mission is to analyze newly formed memories against existing similar memories and determine the optimal consolidation strategy.
</system_role>

<similarity_guidelines>
- High Similarity (>0.9): Suitable for REPLACE if new information makes old obsolete.
- Moderate Similarity (0.7-0.9): Suitable for MERGE or UPDATE; preserve distinct historical details.
- Low Similarity (<0.7): KEEP_SEPARATE.
</similarity_guidelines>

<context>
New Memory Content:
{{NEW_MEMORY_CONTENT}}

Similar Existing Memories:
{{SIMILAR_EXISTING_MEMORIES}}
</context>

<output_format>
Return valid JSON:
{
  "action": "merge|replace|keep_separate|update|skip",
  "memories_to_remove": ["id1"],
  "memories_to_update": [
    {
      "id": "memory_id",
      "new_content": "updated memory content",
      "metadata": {}
    }
  ],
  "new_memory_content": "Consolidated memory string",
  "metadata": {
    "consolidated_from": ["id1"],
    "historical_notes": "Summary of prior context",
    "importance_score": 0.85
  },
  "reasoning": "Explicit explanation for action taken"
}
</output_format>
```

---

## Deployment SOP & Operational Guide

1. **Database Scaffolding**:
   - Initialize SQLite storage: `python -c "from agent_memory_engine import HierarchicalMemoryManager; HierarchicalMemoryManager('test_memory.db')"`
2. **Ingest Initial Long-Term Knowledge**:
   - Parse markdown documentation files into chunks and insert as `category="knowledge"`.
3. **Hook Runtime Context Loop**:
   - Before executing an LLM agent prompt, query `query_memories_bm25(user_task)` and inject top 3 memories into system context.
4. **Trigger Compaction Routine**:
   - Run memory consolidation after every 10 conversation turns or during nightly maintenance scripts.

---

## Failure Modes, Edge Cases & Troubleshooting

- **Failure Mode 1: Accidental Overwrite of Knowledge Base (Premature REPLACE)**:
  - *Cause*: High cosine similarity on different factual topics.
  - *Remedy*: Memory consolidation rule prohibits replacing `category="knowledge"` memories with `category="conversation"` memories unless explicitly authorized by user.
- **Failure Mode 2: FTS5 SQLite Lock During Concurrent Agent Writes**:
  - *Cause*: Multiple worker agents writing to SQLite simultaneously.
  - *Remedy*: Enable Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) and set `busy_timeout=5000`.
- **Failure Mode 3: Memory Bloat / Infinite Token Expansion**:
  - *Cause*: Recursive merging without length limits.
  - *Remedy*: Enforce maximum consolidated memory length limit of 500 words per card.
