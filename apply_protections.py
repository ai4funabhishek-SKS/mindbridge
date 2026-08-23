"""One-shot Phase 1 finisher:
1. Load the 26 generated rules, drop self/tool false-positives.
2. Append clean LF-ending block to .gitignore (+ RAG DB exclusion).
3. Untrack (git rm --cached) any listed file still in the index.
4. Report final state.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(r"C:\knowledgeBase_staging")
AUDIT = ROOT / "Processed_Assets" / "credential_audit.json"
GI = ROOT / ".gitignore"

SELF_TOOL_FALSE_POSITIVES = {
    "audit_credentials.py",
    "audit_repo_wide.py",
    "Processed_Assets/credential_audit.json",
    "Processed_Assets/_gitignore_generated_rules.txt",
}

report = json.loads(AUDIT.read_text(encoding="utf-8"))
details = report["repo_wide_scan"]["details"]
risky_paths = sorted({d["path"] for d in details} - SELF_TOOL_FALSE_POSITIVES)

block = [
    "",
    "# ---- M5 Phase 1b: credential/PII copies outside Raw_copies (generated) ----",
    "# Source: Processed_Assets/credential_audit.json. Files stay on disk, never in git.",
]
for p in risky_paths:
    block.append(f"/{p}")
block += [
    "# RAG DB embeds raw text (incl. secret-bearing chunks) in its search index.",
    "# Regenerable via init_rag_and_knowledge_graph.py - never publish without scrubbing.",
    "/Processed_Assets/my_rag_data.db",
]

old = GI.read_text(encoding="utf-8")
marker = "# ---- M5 Phase 1b"
base = old.split(marker)[0].rstrip("\n") if marker in old else old.rstrip("\n")
GI.write_text(base + "\n" + "\n".join(block) + "\n", encoding="utf-8", newline="\n")

indexed = subprocess.run(
    ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True
).stdout.splitlines()
tracked_risky = [p for p in risky_paths + ["Processed_Assets/my_rag_data.db"] if p in set(indexed)]

for p in tracked_risky:
    subprocess.run(["git", "rm", "--cached", "--quiet", p], cwd=ROOT, check=True)

print("rules kept:", len(risky_paths))
print("untracked from index:", len(tracked_risky))
for p in tracked_risky:
    print("  rm --cached:", p)
