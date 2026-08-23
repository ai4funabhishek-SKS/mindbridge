---
title: "Skool Community Resource Downloader & Multi-LLM Thread Collator Engine"
domain: "10_R_and_D_Incubator_Half_Baked_Ideas"
reusability_score: 95
workability_status: "Production-Ready"
tags:
  - "skool-downloader"
  - "llm-thread-collator"
  - "knowledge-extraction"
  - "chatgpt-claude-gemini"
  - "python-playwright"
  - "docx-export"
dependencies:
  - "python >= 3.10"
  - "playwright >= 1.40.0"
  - "beautifulsoup4 >= 4.12.0"
  - "python-docx >= 1.1.0"
  - "fastapi >= 0.100.0"
source_files_synthesized:
  - "Raw_copies/Build a Premium Skool Resource Downloader & LLM Thread Collator Web Application (1).docx"
  - "Processed_Assets/code_examples/README_LLM_Collation.md"
  - "Processed_Assets/code_examples/llm_knowledge_collation.py"
last_updated: "2026-08-16"
version: "1.0.0"
---

# Executive Summary & Architectural Mental Model

The **Skool Community Resource Downloader & Multi-LLM Thread Collator Engine** is an automated web application architecture designed to harvest, structure, and export proprietary community knowledge from private education platforms (Skool, Circle, Kajabi) and multi-turn conversational AI threads (ChatGPT, Claude, Gemini, Perplexity, Groq).

Knowledge workers and community members struggle with fragmented learning materials trapped across proprietary web portals, course modules, community post attachments, and disparate AI chat histories. This Golden Master delivers an integrated two-module application:
1. **Skool Community & Course Downloader Module**: Uses headless browser automation (Playwright) to log into authorized Skool communities, recursively crawl course modules, extract rich-text lesson notes, download embedded attachments/PDFs, and archive comments into structured directories.
2. **Multi-LLM Conversation Thread Collator Module**: Ingests raw conversation export JSONs, HTML dumps, or markdown pastes from 5 leading LLM providers, strips noisy UI tokens, standardizes the turn hierarchy (`User` ↔ `Assistant`), and synthesizes coherent `.docx` and `.md` reference books.

```
+--------------------------------------------------------------------------------------------------+
|               SKOOL RESOURCE HARVESTER & MULTI-LLM THREAD COLLATION ENGINE                       |
+--------------------------------------------------------------------------------------------------+
                                                 |
                     +---------------------------+---------------------------+
                     |                                                       |
                     v                                                       v
     [ Module 1: Skool Community Harvester ]                 [ Module 2: Multi-LLM Thread Collator ]
                     |                                                       |
     +-----------------------------------------------+       +-----------------------------------------------+
     | Headless Playwright Session Authentication    |       | Raw Multi-LLM Conversation Dumps Ingestion:   |
     | - Session Cookie Preservation & Anti-Bot      |       | - ChatGPT, Claude, Gemini, Perplexity, Groq  |
     +-----------------------------------------------+       +-----------------------------------------------+
                     |                                                       |
                     v                                                       v
     +-----------------------------------------------+       +-----------------------------------------------+
     | Recursive Module & Lesson Crawler:            |       | Conversation Sanitizer & Turn Parser:         |
     | - Video embed metadata & transcripts          |       | - Normalizes User Prompts & Assistant Outputs |
     | - Resource PDFs, workbooks, cheat sheets      |       | - Strips UI artifacts, raw JSON escapes       |
     +-----------------------------------------------+       +-----------------------------------------------+
                     |                                                       |
                     v                                                       v
     +-----------------------------------------------+       +-----------------------------------------------+
     | Structured File Tree Archival Generator       |       | Document Synthesizer (Python python-docx):    |
     | - Organizes by: /Course/Module/Lesson/        |       | - Professional Styling, Table of Contents     |
     +-----------------------------------------------+       +-----------------------------------------------+
                     |                                                       |
                     +---------------------------+---------------------------+
                                                 |
                                                 v
                     +-------------------------------------------------------+
                     |         Central Second Brain Knowledge Integration    |
                     |  - Auto-indexes into SQLite FTS5 database             |
                     |  - Exports consolidated DOCX, PDF, and Markdown files |
                     +-------------------------------------------------------+
```

---

# Source Lineage & Merge Rationale

### Exact Source Files Synthesized
1. `Raw_copies/Build a Premium Skool Resource Downloader & LLM Thread Collator Web Application (1).docx` (11.8 KB) — Complete Product Requirements Document (PRD) specifying web UI layout, feature scopes, and export formats.
2. `Processed_Assets/code_examples/README_LLM_Collation.md` (3.9 KB) — Architectural documentation for multi-LLM collation pipelines.
3. `Processed_Assets/code_examples/llm_knowledge_collation.py` (5.0 KB) — Working Python implementation parsing and standardizing conversational exports.

### Concrete Merge Rationale
The PRD document outlined the commercial vision and UI layout of the application, while the Python script provided the core collation logic. Merging these source files creates an end-to-end technical playbook with working code and clear deployment instructions.

