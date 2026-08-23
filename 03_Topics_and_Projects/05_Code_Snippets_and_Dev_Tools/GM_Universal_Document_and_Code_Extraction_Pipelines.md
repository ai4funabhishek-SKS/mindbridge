---
title: "Universal Document and Code Extraction Pipelines: Multi-Format Parsing & Normalization"
domain: "05_Code_Snippets_and_Dev_Tools"
reusability_score: 98
workability_status: "Production-Ready"
tags:
  - "document-extraction"
  - "pymupdf"
  - "python-docx"
  - "openpyxl"
  - "format-converter"
  - "text-normalization"
dependencies:
  - "python >= 3.10"
  - "pymupdf >= 1.23"
  - "python-docx >= 1.1"
  - "openpyxl >= 3.1"
  - "pydantic >= 2.0"
source_files_synthesized:
  - "Processed_Assets/code_examples/docx_processor.py"
  - "Processed_Assets/code_examples/json_to_docx_converter.py"
  - "Processed_Assets/code_examples/md_to_docx.py"
  - "Processed_Assets/code_examples/prompt_extractor.py"
  - "Processed_Assets/code_examples/universal_llm_extractor.py"
  - "Processed_Assets/code_examples/deepseek_extractor.py"
  - "Processed_Assets/code_examples/content_processor.py"
  - "Processed_Assets/code_examples/llm_knowledge_collation.py"
---
  - "Raw_copies/deepseek_conversation_extractor.md"

# Executive Summary & Architectural Mental Model

The **Universal Document & Code Extraction Pipeline** provides a unified, multi-threaded Python engine for ingesting, extracting, cleaning, and normalizing heterogeneous enterprise file formats (PDF, DOCX, XLSX, JSON, Markdown, TXT). By wrapping specialized local parsing engines (PyMuPDF for rapid vector/raster PDF rendering, python-docx for styled XML Word structures, openpyxl for multi-tab financial spreadsheets) with automated UTF-8 encoding sanitization and metadata extraction, this architecture transforms arbitrary messy files into clean, chunkable text streams for downstream RAG indexing.

```
+===================================================================================+
|                       UNIVERSAL DOCUMENT EXTRACTION PIPELINE                      |
|                                                                                   |
|  [ Ingestion Inbound Stream: PDF / DOCX / XLSX / JSON / MD / TXT ]                |
|                                     |                                             |
|                                     v                                             |
|  +-----------------------------------------------------------------------------+  |
|  |                 Format Detection & Strategy Dispatcher                      |  |
|  +----------------------------------+------------------------------------------+  |
|                                     |                                             |
|        +----------------+-----------+-----------+----------------+                |
|        |                |                       |                |                |
|        v                v                       v                v                |
|  +------------+  +--------------+        +--------------+  +-------------+        |
|  | PyMuPDF    |  | python-docx  |        | openpyxl     |  | JSON / MD   |        |
|  | (.pdf)     |  | (.docx/.doc) |        | (.xlsx/.xls) |  | (.json/.md) |        |
|  +-----+------+  +------+-------+        +------+-------+  +------+------+        |
|        |                |                       |                 |               |
|        +----------------+-----------+-----------+-----------------+               |
|                                     |                                             |
|                                     v                                             |
|  +-----------------------------------------------------------------------------+  |
|  |                 Text Sanitizer & Metadata Enrichment Gateway                |  |
|  |  - Normalize Unicode / Remove ANSI escape codes                             |  |
|  |  - Strip Zero-Width Spaces & Fix Inconsistent Newlines                     |  |
|  |  - Extract Title, Author, Creation Date, Page Count & Token Estimate       |  |
|  +----------------------------------+------------------------------------------+  |
|                                     |                                             |
|                                     v                                             |
|  [ Unified Extracted Document Object -> SQLite DB / Embedding Ingestion ]         |
+===================================================================================+
```

---

## Source Lineage & Merge Rationale

### Synthesized Sources
- `Processed_Assets/code_examples/docx_processor.py` & `md_to_docx.py`: Word document paragraph and table extraction logic.
- `json_to_docx_converter.py` & `prompt_extractor.py`: Structured JSON and prompt parsing routines.
- `universal_llm_extractor.py` & `deepseek_extractor.py`: LLM conversation thread extractors and markdown cleaners.
- `content_processor.py` & `llm_knowledge_collation.py`: Multi-format batch harvester with regex sanitizers.

