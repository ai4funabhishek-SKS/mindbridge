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
| Claimed by | — (opencode finished M8 GK-cleanup session; slot released) |
| Claimed at | 2026-08-25 20:10 → released 20:40 |
| Status | FREE |

## 3. Current Status
🟢 **M8 DATA-DEBT CLEANUP EXECUTED (2026-08-25) — library fully curated.**
The 242-file "General Knowledge" catch-all was individually reviewed
(`GK_242_FILE_REVIEW.csv`, owner decisions stamped in every row) and resolved:
- **164 evicted from search index only** (framework plumbing ~95, dup/clone
  ~29, secrets+PII ~18, logs/boilerplate) — originals untouched in Raw_copies.
- **78 keepers re-shelved** into proper homes incl. new labels
  `04_Prompt_Engineering_quick_prompts` (15), `03_RnD_Incubator_Business_Ideas`
  (8, owner's business-gold), `05_Reference_Documentation_tool_configs` (39).
- Owner rescued 2: KNOWLEDGE.md (KB operating manual) + Oracle lab reference;
  evicted the other 4 REVIEW files.
- Live DB now: **338 docs / 10,075 chunks**, all tables aligned, KG intact,
  VACUUMed; anchors rebuilt 338/338; folder indexes + master CSV + dashboards +
  navigator all regenerated.
- v1 surgery over-deleted 11 same-named docs → restored from cold-storage
  backup, re-ran topic-scoped (v2). Lesson baked into L1 skill (P2.5 hygiene
  gate + bulk-mutation safety rules).
- Two tests fixed: hardcoded ">400 anchors" thresholds replaced with
  relative invariants (anchors == live document count).
**Test suite: 181 passed / 0 failed / 0 skipped.**
Spot-proof: crypto-sentiment prompts now rank #1; key-material unfindable;
fw-junk unfindable.
Earlier milestones still in force: Ask mode default = Groq cloud brain
`openai/gpt-oss-120b` (User-Agent header required; 429 auto-retry); security
audit of push set PASSED (548 files, 0 keys). Open items: GitHub push to
KBmomentum-2Braininprocess awaiting owner GO; key rotation pre-public;
Task-7 review actioning; legacy friendly-vs-numbered topic names may be
normalized someday (cosmetic).

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
| 2026-08-25 | M6e ask mode + briefings + model ladder | CODE DONE | live proof blocked by RAM |
| 2026-08-25 | M6f Groq cloud brain (gpt-oss-120b) default | DONE | 181/181 green; live E2E proven |
| 2026-08-25 | M7 docs layer: onboarding, journey/business plan, L1 skill, exclusions, security audit PASS | DONE | push set clean: 548 files, 0 key hits |
| 2026-08-25 | M8 GK catch-all cleanup: 164 evicted / 78 re-shelved; DB rebuilt; L1 skill hardened with hygiene gate + surgery rules | DONE | 181/181 green; backup kept in cold storage |

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
| 2026-08-25 | Ask brain → Groq free tier by default (owner Option A); local kept as `--model` fallback | RAM ceiling (.wslconfig=4GB) made local llama3.2 permanently borderline; cloud = smarter + zero RAM | B: qwen3.5-2b local swap; C: hybrid auto-ladder (revisit if privacy needs demand) |

## 7. Next Steps & Open Questions
1. ~~M5 Phase 2 (active): deep-process remaining 257 files~~ DONE (see M5 log).
2. GitHub push only after owner provides repo + approves; recommend Private;
   scrub dashboard exports first; rotate live keys before any external sharing.
3. ~~M6 finish line: free RAM → live Ask E2E~~ DONE via cloud brain (M6f).
4. Task-7 brutal review: report exists, actioning still open.
5. ~~Data debt: 242 docs under "General Knowledge"~~ DONE (M8): 164 evicted
   from index, 78 re-shelved; review record in GK_242_FILE_REVIEW.csv.
6. Optional cosmetic pass: merge legacy friendly topic names
   ("AI & Automation") with numbered-domain equivalents someday.

## 8. Blockers & Gotchas
- Antigravity quota exhaustion repeatedly interrupted work (resets daily).
- Free LLM providers via OmniRoute can drop connections mid-run ("Cannot connect"); sessions survive — always resume via PROJECT_STATE.md, never restart from scratch.
- `.gitignore` protects vault/credentials — never weaken it.
- Groq behind Cloudflare: requests WITHOUT a real User-Agent header get
  error-1010 blocked at the edge (looks like auth failure but isn't).
- Groq free tier TPM ≈ 8k/min on gpt-oss-120b: bursts of Ask queries need the
  built-in 429 retry (shipped in M6f). RPD = 1,000/day on that model.
- Vault contains FOUR gsk_ keys (all currently valid); `_load_groq_key` takes
  first match (`my_api_keys_backup.md`). If it ever dies, try others manually.

## 9. Environment Map
- Root: `C:\knowledgeBase_staging`
- Search CLI: `python search_engine.py --mode linear|graph "<query>"`
- Key scripts: `Collect-KnowledgeBase.ps1`, `Cleanup-RawCopies.ps1`, `process_gms.py`, `copy_raw_assets_to_domains.py`, `init_rag_and_knowledge_graph.py`, `deep_inspect_and_build_dashboard.py`, `generate_master_dashboard.py`
- Docs: `PROJECT.md` (architecture/contracts), `ORIGINAL_REQUEST.md`, `TEST_READY.md`, `TEST_INFRA.md`
- Secrets: none in repo; real credentials live in `01_Vault_Private/credentials_and_keys/` (gitignored)

## 10. 🔄 Handoff Capsule (paste into any other AI tool)
```
CONTEXT: C:\knowledgeBase_staging — Second Brain KB: 443 raw files refined
into vault + 10-domain library (49 playbooks) + FTS5/KG database (338 docs,
10075 chunks, 338 anchors — post-M8 cleanup) + dashboards + CSV asset
indexes + 181-test suite (ALL GREEN, 0 skips). Onboarding: START_HERE.md.
Exclusion rules: DO_NOT_MOVE_TO_KB.md. Review record: GK_242_FILE_REVIEW.csv.
Business/community: JOURNEY_AND_BUSINESS_PLAN.md. Portable L1 skill:
_handoff/L1_second_brain_refinement/SKILL.md (now incl. P2.5 hygiene gate).
STATE:   M1-M8 DONE 2026-08-25. Ask mode DEFAULT brain = Groq free-tier
`openai/gpt-oss-120b` (key auto-found in vault, never printed; User-Agent
header REQUIRED; 429 auto-retry). Aliases: groq | groq-fast(qwen3.6-27b)
| phi3/llama3.2/mistral = local Ollama w/ RAM ctx-ladder. M8 purged the
General-Knowledge junk drawer: secrets/PII/plumbing unfindable, keepers
re-shelved (business ideas now their own label). Bulk-surgery rules live
in the L1 skill: topic-scoped doc-id deletes, cold-storage DB backup first,
relative test invariants.
NEXT:    Owner GO -> push to Private repo KBmomentum-2Braininprocess; then
key rotation; optional public sanitized mirror per business plan; Task-7
review actioning; someday normalize legacy friendly vs numbered topics.
GOTCHAS: .wslconfig caps WSL VM at 4GB -> no local llama3.2 as primary.
Ollama lives in Docker-in-WSL; needs Docker Desktop after reboot. Groq
model lineup changed vs old notes - query /v1/models, don't trust memory.
Filenames are NOT unique DB keys - scope bulk ops by topic+id lists.
RULES:   read+update PROJECT_STATE.md, claim Active Worker before work,
commit checkpoints, verify-before-done mandate is in global AGENTS.md,
never delete data / spend money / publish without owner approval; vault
never leaves this machine unencrypted.
```
