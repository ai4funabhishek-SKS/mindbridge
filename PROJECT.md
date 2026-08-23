# Project: Laptop 1 (L1) Second Brain Knowledge Base Refinement & Indexing

## Architecture
The Second Brain repository at `C:\knowledgeBase_staging` is structured into five distinct operational tiers:
1. **Source Tier (`Raw_copies/`)**: Immutable original repository assets (JSON, PDF, DOCX, MD, TXT, XLSX). Guarded by strict 0-deletion non-destructive constraints (443 total assets preserved).
2. **Security & Archive Tier (`01_Vault_Private/`, `04_Archive_Cold_Storage/`)**:
   - `01_Vault_Private/`: Isolated financial statements (26 files), KYC identity (9 files), and API credentials (38 files) protected by `.gitignore`.
   - `04_Archive_Cold_Storage/`: Zero-byte files, temporary lock files, duplicate stubs, and empty boilerplates.
3. **Domain Taxonomy & Synthesis Tier (`02_Assets_Library/`, `03_Topics_and_Projects/`)**:
   - 10 Canonical Domain directories hosting curated assets in `02_Assets_Library/` and 46 high-density Golden Master Playbooks in `03_Topics_and_Projects/`.
   - Standardized YAML frontmatter, source file lineage, merge rationale, superior draft justification, mental models, code blocks, prompt decks, and operational SOPs.
4. **Data & Hybrid Search Tier (`Processed_Assets/my_rag_data.db`, `search_engine.py`)**:
   - SQLite database with FTS5 BM25 full-text search (`chunks_fts`) using Porter stemmer tokenizer.
   - Knowledge Graph tables (`kg_nodes`, `kg_edges`) tracking entities and cross-domain relationships.
   - CLI search engine supporting `--mode linear` and `--mode graph` sub-second queries.
5. **Dashboard & Visual Navigation Tier (`00_Index_and_Dashboards/`)**:
   - `Master_Second_Brain_Knowledge_Mine.xlsx`: 8-tab styled Excel workbook with navy headers, zebra striping, and auto-filters.
   - `Interactive_Knowledge_Mine_Navigator.html`: Chart.js visualizations, 10-domain filter pills, real-time live search, responsive cards.
   - `Interactive_Knowledge_Graph.html`: Vis.js physics-driven network relationship explorer.

---

