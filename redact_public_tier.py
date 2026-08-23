"""Redact real credential patterns in PUBLIC tiers (02_Assets_Library, 03_Topics,
00_Index) so no public file requires a gitignore exemption. Raw_copies and
cold-storage quarantine are intentionally left untouched."""
import json
import re
from pathlib import Path

ROOT = Path(r"C:\knowledgeBase_staging")
PUBLIC_PREFIXES = ("02_Assets_Library/", "03_Topics_and_Projects/", "00_Index_and_Dashboards/")
SELF = {"audit_credentials.py", "audit_repo_wide.py", "apply_protections.py",
        "apply_rules.py", "redact_gm_secrets.py"}

report = json.loads((ROOT / "Processed_Assets/credential_audit.json").read_text(encoding="utf-8"))
details = report["repo_wide_scan"]["details"]

SUBS = [
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}"), "sk-[REDACTED]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "ghp_[REDACTED]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AKIA[REDACTED]"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}"), "xox[REDACTED]"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}"), "AIza[REDACTED]"),
    (re.compile(r"tvly-dev-[A-Za-z0-9_\-]{15,}"), "tvly-dev-[REDACTED]"),
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9_\-\.=]{20,}"), "Bearer [REDACTED]"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
     "[REDACTED PRIVATE KEY BLOCK]"),
]

changed = []
for d in details:
    rel = d["path"]
    if not rel.startswith(PUBLIC_PREFIXES) or Path(rel).name in SELF:
        continue
    p = ROOT / rel
    if p.suffix.lower() not in {".md", ".json", ".txt", ".csv", ".py", ".html"}:
        continue
    t = p.read_text(encoding="utf-8", errors="ignore")
    orig = t
    for pat, repl in SUBS:
        t = pat.sub(repl, t)
    if t != orig:
        p.write_text(t, encoding="utf-8", newline="\n")
        changed.append(rel)

print("redacted files:", len(changed))
for c in changed:
    print("  ", c)
