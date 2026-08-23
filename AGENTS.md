# Project Rules — Second Brain Knowledge Base

Shared by ALL AI tools working in this folder (opencode, Kilo Code,
Antigravity, Claude Code, …).

## Coordination (mandatory)
1. Read `PROJECT_STATE.md` FIRST. It is the single source of truth.
2. Before any work: check 🔒 Active Worker. If another tool claimed it in the
   last 30 minutes → STOP and report to the owner instead of starting.
3. When you start: write your tool name + timestamp into Active Worker.
   Release/clear it when you pause or finish.
4. Run `git status` before editing. Uncommitted changes you did not make →
   report to owner first.
5. Commit checkpoints after every completed step
   (`feat:` / `fix:` / `docs:` style messages).

## Hard constraints
- NEVER modify anything inside `Raw_copies/` (immutable originals, 443 files).
- NEVER weaken `.gitignore`; `01_Vault_Private/` must stay out of git.
- No irreversible deletions — use `_trash_<date>/` instead.
- No spending, publishing, or external communication without owner approval.
- No secrets/keys in code, docs, or commits — reference vault paths only.

## Conventions
- Update PROJECT_STATE.md after every milestone, decision, or blocker.
- Keep the 🔄 Handoff Capsule current so work can move between tools anytime.
- Python scripts at root are the build pipeline; dashboards live in
  `00_Index_and_Dashboards/`.
