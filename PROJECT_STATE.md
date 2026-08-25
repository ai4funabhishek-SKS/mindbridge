# PROJECT_STATE.md — Second Brain Knowledge Base (L1)

## 1. Mission & Objective
Transform 443 raw files (MD/JSON/PDF/TXT/DOCX/XLSX) on this laptop into a
structured, searchable, intelligent Second Brain: private vault for sensitive
documents, a 10-domain curated library of 46 Golden Master playbooks, hybrid
search (SQLite FTS5 + knowledge graph), visual dashboards, and an automated
test suite — all non-destructive to the original raw files.

## 2. 🔒 Active Worker
| Field | Value |
|---|---|
| Claimed by | opencode (session: search-quality improvement planning) |
| Claimed at | 2026-08-25 12:30 |
| Status | ACTIVE |

## 3. Current Status
🟢 **M6 SMART SEARCH + SMART INDEXES (2026-08-25) — 6/7 tasks done.**
New capabilities shipped and committed:
- **M6a** Per-folder CSV indexes + MASTER_ASSET_INDEX.csv: all 156 Asset-Library
  files catalogued (13 columns incl. related_files, gem flags); builder
  `build_folder_indexes.py`; idempotent.
- **M6b** Document fingerprints: `build_doc_anchors.py` → doc_anchors table,
  502/502 docs (461 real + 41 hollow zero-vectors; filler metadata stripped).
- **M6c** Anchor rank-fusion + per-doc result diversity in semantic/hybrid.
  ACCEPTANCE PROVEN: "find clients for finance advisory" now ranks the
  subbroking playbook #3 (was absent from top-50, buried under SEBI PDFs/CVs).
