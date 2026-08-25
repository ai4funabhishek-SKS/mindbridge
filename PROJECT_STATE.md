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
| Claimed by | opencode (session: M5c semantic search command) |
| Claimed at | 2026-08-25 — session complete, claim RELEASED |
| Status | FREE |

## 3. Current Status
🟢 **M5c SEMANTIC SEARCH: COMPLETE (2026-08-25).** `search_engine.py` now has 4
modes: linear (FTS5/BM25), graph (KG), **semantic** (cosine over 10,785
chunk_embeddings via Ollama nomic-embed-text, ~0.2s warm), **hybrid**
(Reciprocal Rank Fusion of both legs). Embedding matrix cached in-process by
DB mtime. Graceful fallback message if Ollama is down. Test suite grown to
**139 tests, 100% pass** (96 e2e + 21 adversarial + 22 semantic/hybrid).
**NEXT:** GitHub push pending owner repo decision (recommend Private; scrub
dashboard exports first); rotate live keys before any external sharing.

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
1. **M5 Phase 2 (active):** deep-process remaining 257 files — per-file: nature,
   purpose, reusability, valuable content (business ideas / half-baked projects /
   code snippets / prompts), topic categorization + tags + metadata. Append to
   `file_classification_manifest.json` using the exact schema of the 186 done
   entries. Commit after every ~30-file batch.
2. Credentials audit → authoritative risky list (60 flagged in index + fresh scan);
   keep risky aside via .gitignore; commit safe outputs locally; GitHub only after
   owner provides repo + approves push (recommend Private).
3. ~~Fix anomaly: manifest shows 11 distinct domains vs canonical 10.~~ RESOLVED
   2026-08-24: ARCHIVE is the routing bucket for cold storage (by design); 42
   mismatched action↔domain entries aligned; pre-fix backup at
   `_trash_manifest_backup_2026-08-24.json`.
4. ~~After M5 processing completes → semantic/vector search layer (owner-chosen).~~ DONE
   2026-08-25: `--mode semantic` + `--mode hybrid` (RRF) shipped. Honest quality
   note: natural-language queries work well; one weak spot found — vague queries
   like "find clients for finance advisory" rank CVs above the subbroking
   playbook (embedding-level limitation; domain-specific phrasing fixes it).
   Future option: embed title+summary alongside chunks for stronger anchors.
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
into vault + 10-domain library (49 playbooks) + FTS5/KG database (502 docs,
10785 chunks) + dashboards + 139-test suite at 100% pass. Owner is
non-technical, decides in natural language.
STATE:   M1-M5 DONE. M5b semantic index DONE (10785/10785, nomic 768d).
M5c search layer DONE 2026-08-25: search_engine.py has 4 modes — linear
(FTS5), graph (KG), semantic (cosine over chunk_embeddings, ~0.2s warm),
hybrid (RRF fusion, k=60). Ollama-down = friendly fallback message.
Credentials audited; public tiers sanitized; 139/139 tests pass.
NEXT:    GitHub push only after owner names repo + approves; recommend Private;
scrub Excel/HTML dashboard exports for embedded content first; rotate live
keys before any external sharing. Optional quality upgrade: embed title+
summary anchors for better vague-query hits.
GOTCHAS: free providers/quota drops interrupt runs — small committed
increments only. Raw_copies/ + vault + RAG DB stay out of git. Live keys exist
in key.txt, my_api_keys_backup.md, test.env.txt, google oauth json — rotate
before any external sharing. Semantic mode needs local Ollama running.
RULES:   read+update this PROJECT_STATE.md, claim 🔒 Active Worker before
work, commit checkpoints, never delete data / spend money / publish without
owner approval.
```
