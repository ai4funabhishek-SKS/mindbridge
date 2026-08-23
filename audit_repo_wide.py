"""
M5 Phase 1b — REPO-WIDE credentials scan (everything except Raw_copies/,
01_Vault_Private/, .git). Updates Processed_Assets/credential_audit.json with
a repo_risky section and emits generated .gitignore rules to stdout file.
Read-only scan.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
OUT = ROOT / "Processed_Assets" / "credential_audit.json"
RULES_OUT = ROOT / "Processed_Assets" / "_gitignore_generated_rules.txt"

SKIP_DIRS = {".git", "Raw_copies", "01_Vault_Private"}
TEXT_EXTS = {".md", ".json", ".txt", ".csv", ".py", ".html", ".xml", ".yml", ".yaml"}
MAX_SCAN_BYTES = 2_000_000

CONTENT_PATTERNS = {
    "openai_key": r"\bsk-[A-Za-z0-9_\-]{20,}",
    "github_token": r"\bgh[pousr]_[A-Za-z0-9]{20,}",
    "aws_access_key": r"\bAKIA[0-9A-Z]{16}\b",
    "slack_token": r"\bxox[baprs]-[A-Za-z0-9\-]{10,}",
    "google_api_key": r"\bAIza[0-9A-Za-z_\-]{30,}",
    "private_key_block": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "jwt": r"\beyJ[A-Za-z0-9_\-]{15,}\.[A-Za-z0-9_\-]{10,}",
    "telegram_bot": r"\b\d{8,10}:AA[A-Za-z0-9_\-]{30,}",
    "twilio_sid": r"\bAC[a-f0-9]{32}\b",
    "db_uri_with_pass": r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^\s:/@]+:[^\s/@]+@",
    "generic_secret_assignment": r"""(?i)(?:api[_-]?key|apikey|secret|access[_-]?token|auth[_-]?token|client[_-]?secret|passwd|password|pwd)\b\s*[:=]\s*["']?[^\s"']{8,}""",
    "bearer_token": r"(?i)\bbearer\s+[A-Za-z0-9_\-\.=]{20,}",
}

FILENAME_RULES = [
    (r"(?i)aadha[r]|adhar|\bpan[-_. ]?(card|no)\b|passport|kyc|voter", "identity_document"),
    (r"(?i)(account|bank|acct)[-_ ]?(statement)?|\bstatement\b|capital[ _-]?gains|holdings?\b|salary|form[- _]?16", "financial_statement"),
    (r"(?i)\bcv\b|curriculum[_ -]?vitae|\bresume\b", "personal_cv"),
    (r"(?i)secret|credential|api[_ -]?keys?|tokens?|\.env", "credentials_by_name"),
]


def main():
    risky = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        parts = set(rel.parts)
        if parts & SKIP_DIRS:
            continue
        reasons = []
        for pattern, cat in FILENAME_RULES:
            if re.search(pattern, p.name):
                reasons.append(cat)
        if p.suffix.lower() in TEXT_EXTS:
            try:
                if p.stat().st_size <= MAX_SCAN_BYTES:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    reasons += [f"content:{m}" for m in CONTENT_PATTERNS
                                if re.search(CONTENT_PATTERNS[m], text)]
            except OSError:
                pass
        if reasons:
            risky.append({"path": rel.as_posix(), "reasons": sorted(set(reasons))})

    prev = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    report = {
        "raw_tier_scan": {k: v for k, v in prev.items() if k != "repo_wide_scan"},
        "repo_wide_scan": {
            "risky_files": len(risky),
            "details": risky,
        },
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "",
        "# ---- M5 Phase 1b: generated protections (credential/PII copies outside Raw_copies) ----",
        "# Auto-generated from Processed_Assets/credential_audit.json — do not hand-edit below this marker.",
    ]
    for item in risky:
        lines.append(f"/{item['path']}")
    RULES_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Repo-wide risky files: {len(risky)}")
    from collections import Counter
    cats = Counter(r.split(':', 1)[0] for i in risky for r in i['reasons'])
    for c, n in cats.most_common():
        print(f"  {c:<22} {n}")
    print(f"Ignore rules written: {RULES_OUT}")


if __name__ == "__main__":
    main()
