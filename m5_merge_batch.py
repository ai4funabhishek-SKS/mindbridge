"""
M5 Phase 2 — Batch merger. Validates a batch JSON against the schema and
atomically merges entries into the master manifest. Usage:
    python m5_merge_batch.py Processed_Assets/m5_batches/batch_01.json
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
MANIFEST = ROOT / "Processed_Assets" / "file_classification_manifest.json"
QUEUE = ROOT / "Processed_Assets" / "m5_remaining_queue.json"

DOMAINS = {
    "01_AI_Agents_and_Autonomous_Systems",
    "02_Workflow_Automations_n8n",
    "03_Prompt_Engineering_and_Frameworks",
    "04_Mobile_and_Android_Ecosystem",
    "05_Code_Snippets_and_Dev_Tools",
    "06_Quantitative_Finance_and_Trading",
    "07_Content_Creation_and_Media_Engines",
    "08_Business_Operations_and_Subbroking",
    "09_LLM_Conversations_and_Syntheses",
    "10_R_and_D_Incubator_Half_Baked_Ideas",
    "ARCHIVE",
}
ACTIONS = {"merge_into_existing_gm", "archive", "reference_only", "new_gm_needed"}
REQUIRED = {"raw_path", "domain", "file_type", "content_summary",
            "reusability_score", "action", "target_gm", "rationale"}


def main(batch_file):
    batch = json.loads(Path(batch_file).read_text(encoding="utf-8"))
    queue = set(json.loads(QUEUE.read_text(encoding="utf-8")))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    done = {e["raw_path"] for e in manifest}

    errors, fresh = [], []
    for e in batch:
        missing = REQUIRED - set(e)
        if missing:
            errors.append(f"{e.get('raw_path','?')}: missing {missing}")
            continue
        if e["domain"] not in DOMAINS:
            errors.append(f"{e['raw_path']}: bad domain {e['domain']}")
        if e["action"] not in ACTIONS:
            errors.append(f"{e['raw_path']}: bad action {e['action']}")
        if not isinstance(e["reusability_score"], int) or not 1 <= e["reusability_score"] <= 10:
            errors.append(f"{e['raw_path']}: score must be int 1-10")
        if len(e["content_summary"]) < 20 or e["content_summary"].startswith(("Core reference", "Standardized template", "Temporary or obsolete")):
            errors.append(f"{e['raw_path']}: generic/banned summary")
        if e["raw_path"] not in queue:
            errors.append(f"{e['raw_path']}: not in remaining queue")
        if e["raw_path"] in done:
            errors.append(f"{e['raw_path']}: already classified")
        fresh.append(e)

    if errors:
        print("REJECTED — fix these:")
        for x in errors:
            print(" ", x)
        sys.exit(1)

    bak = MANIFEST.with_suffix(".json.bak")
    shutil.copy2(MANIFEST, bak)
    manifest.extend(fresh)
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")

    total_done = len({e["raw_path"] for e in manifest})
    print(f"merged {len(fresh)} | manifest now covers {total_done}/443 | backup: {bak.name}")


if __name__ == "__main__":
    main(sys.argv[1])
