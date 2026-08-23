#!/usr/bin/env python3
"""Step 1c: verdict every flagged key-looking string in git-visible files.

For each match: is it (a) a REAL secret that exists in the vault inventory,
or (b) an example/placeholder/document fragment? Real ones get redacted in
place with a marker; originals remain in Raw_copies (non-destructive rule).
"""
import json
import os
import re
import sys

ROOT = "."
INV = json.load(open("01_Vault_Private/_credentials_inventory.json", encoding="utf-8"))
real_values = set()
for grp in ("labeled", "bare"):
    for items in INV.get(grp, {}).values():
        for it in items:
            real_values.add(it["value"])
# authoritative source: every backticked value recorded in the master registry
REG_TEXT = open("01_Vault_Private/MASTER_CREDENTIALS_REGISTRY.md", encoding="utf-8").read()
# authoritative source: ONLY the Value column of registry tables (row shape
# "| account | `value` | sources | notes |"), never prose/backticked filenames.
BENIGN_HINTS = ("/", ".md", ".txt", ".json", ".xlsx", ".py", ".ps1", "http", " ")
real_values = {
    v.strip() for v in re.findall(r"^\|.*?\|\s*`([^`\n]+)`\s*\|", REG_TEXT, re.M)
    if len(v.strip()) >= 12 and not any(h in v for h in BENIGN_HINTS)
}
real_values.update(
    v for grp in () for v in []  # placeholder no-op keeps set type explicit
)
for v in re.findall(r"`(GOCSPX-[A-Za-z0-9\-_]+)`", REG_TEXT):
    real_values.add(v)
real_literals = sorted((v for v in real_values if len(v) >= 12), key=len, reverse=True)

PATTERNS = {
    "openai_sk": re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    "gsk_groq": re.compile(r"gsk_[A-Za-z0-9]{20,}"),
    "google_api": re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),
    "tavily": re.compile(r"tvly-[A-Za-z0-9\-_]{15,}"),
    "hf": re.compile(r"hf_[A-Za-z0-9]{30,}"),
    "bearer_long": re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.]{35,}"),
}
SKIP_DIRS = {".git", "__pycache__", "node_modules", "Raw_copies", "01_Vault_Private"}
PLACEHOLDER_HINTS = ["PLACEHOLDER", "REDACTED", "YOUR_", "XXXX", "EXAMPLE", "<", "{", "}"]


def mask(v):
    return v[:8] + "***" + v[-4:] if len(v) > 16 else v[:4] + "***"


def main(redact=False):
    actions = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if not f.lower().endswith((".md", ".txt", ".json", ".py", ".ps1", ".yaml", ".yml", ".html", ".csv")):
                continue
            p = os.path.join(dp, f).replace(".\\", "")
            try:
                t = open(p, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            orig = t
            file_hits = []
            for name, rx in PATTERNS.items():
                for mt in rx.finditer(t):
                    s = mt.group(0)
                    probe = s.replace("Bearer ", "").replace("bearer ", "")
                    is_real = probe in real_values or s in real_values
                    is_ph = any(h.upper() in s.upper() for h in PLACEHOLDER_HINTS)
                    verdict = "REAL-KEY" if is_real else ("placeholder-ish" if is_ph else "example/doc-fragment")
                    ctx = t[max(0, mt.start() - 60):mt.end() + 20].replace("\n", " ")[:90]
                    file_hits.append((name, mask(s), verdict, ctx))
                    if redact and is_real:
                        t = t.replace(s, "[[REDACTED-REAL-KEY-2026-08-23]]")
            if file_hits:
                print(f"\n### {p}")
                for name, m, verdict, ctx in file_hits:
                    print(f"  [{verdict:^18}] {name:11} {m}")
                    print(f"      ctx: ...{ctx}...")
            # literal pass: any known real value, any format
            lit_found = [v for v in real_literals if v in t]
            for v in lit_found:
                print(f"  [{'LITERAL-KEY':^18}] {'registry-value':11} {mask(v)}")
                if redact:
                    t = t.replace(v, "[[REDACTED-REAL-KEY-2026-08-23]]")
            if redact and t != orig:
                open(p, "w", encoding="utf-8").write(t)
                actions.append(p)
                print("  -> REDACTED real keys in this file")
    print("\n==== SUMMARY ====")
    print(f"files modified during redaction pass: {len(actions)}")
    for a in actions:
        print("  ", a)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(redact="--redact" in sys.argv)