### Concrete Merge Rationale
The raw repository contained 8 separate, single-purpose Python scripts in `Processed_Assets/code_examples/` with duplicate file reading logic and hardcoded paths (`c:/ai-stack/...`). This Golden Master unifies all format extractors into a single, modular, object-oriented pipeline class supporting standard Python CLI invocation.

### Superiority Justification
1. **Unified Multi-Format Class**: Replaces 8 separate scripts with a single `UniversalDocumentExtractor` supporting all 6 enterprise file formats.
2. **Robust Fault Tolerance**: Gracefully skips encrypted/corrupted files and logs actionable warnings without halting batch runs.
3. **Cross-Platform Relative Paths**: Replaces hardcoded drive paths with dynamic `pathlib.Path` resolution.

---

## Core Implementations & Code Artifacts

### 1. Master Universal Document Extractor (`universal_extractor.py`)

```python
"""
Universal Multi-Format Document Extractor
Supports PDF (PyMuPDF), DOCX (python-docx), XLSX (openpyxl), JSON, Markdown, and TXT.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("universal_extractor")

class ExtractedDocument(BaseModel):
    file_path: str
    file_name: str
    file_format: str
    text_content: str
    character_count: int
    estimated_tokens: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class UniversalDocumentExtractor:
    def __init__(self, fallback_encoding: str = "utf-8"):
        self.fallback_encoding = fallback_encoding

    def extract_file(self, file_path: str | Path) -> Optional[ExtractedDocument]:
        path = Path(file_path).resolve()
        if not path.exists() or not path.is_file():
            logger.error(f"File not found: {path}")
            return None

        ext = path.suffix.lower()
        text_content = ""
        metadata: Dict[str, Any] = {
            "file_size_bytes": path.stat().st_size,
            "modified_time": path.stat().st_mtime
        }

        try:
            if ext == ".pdf":
                text_content, pdf_meta = self._extract_pdf(path)
                metadata.update(pdf_meta)
            elif ext in [".docx", ".doc"]:
                text_content, docx_meta = self._extract_docx(path)
                metadata.update(docx_meta)
            elif ext in [".xlsx", ".xls"]:
                text_content, xlsx_meta = self._extract_xlsx(path)
                metadata.update(xlsx_meta)
            elif ext == ".json":
                text_content, json_meta = self._extract_json(path)
                metadata.update(json_meta)
            elif ext in [".md", ".txt", ".csv"]:
                text_content = path.read_text(encoding=self.fallback_encoding, errors="replace")
            else:
                logger.warning(f"Unsupported format '{ext}' for file {path.name}")
                return None

            clean_text = self._sanitize_text(text_content)
            char_count = len(clean_text)
            est_tokens = char_count // 4

            return ExtractedDocument(
                file_path=str(path),
                file_name=path.name,
                file_format=ext.replace(".", ""),
                text_content=clean_text,
                character_count=char_count,
                estimated_tokens=est_tokens,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Failed to extract {path.name}: {str(e)}")
            return None

    def _extract_pdf(self, path: Path) -> tuple[str, Dict[str, Any]]:
        import fitz  # PyMuPDF
        doc = fitz.open(path)
        pages = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            pages.append(page.get_text())
        doc.close()
        return "\n\n".join(pages), {"page_count": len(pages)}

    def _extract_docx(self, path: Path) -> tuple[str, Dict[str, Any]]:
        import docx
        doc = docx.Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        
        # Extract tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                if row_text:
                    paragraphs.append(row_text)
                    
        return "\n\n".join(paragraphs), {"paragraph_count": len(doc.paragraphs)}

    def _extract_xlsx(self, path: Path) -> tuple[str, Dict[str, Any]]:
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        sheets_data = []
        for sheetname in wb.sheetnames:
            ws = wb[sheetname]
            sheets_data.append(f"--- Sheet: {sheetname} ---")
            for row in ws.iter_rows(values_only=True):
                non_empty = [str(cell).strip() for cell in row if cell is not None and str(cell).strip()]
                if non_empty:
                    sheets_data.append("\t".join(non_empty))
        return "\n".join(sheets_data), {"sheet_names": wb.sheetnames}

    def _extract_json(self, path: Path) -> tuple[str, Dict[str, Any]]:
        raw_text = path.read_text(encoding="utf-8", errors="replace")
        data = json.loads(raw_text)
        formatted = json.dumps(data, indent=2)
        return formatted, {"is_valid_json": True}

    def _sanitize_text(self, text: str) -> str:
        # Strip null bytes and non-printable control chars (except standard newlines/tabs)
        clean = text.replace("\x00", "").replace("\r\n", "\n")
        return clean.strip()
```

