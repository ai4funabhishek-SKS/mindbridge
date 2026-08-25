# 🧠 START HERE — Your Second Brain in 5 Minutes

> **If you remember only one thing:** this folder is a *library building*
> built from 443 of your real files. Nothing original was ever deleted.
> Everything else below is just knowing which floor to walk to.

---

## 🏢 The Building Map (memorize these 6 floors)

| Floor | Folder | Plain-language meaning |
|---|---|---|
| 🏛️ Front Desk | `00_Index_and_Dashboards/` | Excel dashboard, interactive navigator, master index CSV. *Start browsing here.* |
| 🔐 Safe Deposit | `01_Vault_Private/` | Bank statements, IDs, keys, passwords. **NEVER leaves this laptop. Never goes online.** |
| 📚 Library Shelves | `02_Assets_Library/` | Your 156 curated assets sorted into 10 domains |
| 🛠️ Workshop | `03_Topics_and_Projects/` | The gold: **49 Golden-Master playbooks** — many messy files merged into one great guide each |
| 📦 Attic | `04_Archive_Cold_Storage/` | Junk we quarantined instead of deleting (locks, empties, duplicates) |
| 🗄️ Basement Sealed Boxes | `Raw_copies/` | All 443 ORIGINALS, untouched forever. If anything ever breaks, truth lives here |

Plus two engine rooms you never touch by hand:
`Processed_Assets/` (the searchable database) and `Briefings/` (answers the
AI wrote for you, saved as notes).

**Golden rule of the house:** COPY, never delete. When unsure, ask the owner.

---

## 💬 Ask Your Brain Anything (the magic door)

Open a terminal in this folder and type:

```
python search_engine.py "your question here" --mode ask
```

You get an answer **built from YOUR documents with [S#] citations**, plus a
source list. Add `--save` to keep it as a note in `Briefings/`.

Useful dials:
```
--topic subbroking        # only read from one domain
--gems                    # only use your 8+/10 rated best material
--save                    # write the answer to Briefings/
--model phi3              # offline/private mode (no internet used)
```
The default brain is a free cloud model (`gpt-oss-120b` via Groq) — smart,
fast, costs nothing. Document excerpts travel to Groq for the answer step;
searching stays fully local.

## 🔍 Four more ways to look things up

```
python search_engine.py "camarilla"                      # keyword search
python search_engine.py "n8n" --mode semantic            # meaning-based search
python search_engine.py "n8n" --mode hybrid              # both combined (best)
python search_engine.py "ollama" --mode graph            # how things connect
python search_engine.py --topics                         # list all domains
```

## 👀 Prefer clicking to typing?

- Double-click `00_Index_and_Dashboards\Interactive_Knowledge_Mine_Navigator.html`
- Or open `Master_Second_Brain_Knowledge_Mine.xlsx` — every asset, filterable

---

## 🤝 For visiting AI tools (Claude, Kilo, Antigravity, future opencode…)

1. Read `PROJECT_STATE.md` FIRST — especially section 10, the **Handoff
   Capsule** (paste it into your own context and you are fully briefed).
2. Claim the 🔒 Active Worker slot before working; release it when done.
3. Obey `DO_NOT_MOVE_TO_KB.md` before touching any file layout.
4. Tests are law: run `python -m pytest tests/ -q` after changes.
   Current known-good state: **181 passed / 0 failed / 0 skipped**.
5. Never weaken `.gitignore`; never print or copy anything from
   `01_Vault_Private/`.

## 👤 For the human owner (cheat card)

| I want to… | Do this |
|---|---|
| Find that thing I half-remember | Ask mode (command above) |
| See everything I own | Front Desk HTML or Excel |
| Save an answer for later | add `--save` |
| Keep something private forever | put it in `01_Vault_Private/` |
| Continue where a previous session died | open `PROJECT_STATE.md`, read top-to-bottom |
| Back all this up safely | GitHub (code/playbooks) + Drive (raw bulk) — vault NEVER syncs |

*Created 2026-08-25 · Maintained in PROJECT_STATE.md · Verified by 181 automated tests.*