- **M6d** `--topic` filter + `--topics` listing + `--gems` (rating≥8) on all modes.
- **M6e** `--mode ask`: funnel retrieval → local LLM synthesis with [S#] source
  citations; `--model` ladder (llama3.2 default → phi3 fallback) with automatic
  RAM-fallback; native chat API keep_alive=0 frees RAM after each answer;
  `--save` writes Obsidian-ready briefs to `Briefings/`.
Test suite: **177 passed / 4 skipped** (skips = live LLM tests gated on free RAM).
**PENDING:** live E2E proof of Ask mode blocked by machine RAM (<2.7GB free);
needs ~150MB more freed (WSL shutdown or closing apps). Task 7 brutal review
pending. GitHub push still parked pending owner repo decision.

## 4. Milestone Log
| Date | Milestone | Status | Notes |
|---|---|---|---|
| 2026-08-15→16 | M1 Vault segregation & cold storage | DONE | 73 sensitive files isolated; 0 deletions in Raw_copies |
| 2026-08-17 | M2 10-domain taxonomy + 46 playbooks | DONE | YAML frontmatter + lineage standardized |
| 2026-08-17→18 | M3 Dashboards + RAG/KG DB + CLI search | DONE | Excel 8-tab, 2 HTML navigators, sub-second BM25 |
| 2026-08-18 | M4 E2E test suite + forensic audit | DONE | see TEST_READY.md |
| 2026-08-18 (crashed) | M5 deep-processing 443 files | PARTIAL | 186/443 deep-classified; run died at ~186 |
| 2026-08-23 | Crash recovery & mission reconstruction | DONE | owner confirmed lost context; resumed M5 |
| 2026-08-23 | M5 deep-processing 443/443 + security hardening | DONE | 96/96 tests; see batches 01-11 + redaction commits |
| 2026-08-24 | M5b semantic index 10,785/10,785 embedded | DONE | survived UI freeze mid-run; crash-safe resume worked |
| 2026-08-24 | Domain anomaly resolved (42 manifest fixes) | DONE | backup kept; 96/96 tests re-verified |
| 2026-08-25 | M5c semantic + hybrid (RRF) search modes | DONE | 4 search modes; 139/139 tests pass |
| 2026-08-25 | M6a CSV asset indexes (156 files, 13 cols) | DONE | per-folder + master; 8 tests |
| 2026-08-25 | M6b doc fingerprints 502/502 | DONE | filler stripped; hollow → zero-vec |
| 2026-08-25 | M6c anchor fusion + diversity cap | DONE | finance-advisory acceptance PROVEN |
| 2026-08-25 | M6d --topic/--topics/--gems | DONE | all modes; 174/174 at commit |
| 2026-08-25 | M6e ask mode + briefings + model ladder | CODE DONE | live E2E pending free RAM |

## 5.1 M5 Final Statistics (2026-08-23, split corrected 2026-08-24)
- Classification: 255 merge_into_gm · 149 archive · 39 reference_only · 0 pending
- 117 files scored reusability ≥8 ("gems"); avg score 4.92
- Credentials: live keys found in my_api_keys_backup.md, key.txt (DeepInfra+Jina),
  test.env.txt (Groq), Google OAuth client-secret json — all local-only
- Redacted from public tiers: sk- key ×3 (GM_Developer_Assistant), Tavily key ×3
  (GM_AI_Search) + 6 library copies. Originals preserved in Raw_copies.
- Git protections: Raw_copies/, vault, RAG DB + 7 residual risky files excluded

## 5. Achievements
- 443 raw assets preserved immutably (`Raw_copies/`)
- `01_Vault_Private/` (73 sensitive files, gitignored) + `04_Archive_Cold_Storage/`
- 46 Golden Master Playbooks across 10 canonical domains (`03_Topics_and_Projects/`)
- `Processed_Assets/my_rag_data.db`: documents/chunks/chunks_fts/kg_nodes/kg_edges
- Dashboards: Master Excel workbook, Interactive HTML Navigator, Knowledge Graph explorer
- `search_engine.py` verified (linear + graph modes); full test suite in `tests/`

## 6. Decisions Log
| Date | Decision | Why | Alternatives rejected |
|---|---|---|---|
| Aug 2026 | Non-destructive pipeline (copy, never move/delete originals) | Owner requirement: zero data loss | In-place reorganisation |
| Aug 2026 | SQLite FTS5 + KG tables instead of external vector DB | Free, local, no service dependency | Pinecone/cloud RAG |
| Aug 2026 | Sensitive files out of git via `.gitignore` | Privacy + repo portability | Encrypted commits |
| Aug 2026 | Move active work to quota-independent tools (opencode/Kilo) | Antigravity quota kept blocking deadlines | Waiting for quota reset |

## 7. Next Steps & Open Questions
1. ~~M5 Phase 2 (active): deep-process remaining 257 files~~ DONE (see M5 log).
2. GitHub push only after owner provides repo + approves; recommend Private;
   scrub dashboard exports first; rotate live keys before any external sharing.
3. **M6 finish line:** free ~150MB RAM (owner decision: wsl --shutdown or close
   apps) → run live Ask E2E tests → Task 7 brutal review report.
4. Known data debt: 242 docs carry generic topic "General Knowledge"; 145/156
   library files have rich catalogue entries, 11 generated artifacts don't.
   Optional future pass: relabel topics + AI-enrich descriptions.

## 8. Blockers & Gotchas
- Antigravity quota exhaustion repeatedly interrupted work (resets daily).
- Free LLM providers via OmniRoute can drop connections mid-run ("Cannot connect"); sessions survive — always resume via PROJECT_STATE.md, never restart from scratch.
- `.gitignore` protects vault/credentials — never weaken it.

## 9. Environment Map
- Root: `C:\knowledgeBase_staging`
- Search CLI: `python search_engine.py --mode linear|graph "<query>"`
- Key scripts: `Collect-KnowledgeBase.ps1`, `Cleanup-RawCopies.ps1`, `process_gms.py`, `copy_raw_assets_to_domains.py`, `init_rag_and_knowledge_graph.py`, `deep_inspect_and_build_dashboard.py`, `generate_master_dashboard.py`
- Docs: `PROJECT.md` (architecture/contracts), `ORIGINAL_REQUEST.md`, `TEST_READY.md`, `TEST_INFRA.md`
- Secrets: none in repo; real credentials live in `01_Vault_Private/credentials_and_keys/` (gitignored)

## 10. 🔄 Handoff Capsule (paste into any other AI tool)
```
CONTEXT: C:\knowledgeBase_staging — Second Brain KB: 443 raw files refined
into vault + 10-domain library (49 playbooks) + FTS5/KG database (502 docs,
10785 chunks, 502 doc anchors) + dashboards + CSV asset indexes (156 files,
13 cols) + 177-test suite. Owner is non-technical, decides in plain language.
STATE:   M1-M6a..e DONE 2026-08-25: search_engine.py has 5 modes — linear,
graph, semantic, hybrid (RRF), ask (funnel retrieval → local LLM synthesis
with [S#] citations; --model llama3.2 default w/ RAM fallback ladder;
--save writes Obsidian briefs to Briefings/). Doc-anchor fingerprints fused
into ranking + per-doc diversity cap (MAX_PER_DOC=2) fixed vague-query
failure: "find clients for finance advisory" → subbroking playbook top-3.
--topic/--topics/--gems filters on all modes.
NEXT:    live Ask E2E blocked on ~150MB RAM (wsl --shutdown or close apps);
then Task-7 brutal review; GitHub push only after owner names repo+approves
(recommend Private; scrub dashboard exports first); rotate live keys before
external sharing.
GOTCHAS: free providers/quota drops interrupt runs — small committed
increments only. Raw_copies/ + vault + RAG DB stay out of git. Live keys in
01_Vault_Private/credentials_and_keys/. Semantic/ask modes need local Ollama;
ask needs ~3GB free RAM (16GB machine, WSL VM eats 2.2GB).
RULES:   read+update this PROJECT_STATE.md, claim 🔒 Active Worker before
work, commit checkpoints, verify-before-done mandate is in global AGENTS.md,
never delete data / spend money / publish without owner approval.
```