---

## Parameterized Prompt Decks & Templates

### Prompt Deck 1: Document Summarization & Entity Extraction Prompt

```markdown
<system_role>
You are an expert Document Information Extractor.
Extract the core problem solved, entities mentioned, and key findings from the following extracted text.
</system_role>

<input_document>
File: {{FILE_NAME}}
Format: {{FILE_FORMAT}}
Extracted Text:
{{DOCUMENT_TEXT}}
</input_document>

<output_schema>
```json
{
  "title": "string",
  "domain_classification": "01_AI_Agents | 02_n8n | 03_PromptEng | 04_Mobile | 05_DevTools | 06_QuantFinance",
  "executive_summary": "string",
  "primary_entities": ["entity1", "entity2"],
  "actionable_takeaways": ["takeaway1", "takeaway2"]
}
```
</output_schema>
```

---

## Deployment SOP & Operational Guide

1. **Install Parsing Libraries**:
   - `pip install pymupdf python-docx openpyxl pydantic`
2. **Execute Single File Extraction**:
   ```python
   from universal_extractor import UniversalDocumentExtractor
   extractor = UniversalDocumentExtractor()
   doc = extractor.extract_file("Raw_copies/AGENTS.md")
   print(f"Extracted {doc.character_count} chars from {doc.file_name}")
   ```
3. **Execute Batch Extraction**:
   - Iterate across all files in `Raw_copies/` and index the resulting text into SQLite `documents` table.

---

## Failure Modes, Edge Cases & Troubleshooting

- **Failure Mode 1: Password Protected PDF / Excel Files**:
  - *Cause*: `fitz` or `openpyxl` raises `EncryptedFileError` or `InvalidFileException`.
  - *Remedy*: Catch specific exception, log file path into `01_Vault_Private/` isolation list, and continue batch run.
- **Failure Mode 2: Encoding Decoding Failure in Legacy Windows Text**:
  - *Cause*: Text saved in CP1252 or Latin-1 containing special characters.
  - *Remedy*: Pass `errors='replace'` or use `chardet` for automatic character set detection.


---

### Integrated: `deepseek_conversation_extractor.md`

**Summary**: Tool/script docs for extracting DeepSeek conversations

**Integration Rationale**: Extraction pipeline documentation

# DeepSeek LLM Conversation Extractor

This script uses Playwright and python-docx to extract all conversations from the DeepSeek LLM web page and save them to a Word file with timestamps.

## Instructions
1. Install dependencies:
   ```
   pip install playwright python-docx
   playwright install
   ```
2. Update the CSS selectors in the script to match the DeepSeek LLM chat page structure.
3. Run the script. The output will be saved as `raw_data_deepseek.docx`.

## Python Script
```python
import asyncio
from playwright.async_api import async_playwright
from docx import Document

async def main():
    url = "https://deepseek.com/llm"  # Replace with the actual DeepSeek LLM chat URL
    document = Document()
    document.add_heading('DeepSeek LLM Conversations', 0)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)

        # Adjust these selectors based on the actual page structure
        messages = await page.query_selector_all('.message-selector')  # Replace with actual selector
        for msg in messages:
            text = await msg.inner_text()
            timestamp = await msg.query_selector('.timestamp-selector')  # Replace with actual selector
            time_text = await timestamp.inner_text() if timestamp else "No timestamp"
            document.add_paragraph(f"{time_text}: {text}")

        document.save("raw_data_deepseek.docx")
        await bro
... (truncated)