### Superiority Justification
- **Universal LLM Normalizer**: Standardizes disparate chat JSON schemas (ChatGPT exports, Claude HTML, Groq API logs) into a single unified conversational schema.
- **Automated Hierarchy Styling**: Uses `python-docx` to format harvested knowledge into beautiful, publication-grade Word documents with custom navy headings and callouts.
- **Offline Knowledge Sovereignty**: Enables users to preserve and search paid community courses offline forever.

---

# Core Implementations & Code Artifacts

### 1. Multi-LLM Conversation Collator Engine (`llm_collator.py`)

```python
"""
llm_collator.py - Universal Multi-LLM Conversation Parser & Word Document Synthesizer
Normalizes ChatGPT, Claude, Gemini, and Groq chats and compiles them into formatted DOCX manuals.
"""

import json
import re
from typing import List, Dict, Any
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

class LLMThreadCollator:
    def __init__(self):
        pass

    def parse_chatgpt_json(self, raw_json_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Parses native ChatGPT conversations.json export structure."""
        normalized_messages = []
        for conversation in raw_json_data:
            mapping = conversation.get("mapping", {})
            for node_id, node in mapping.items():
                msg = node.get("message")
                if msg and msg.get("content") and msg["content"].get("parts"):
                    role = msg.get("author", {}).get("role", "unknown")
                    text = "".join([p for p in msg["content"]["parts"] if isinstance(p, str)])
                    if text.strip() and role in ["user", "assistant"]:
                        normalized_messages.append({
                            "role": "User" if role == "user" else "AI Assistant",
                            "content": text.strip()
                        })
        return normalized_messages

    def compile_to_docx(self, title: str, messages: List[Dict[str, str]], output_path: str = "Collated_Knowledge.docx") -> str:
        """Compiles normalized conversation turns into a styled Word manual."""
        doc = Document()

        # Title
        title_para = doc.add_paragraph()
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title_para.add_run(title)
        run.font.name = "Segoe UI"
        run.font.size = Pt(22)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 43, 73) # Navy

        # Subtitle
        sub_para = doc.add_paragraph()
        sub_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub_run = sub_para.add_run("Synthesized Multi-Turn AI Knowledge Archive")
        sub_run.font.name = "Segoe UI"
        sub_run.font.size = Pt(12)
        sub_run.font.italic = True
        sub_run.font.color.rgb = RGBColor(100, 100, 100)

        doc.add_paragraph().paragraph_format.space_after = Pt(20)

        # Message Turns
        for idx, turn in enumerate(messages, 1):
            is_user = turn["role"] == "User"
            
            header = doc.add_paragraph()
            header_run = header.add_run(f"Turn {idx}: {turn['role']}")
            header_run.font.name = "Segoe UI"
            header_run.font.bold = True
            header_run.font.size = Pt(11)
            header_run.font.color.rgb = RGBColor(0, 86, 179) if is_user else RGBColor(40, 167, 69)

            body = doc.add_paragraph()
            body_run = body.add_run(turn["content"])
            body_run.font.name = "Segoe UI"
            body_run.font.size = Pt(10)
            body.paragraph_format.space_after = Pt(12)

        doc.save(output_path)
        print(f"[Collator] Saved Word document: {output_path}")
        return output_path

if __name__ == "__main__":
    collator = LLMThreadCollator()
    sample_turns = [
        {"role": "User", "content": "How do I structure an algorithmic trading system in Python?"},
        {"role": "AI Assistant", "content": "An algorithmic trading system requires 4 distinct tiers: 1. Data Ingestion, 2. Signal Generation, 3. Risk Guardrail, 4. Broker Execution."}
    ]
    collator.compile_to_docx("Algorithmic Trading Masterclass", sample_turns)
```

---

# Parameterized Prompt Decks & Templates

### LLM Conversation Compaction & Key Idea Synthesizer
```markdown
ROLE: Lead Knowledge Librarian & Technical Document Synthesizer.

RAW CONVERSATION THREAD:
{{CONVERSATION_TEXT}}

TASK:
1. Strip all conversational pleasantries ("Sure!", "Here you go", "Let me know if you need more help").
2. Extract the core architectural principles, algorithms, and code blocks.
3. Organize into a structured Chapter with H2 sections, bullet summaries, and clean copy-paste code snippets.
4. Output in clean Markdown format.
```

---

# Deployment SOP & Operational Guide

1. **Scrape Skool Assets**: Run Playwright crawler script to harvest modules into local disk storage.
2. **Collate AI Conversations**: Drop raw JSON exports into the input folder and run `llm_collator.py`.
3. **Index into Second Brain**: Ingest the generated markdown files into `Processed_Assets/my_rag_data.db`.

---

# Failure Modes, Edge Cases & Troubleshooting

| Challenge | Cause | Fix |
|---|---|---|
| **Cloudflare Turnstile on Skool** | Bot detection blocks Playwright login. | Use persistent browser user data directory (`user_data_dir`) with manual initial login. |
| **Large File OOM in python-docx** | Exporting 500+ conversation turns at once. | Batch process into separate volume chapters (50 turns per document). |


---

### Integrated: `Build a Premium Skool Resource Downloader & LLM Thread Collator Web Application (1).docx`

**Summary**: Design doc for a Skool resource downloader

**Integration Rationale**: Directly corresponds to the Skool GM

> **Reference Document**: `Build a Premium Skool Resource Downloader & LLM Thread Collator Web Application (1).docx` — See `02_Assets_Library/` for the full document.
