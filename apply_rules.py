"""Regenerate .gitignore generated block from current audit + restage."""
import json
import subprocess
from pathlib import Path

ROOT = Path(r"C:\knowledgeBase_staging")
report = json.loads((ROOT / "Processed_Assets/credential_audit.json").read_text(encoding="utf-8"))
SELF = {"audit_credentials.py", "audit_repo_wide.py", "apply_protections.py",
        "redact_gm_secrets.py", "Processed_Assets/credential_audit.json",
        "Processed_Assets/_gitignore_generated_rules.txt"}
risky = sorted({d["path"] for d in report["repo_wide_scan"]["details"]} - SELF)
gm = [p for p in risky if p.startswith("03_Topics")]
print("GM still flagged:", gm)

block = ["", "# ---- M5 Phase 1b: credential/PII copies outside Raw_copies (generated) ----",
         "# Source: Processed_Assets/credential_audit.json. Files stay on disk, never in git."]
block += [f"/{p}" for p in risky]
block += ["# RAG DB embeds raw text (incl. secret-bearing chunks) in its search index.",
          "# Regenerable via init_rag_and_knowledge_graph.py - never publish without scrubbing.",
          "/Processed_Assets/my_rag_data.db"]

gi = ROOT / ".gitignore"
old = gi.read_text(encoding="utf-8")
marker = "# ---- M5 Phase 1b"
base = old.split(marker)[0].rstrip("\n") if marker in old else old.rstrip("\n")
gi.write_text(base + "\n" + "\n".join(block) + "\n", encoding="utf-8", newline="\n")
print("rules applied:", len(risky))
