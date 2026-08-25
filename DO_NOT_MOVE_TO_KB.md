# 🚫 DO NOT MOVE TO KNOWLEDGE BASE — Exclusion List

> **Purpose:** This is the official "keep out" list for the Second Brain.
> Any AI tool or human tidying files on any laptop must follow it BEFORE
> moving anything into `02_Assets_Library/` or `03_Topics_and_Projects/`.
>
> **Golden rule (never broken in this project):** we COPY, never move or
> delete originals. Originals stay untouched in `Raw_copies/`.

Born from hard lessons between 2026-08-15 and 2026-08-25. Each rule below
was violated by real files found on this laptop.

---

## 1. 🔑 Secrets & Credentials — NEVER into the KB (vault only)

| Keep out | Why | Where it goes instead |
|---|---|---|
| API keys / tokens (`sk-…`, `gsk_…`, `tvly-…`, `nvapi-…`, `hf_…`, `ghp_…`, Google `AIza…`, OAuth client-secret JSON) | Live keys = money & identity risk; KB text gets indexed, searched, embedded | `01_Vault_Private/credentials_and_keys/` — and record the find in `01_Vault_Private/MASTER_CREDENTIALS_REGISTRY.md` |
| `.env`, `*.env.txt`, `key.txt`, files with `secret`/`credential` in the name | Same as above | Vault |
| Passwords inside n8n workflow JSON exports | Workflows often embed credentials in node parameters | Vault; a SCRUBBED copy may enter KB |
| Bank statements, fee receipts, tax/capital-gain sheets | Financial PII | `01_Vault_Private/financial_statements/` |
| Aadhaar/ID scans, CVs/resumes, personal applications | Identity PII | `01_Vault_Private/personal_identity/` |
| Anything from `01_Vault_Private/` itself | Vault stays vault; never re-circulate | Nowhere |

## 2. 🗑️ Junk & Machine Noise — cold storage or ignore

| Keep out | Why | Where it goes instead |
|---|---|---|
| Office lock files (`~$*.docx`, `.~lock.*#`) | Meaningless machine temp data | `04_Archive_Cold_Storage/temporary_lock_files/` |
| Zero-byte files | Empty shells; pollute indexes | `04_Archive_Cold_Storage/zero_byte_files/` |
| `*.tmp *.temp *.bak *.old *.wbk *.dmp *.log *.err` | Run debris, not knowledge | Cold storage / leave gitignored |
| `_trash_*` backups, crash manifests | Recovery artifacts | Stay at root, gitignored |
| `Thumbs.db`, `Desktop.ini`, `$RECYCLE.BIN` | OS metadata | Ignore entirely |

## 3. 👯 Duplicates — keep ONE canonical copy

| Keep out | Why | Where it goes instead |
|---|---|---|
| `name (1).ext`, `name (2).ext`, `copy of …`, `dup_*` | We found dozens (`screener (1).json`, `dup_screener`, resume ×3…) | Best original stays; rest → `04_Archive_Cold_Storage/duplicate_stubs/` with manifest note |

## 4. 💾 Bulk & Binary Bloat — curate before entering

| Keep out | Why | Where it goes instead |
|---|---|---|
| Raw video/audio/images over ~20 MB each unless core knowledge | Bloats search index and any future Git repo | Stay in `Raw_copies/`; link from a playbook instead |
| App installers, ZIP bombs, dataset dumps | Not knowledge, pure weight | Cold storage |
| Browser profiles, app caches, `node_modules`, `__pycache__` | Machine state, not your mind | Ignore entirely |

## 5. 🧩 Boilerplate & Unmodified Third-Party Material

| Keep out | Why | Where it goes instead |
|---|---|---|
| Untouched vendor docs dumps (e.g., whole `n8n-docs-main` tree) | Public info; huge; belongs online, not in private KB | Reference the source URL in a playbook; optionally park in cold storage |
| Generic uncustomized templates never used | Clutter the taxonomy | Cold storage |

## 6. 🤖 Generated Artifacts — regenerable, don't hand-file them

| Keep out | Why | Where it goes instead |
|---|---|---|
| Regenerated dashboards/indexes (Excel/HTML/CSV under `00_`) | Rebuilt by scripts | They live in `00_Index_and_Dashboards/`; never copy elsewhere by hand |
| `my_rag_data.db`, embeddings, digests, manifests under `Processed_Assets/` | Script outputs | Stay put; regenerate via builders |
| AI briefings (`Briefings/*.md`) | Personal notes layer | Stay in `Briefings/`, gitignored |

---

## Quick decision flow (for humans AND AI tools)

```
Found a file. Ask in order:
1. Does it contain keys/passwords/money/ID?      → VAULT (+ registry entry)
2. Is it empty / lock / tmp / log / err?         → COLD STORAGE or ignore
3. Is it an exact duplicate?                     → best copy kept, rest COLD
4. Is it >20 MB media or vendor doc dump?        → stay in RAW_COPIES, link it
5. Is it real knowledge I wrote/curated?         → 02_/03_ + manifest entry
6. Unsure?                                       → leave in place, ask the owner
NEVER delete. NEVER move originals out of Raw_copies/.
```

*Last updated: 2026-08-25 · Owner-approved rules from PROJECT_STATE.md Decisions Log.*
