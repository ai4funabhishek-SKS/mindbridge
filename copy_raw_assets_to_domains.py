import os
import sys
import json
import shutil
from pathlib import Path
from collections import defaultdict

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"C:\knowledgeBase_staging")
MANIFEST_PATH = BASE_DIR / "Processed_Assets" / "file_classification_manifest.json"
RAW_COPIES_DIR = BASE_DIR / "Raw_copies"
ASSETS_LIB_DIR = BASE_DIR / "02_Assets_Library"
ARCHIVE_DIR = BASE_DIR / "04_Archive_Cold_Storage" / "classified_archive"
REPORT_PATH = BASE_DIR / "Processed_Assets" / "copy_raw_assets_report.json"

def main():
    print(f"Reading manifest from {MANIFEST_PATH}...")
    with open(MANIFEST_PATH, "r", encoding="utf-8", errors="ignore") as f:
        manifest = json.load(f)

    print(f"Total manifest entries: {len(manifest)}")

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_LIB_DIR.mkdir(parents=True, exist_ok=True)

    domain_counts = defaultdict(int)
    archive_count = 0
    missing_files = []
    errors = []
    copied_records = []

    for idx, entry in enumerate(manifest):
        raw_path = entry.get("raw_path", "")
        filename = Path(raw_path).name
        domain = entry.get("domain", "").strip()
        action = entry.get("action", "").strip().lower()

        src_file = RAW_COPIES_DIR / filename

        if not src_file.exists():
            missing_files.append({"filename": filename, "raw_path": raw_path, "domain": domain, "action": action})
            print(f"WARNING: Source file not found: {src_file}")
            continue

        try:
            if action == "archive" or domain.upper() == "ARCHIVE":
                dst_file = ARCHIVE_DIR / filename
                shutil.copy2(src_file, dst_file)
                archive_count += 1
                copied_records.append({
                    "filename": filename,
                    "type": "archive",
                    "destination": str(dst_file),
                    "bytes": dst_file.stat().st_size
                })
            else:
                target_domain_dir = ASSETS_LIB_DIR / domain
                target_domain_dir.mkdir(parents=True, exist_ok=True)
                dst_file = target_domain_dir / filename
                shutil.copy2(src_file, dst_file)
                domain_counts[domain] += 1
                copied_records.append({
                    "filename": filename,
                    "type": "asset",
                    "domain": domain,
                    "destination": str(dst_file),
                    "bytes": dst_file.stat().st_size
                })
        except Exception as e:
            err_msg = f"Error copying {filename}: {str(e)}"
            errors.append(err_msg)
            print(f"ERROR: {err_msg}")

    print("\n--- Domain Summary in 02_Assets_Library ---")
    for domain, count in sorted(domain_counts.items()):
        print(f"  {domain}: {count} files")

    print(f"\n--- Archive Summary ---")
    print(f"  Archived files: {archive_count}")

    print(f"\n--- Verification of 02_Assets_Library Subdirectories ---")
    actual_domain_counts = {}
    for sub in sorted(ASSETS_LIB_DIR.iterdir()):
        if sub.is_dir():
            count = len(list(sub.iterdir()))
            actual_domain_counts[sub.name] = count
            print(f"  {sub.name}: {count} files on disk")

    actual_archive_count = len(list(ARCHIVE_DIR.iterdir())) if ARCHIVE_DIR.exists() else 0
    print(f"\n--- Verification of classified_archive ---")
    print(f"  classified_archive: {actual_archive_count} files on disk")

    report = {
        "total_manifest_entries": len(manifest),
        "total_domain_copied": sum(domain_counts.values()),
        "total_archived": archive_count,
        "missing_files_count": len(missing_files),
        "missing_files": missing_files,
        "errors_count": len(errors),
        "errors": errors,
        "domain_counts": dict(domain_counts),
        "actual_domain_counts_on_disk": actual_domain_counts,
        "actual_archive_count_on_disk": actual_archive_count
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport written to {REPORT_PATH}")
    print("Done!")

if __name__ == "__main__":
    main()
