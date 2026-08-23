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
| Claimed by | opencode (session: crash-recovery + M5 resume) |
| Claimed at | 2026-08-23 17:48 local |
| Status | CLAIMED |

## 3. Current Status
🟢 M1–M4 DONE & verified. **M5 IN PROGRESS — deep-processing of all 443 raw
files.** Recovered context (owner confirmed 2026-08-23): an interrupted run
had deep-classified 186/443 files into
`Processed_Assets/file_classification_manifest.json`; **257 files remain**.
Resume Phase 2 batching. Housekeeping done: stale lock removed, crash
checkpoint committed, credentials audit + local git checkpoint next.

## 4. Milestone Log
| Date | Milestone | Status | Notes |
|---|---|---|---|
| 2026-08-15→16 | M1 Vault segregation & cold storage | DONE | 73 sensitive files isolated; 0 deletions in Raw_copies |
| 2026-08-17 | M2 10-domain taxonomy + 46 playbooks | DONE | YAML frontmatter + lineage standardized |
| 2026-08-17→18 | M3 Dashboards + RAG/KG DB + CLI search | DONE | Excel 8-tab, 2 HTML navigators, sub-second BM25 |
| 2026-08-18 | M4 E2E test suite + forensic audit | DONE | see TEST_READY.md |
| 2026-08-18 (crashed) | M5 deep-processing 443 files | PARTIAL | 186/443 deep-classified; run died at ~186 |
| 2026-08-23 | Crash recovery & mission reconstruction | DONE | owner confirmed lost context; resumed M5 |

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
1. **M5 Phase 2 (active):** deep-process remaining 257 files — per-file: nature,
   purpose, reusability, valuable content (business ideas / half-baked projects /
   code snippets / prompts), topic categorization + tags + metadata. Append to
   `file_classification_manifest.json` using the exact schema of the 186 done
   entries. Commit after every ~30-file batch.
2. Credentials audit → authoritative risky list (60 flagged in index + fresh scan);
   keep risky aside via .gitignore; commit safe outputs locally; GitHub only after
   owner provides repo + approves push (recommend Private).
3. Fix anomaly: manifest shows 11 distinct domains vs canonical 10.
4. After M5 processing completes → semantic/vector search layer (owner-chosen).
5. Owner memory anchor (2026-08-23): "go through each and every file, identify
   what it is, categorise it, tag metadata — know exactly what I have and whether
   it is useful for future projects."

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
into vault + 10-domain library (46 playbooks) + FTS5/KG database +
dashboards + tests. Owner is non-technical, decides in natural language.
STATE:   M1–M4 DONE. M5 ACTIVE = deep-processing all 443 files; 186 done in
Processed_Assets/file_classification_manifest.json, 257 remain (run crashed
2026-08-18 mid-batch). Resume batching with identical schema, commit every
~30 files.
NEXT:    finish 257 → credentials audit → local git checkpoint of outputs →
semantic search layer (owner-chosen). GitHub push only with owner approval.
GOTCHAS: free providers/quota drops interrupt runs — small committed
increments only. Never touch Raw_copies/ contents or weaken .gitignore.
Raw_copies contains API-key backups + Aadhaar PDF + bank statements — NEVER
commit them to git/GitHub.
RULES:   read+update this PROJECT_STATE.md, claim 🔒 Active Worker before
work, commit checkpoints, never delete data / spend money / publish without
owner approval.
```
