# SKILL: second-brain-refinement

> **Portable skill for a fresh laptop.** Copy this whole folder to
> `%USERPROFILE%\.config\opencode\skills\second-brain-refinement\SKILL.md`
> on the target machine. The AI there can then execute the entire pipeline.
>
> Proven on: 16GB Windows laptop, 443 files, $0 infra, 181/181 tests green.
> Designed to also work on 8GB machines (cloud-brain-first is MANDATORY there).

## Mission

Refine a folder of scattered personal/professional files into a **private,
searchable Second Brain**: vault + domain library + Golden-Master playbooks +
dashboards + hybrid search + cited Ask mode + self-verifying test suite —
**without ever deleting or moving originals**.

## Non-Negotiable Rules (read before ANY action)

1. **COPY, never move/delete.** Originals live untouched in `Raw_copies/`.
2. Secrets (keys/passwords/ID docs/bank records) → `01_Vault_Private/`,
   registered in `MASTER_CREDENTIALS_REGISTRY.md`, gitignored from minute one.
3. Maintain `PROJECT_STATE.md` (diary): claim 🔒 Active Worker, update after
   every milestone, keep a Handoff Capsule. Sessions WILL die; the diary is law.
4. Commit checkpoints constantly. Never trust "it worked" — VERIFY with
   commands and quote real output before claiming done.
5. Respect `DO_NOT_MOVE_TO_KB.md` categories (locks, zero-byte, dups,
   vendor dumps, >20MB media stay out of the curated library).
6. Owner is non-technical: decisions in plain language, Option A/B format.

## Hardware Reality Check (do this FIRST)

```
- Read .wslconfig if present; note WSL memory cap.
- RAM <12GB  → LOCAL LLM IS FORBIDDEN as primary brain. Use cloud API brain
              (Groq free tier) for all synthesis. Local Ollama optional and
              never load-bearing. Embeddings model (nomic-embed-text) is tiny
              and stays local fine even on 4GB VMs.
- RAM >=16GB → local fallback allowed via context-shrink ladder.
- Cloudflare-protected APIs REQUIRE a real User-Agent header (e.g.
  'SecondBrainKB/1.0') — bare urllib/python-requests gets error-1010.
- Groq model lineup changes: ALWAYS GET /openai/v1/models with the key and
  pick current IDs; never hardcode retired names (llama-70b retired 2026).
- Free-tier TPM ≈ 8k/min: implement 429 retry honoring Retry-After.
```

## Pipeline Phases (execute in order; commit after each)

### P0 — Inventory & Diary
Scan source folder: count files by type/size, flag zero-byte/dups/lock files,
grep for key patterns (`sk-`, `gsk_`, `AIza`, `tvly-`, `hf_`, `AKIA`, private
key blocks). Write PROJECT_STATE.md + this inventory. Set up `.gitignore`
(vault/, Raw_copies/, db, env/key/secret patterns, Briefings/, logs).

### P1 — Vault & Cold Storage
Create vault subfolders (credentials_and_keys, financial_statements,
personal_identity). COPY sensitive finds in; register keys. Quarantine junk
to `04_Archive_Cold_Storage/{zero_byte_files,temporary_lock_files,duplicate_stubs}`.
Acceptance: originals intact, vault populated, gitignore proven via `git status`.

### P2 — Taxonomy & Playbooks
10 domains under `02_Assets_Library/` + `03_Topics_and_Projects/`.
Cluster overlapping material per domain → ONE Golden-Master `.md` per cluster:
YAML frontmatter (title/domain/reusability_score/workability_status/tags/
dependencies/source_files_synthesized) + explicit lineage & merge rationale +
mental models + clean code/n8n JSON blocks + deployment SOPs.
Target density over volume (443 files → ~49 playbooks is healthy).

### P3 — Database, Dashboards, Search Engine
SQLite DB (`Processed_Assets/my_rag_data.db`): documents/chunks/chunks_fts
(FTS5/BM25)/kg_nodes/kg_edges. Build Excel dashboard + interactive HTML
navigator + KG explorer. Ship CLI search engine: linear → graph modes.
Acceptance: BM25 queries sub-second; dashboard opens cleanly.

### P4 — Semantic Layer
Embed chunks + document-level anchor fingerprints locally (nomic-embed-text;
crash-safe batched runner with resume). Add semantic mode (cosine) + hybrid
mode (Reciprocal Rank Fusion) + per-doc diversity cap (MAX_PER_DOC=2).
Anchor rank-fusion fixes vague business queries — verify with one real
acceptance query that previously failed.

### P5 — Smart Indexes & Filters
Per-folder CSV indexes + MASTER_ASSET_INDEX.csv (13 cols incl. gem flags,
related_files). Add `--topic/--topics/--gems` filters across all modes.

### P6 — Ask Mode (cloud brain default)
Funnel retrieval (BM25 + anchor-fused semantic, RRF) → LLM synthesis with
mandatory `[S#]` citations and cite-or-refuse instruction. `--save` writes
Obsidian-style briefs. Key discovery: env var → scan vault for provider key
pattern (never print it). Model ladder: cloud default → smaller cloud →
local phi3 (only if RAM allows). Add ANSWER/SOURCES banners to output.

### P7 — Test Suite & Docs
Pytest suite covering every acceptance criterion + adversarial cases
(malformed YAML, FTS5 meta-chars, empty queries, unicode). Target: ALL tests
green including live E2E. Write START_HERE.md (building-metaphor onboarding),
DO_NOT_MOVE_TO_KB.md, README pitch, Handoff Capsule update.

## Known Failure Modes → Fast Fixes

| Symptom | Root cause | Fix |
|---|---|---|
| HTTP 403 err-1010 to Groq/OpenAI-compatible APIs | Cloudflare bot block | Add User-Agent header |
| "model requires more system memory" | WSL VM cap / small RAM | Shrink num_ctx ladder 4096→2048→1024, else switch to cloud brain |
| Tests skip mysteriously | Gate checks only one path | Gate should try cloud THEN local rungs |
| Embedding run dies mid-way | Session/quota loss | Batched resume-safe writer keyed on chunk_id |
| Search returns CVs/SEBI PDFs for vague queries | Pure similarity ranking | Anchor fingerprints + per-doc cap |
| Same doc floods results | No diversity control | MAX_PER_DOC=2 walk |
| 429 bursts | TPM caps | Retry-once honoring Retry-After |

## Final Verification Ritual (before telling owner "done")

1. Re-run full test suite; quote exact pass/fail/skip numbers.
2. Confirm every produced file exists and is non-zero size.
3. Run one real Ask query end-to-end; show the cited answer.
4. `git log --oneline` shows clean checkpoints; `git status` has no strays.
5. Update PROJECT_STATE.md + Handoff Capsule; release worker claim.