## Feature Inventory
| # | Feature | Description | Milestone | Status |
|---|---------|-------------|-----------|--------|
| F01 | Raw Source Immutability | Guarantee 0 deletions and complete integrity of all 443 files in Raw_copies/ | M1 | VERIFIED |
| F02 | Private Vault Partitioning | Segregate 73 sensitive bank statements, KYC documents, and API credentials into `01_Vault_Private/` | M1 | VERIFIED |
| F03 | Git Security Protection | Create `.gitignore` at root to prevent remote exposure of `01_Vault_Private/` | M1 | VERIFIED |
| F04 | Cold Storage Clutter Isolation | Quarantine zero-byte files, duplicate stubs, temporary locks, and empty boilerplates into `04_Archive_Cold_Storage/` | M1 | VERIFIED |
| F05 | 10-Domain Taxonomy Scaffolding | Create standard 10-domain folders in `02_Assets_Library/` and `03_Topics_and_Projects/` | M2 | VERIFIED |
| F06 | Format Asset Categorization | Organize assets in `02_Assets_Library/` by format and 10 canonical domains | M2 | VERIFIED |
| F07 | 10-to-1 Markdown Synthesis | Cluster and synthesize raw assets across 10 domains into 46 high-density Golden Master Playbooks | M2 | VERIFIED |
| F08 | YAML Frontmatter & Lineage | Standardize YAML headers (reusability_score, workability_status, tags, dependencies, source_files_synthesized) | M2 | VERIFIED |
| F09 | Merge Rationale & Superiority | Explicitly document source file list, merge rationale, and superior draft justification in each playbook | M2 | VERIFIED |
| F10 | Architecture, Code & Prompt Decks | Extract clean, verified, copy-paste-ready code blocks, n8n JSON nodes, prompt decks, and SOPs | M2 | VERIFIED |
| F11 | Excel Knowledge Mine Dashboard | Update `Master_Second_Brain_Knowledge_Mine.xlsx` with dedicated category sheets, KPI summaries, and auto-filters | M3 | VERIFIED |
| F12 | Interactive HTML Navigator | Update `Interactive_Knowledge_Mine_Navigator.html` with 10 domain pills, Chart.js metrics, and live search | M3 | VERIFIED |
| F13 | SQLite FTS5 RAG Indexing | Re-index `Processed_Assets/my_rag_data.db` with chunked full-text search tables | M3 | VERIFIED |
| F14 | Knowledge Graph DB & HTML | Populate `kg_nodes` and `kg_edges` in DB, and regenerate `Interactive_Knowledge_Graph.html` | M3 | VERIFIED |
| F15 | CLI Search Engine Verification | Verify `search_engine.py` executes linear BM25 and graph queries with sub-second latency | M3 | VERIFIED |
| F16 | E2E Regression & Coverage Test Suite | Build automated opaque-box test runner validating Tiers 1-4 requirements | M4 | VERIFIED |
| F17 | Adversarial Hardening & Integrity Audit | White-box stress testing and forensic integrity verification | M4 | VERIFIED |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Vault Segregation & Cold Storage Isolation | Scaffold `01_Vault_Private/`, `04_Archive_Cold_Storage/`, write `.gitignore`, copy sensitive assets and clutter without touching `Raw_copies/` | none | DONE |
| M2 | 10-Domain Taxonomy & Golden Markdown Synthesis | Scaffold 10 domain directories in `02_` and `03_`, author 46 high-density Golden Master Playbooks with complete YAML frontmatter, lineage, code, prompts, SOPs | M1 | DONE |
| M3 | Dashboards, Visualizations & Hybrid Search DB | Update `Master_Second_Brain_Knowledge_Mine.xlsx`, `Interactive_Knowledge_Mine_Navigator.html`, re-index `Processed_Assets/my_rag_data.db`, regenerate `Interactive_Knowledge_Graph.html`, verify `search_engine.py` | M2 | DONE |
| M4 | E2E Testing Suite & Forensic Integrity Audit | Execute full dual-track opaque-box E2E test suite (Tiers 1-4) and Phase 2 adversarial hardening & forensic audit | M3 | DONE |

---

## Interface Contracts

### 1. Vault & Archive Contract (`01_Vault_Private/` & `04_Archive_Cold_Storage/`)
- `01_Vault_Private/credentials_and_keys/`: 38 sensitive files.
- `01_Vault_Private/financial_statements/`: 26 sensitive files.
- `01_Vault_Private/personal_identity/`: 9 sensitive files.
- `04_Archive_Cold_Storage/`: Zero-byte files, temporary lock files, duplicate stubs, empty boilerplates.
- `.gitignore`: Ignores `01_Vault_Private/`, `*.env`, `*.key`, `*secret*`, `*credential*`, `.~lock*#`, `~$*`.

### 2. 10 Canonical Domain Names (`02_Assets_Library/` & `03_Topics_and_Projects/`)
1. `01_AI_Agents_and_Autonomous_Systems`
2. `02_Workflow_Automations_n8n`
3. `03_Prompt_Engineering_and_Frameworks`
4. `04_Mobile_and_Android_Ecosystem`
5. `05_Code_Snippets_and_Dev_Tools`
6. `06_Quantitative_Finance_and_Trading`
7. `07_Content_Creation_and_Media_Engines`
8. `08_Business_Operations_and_Subbroking`
9. `09_LLM_Conversations_and_Syntheses`
10. `10_R_and_D_Incubator_Half_Baked_Ideas`

### 3. Golden Master Markdown Specification
Every synthesized playbook in `03_Topics_and_Projects/<domain>/` adheres to the 6-part contract and YAML frontmatter schema.

### 4. Database Schema Contract (`Processed_Assets/my_rag_data.db`)
- `documents`, `chunks`, `chunks_fts`, `kg_nodes`, `kg_edges` populated and verified.
