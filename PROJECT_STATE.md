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
🟢 **M5 DEEP-PROCESSING: COMPLETE.** 443/443 files classified; 96/96 E2E tests
passing (100%). Session delivered: crash recovery → credentials audit (50 raw +
repo-wide scan, placeholder-aware scanner) → live keys redacted from public
tiers (2 GM playbooks + 6 library copies; originals untouched in Raw_copies) →
RAG/KG rebuilt across all tiers (502 docs / 10,785 chunks) → dashboards aligned.
**NEXT:** semantic/vector search layer (owner-chosen M5b); GitHub push pending
owner repo decision — recommend Private; scrub dashboard exports first.

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

## 5.1 M5 Final Statistics (2026-08-23)
- Classification: 251 merge_into_gm · 123 archive · 65 reference_only · 0 pending
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
into vault + 10-domain library (49 playbooks) + FTS5/KG database (502 docs,
10785 chunks) + dashboards + 96-test suite at 100% pass. Owner is
non-technical, decides in natural language.
STATE:   M1-M4 DONE. M5 DONE 2026-08-23: every file deep-classified in
Processed_Assets/file_classification_manifest.json (251 merged, 123 archive,
65 reference, 117 gems scored 8+). Credentials audited; public tiers
sanitized; git protections verified by test suite.
NEXT:    semantic/vector search layer (owner-chosen). GitHub push only after
owner names repo + approves; recommend Private; scrub Excel/HTML dashboard
exports for embedded content first.
GOTCHAS: free providers/quota drops interrupt runs — small committed
increments only (m5_merge_batch.py validator + per-batch commits is the
pattern). Raw_copies/ + vault + RAG DB stay out of git. Live keys exist in
key.txt, my_api_keys_backup.md, test.env.txt, google oauth json — rotate
before any external sharing.
RULES:   read+update this PROJECT_STATE.md, claim 🔒 Active Worker before
work, commit checkpoints, never delete data / spend money / publish without
owner approval.
```
