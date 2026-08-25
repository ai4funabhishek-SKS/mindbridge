#!/usr/bin/env python3
"""Build per-folder CSV indexes + one master CSV for the Asset Library.

For every file under 02_Assets_Library/<domain>/ this produces a row with
catalogue metadata joined from:
  - Processed_Assets/file_classification_manifest.json (content_summary,
    reusability_score, target_gm, raw_path)
  - Processed_Assets/my_rag_data.db documents table (asset_title,
    problem_solved, rating, tags, workability)

Outputs:
  - 02_Assets_Library/<domain>/INDEX_<domain>.csv  (one per folder)
  - 00_Index_and_Dashboards/MASTER_ASSET_INDEX.csv  (all rows combined)

Idempotent: re-running overwrites the generated CSVs in place.
"""
import csv
import json
import sqlite3
import sys
from pathlib import Path

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
LIBRARY_DIR = BASE_DIR / "02_Assets_Library"
MANIFEST_PATH = BASE_DIR / "Processed_Assets" / "file_classification_manifest.json"
DB_PATH = BASE_DIR / "Processed_Assets" / "my_rag_data.db"
DASHBOARDS_DIR = BASE_DIR / "00_Index_and_Dashboards"
MASTER_CSV_PATH = DASHBOARDS_DIR / "MASTER_ASSET_INDEX.csv"

COLUMNS = [
    "file_name", "title", "description", "problem_solved",
    "rating", "gem", "workability", "tags",
    "domain", "format", "size_kb", "related_files", "source_path",
]
GEM_THRESHOLD = 8


def load_catalogues():
    """Returns ({basename_lower: manifest_entry}, {basename_lower: db_row_dict})."""
    manifest_by_base = {}
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            for entry in json.load(f):
                base = Path(entry.get("raw_path", "")).name.lower()
                if base:
                    manifest_by_base.setdefault(base, entry)

    db_by_base = {}
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        try:
            rows = conn.execute(
                """SELECT file_name, asset_title, problem_solved, rating, tags, workability
                   FROM documents WHERE relative_path LIKE 'Raw_copies/%'"""
            ).fetchall()
        finally:
            conn.close()
        for fname, title, problem, rating, tags, workability in rows:
            db_by_base[fname.lower()] = {
                "asset_title": title or "",
                "problem_solved": problem or "",
                "rating_tier": rating or "",
                "tags": tags or "",
                "workability": workability or "",
            }
    return manifest_by_base, db_by_base


def build_row(file_path: Path, manifest_by_base: dict, db_by_base: dict) -> dict:
    """Builds one CSV row dict for a library file. Pure function."""
    name = file_path.name
    base = name.lower()
    domain = file_path.parent.name

    mentry = manifest_by_base.get(base, {})
    drow = db_by_base.get(base, {})

    description = mentry.get("content_summary") or (
        "(no catalog entry - generated artifact)" if mentry == {} else ""
    ) or "(no catalog summary)"
    problem = drow.get("problem_solved", "")

    # Numeric 1-10 score lives in the manifest; documents.rating holds text
    # tiers like "Must Keep - High Reusability". Numeric wins; tier is fallback.
    numeric_score = mentry.get("reusability_score")
    db_tier = drow.get("rating_tier", "")
    if numeric_score is not None:
        rating_str = str(numeric_score)
    elif db_tier:
        rating_str = db_tier
    else:
        rating_str = ""

    try:
        gem = (
            "YES"
            if numeric_score is not None and float(numeric_score) >= GEM_THRESHOLD
            else ""
        )
    except (TypeError, ValueError):
        gem = ""

    try:
        size_kb = str(round(file_path.stat().st_size / 1024, 1))
    except OSError:
        size_kb = ""

    return {
        "file_name": name,
        "title": drow.get("asset_title") or file_path.stem.replace("_", " ").replace("-", " "),
        "description": description,
        "problem_solved": problem,
        "rating": rating_str,
        "gem": gem,
        "workability": drow.get("workability", ""),
        "tags": drow.get("tags", ""),
        "domain": domain,
        "format": file_path.suffix.lower(),
        "size_kb": size_kb,
        "related_files": mentry.get("target_gm", ""),
        "source_path": mentry.get("raw_path", ""),
    }


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    manifest_by_base, db_by_base = load_catalogues()

    folders = sorted(d for d in LIBRARY_DIR.iterdir() if d.is_dir())
    all_rows = []
    print(f"Catalogues loaded: {len(manifest_by_base)} manifest entries, "
          f"{len(db_by_base)} DB documents")

    for folder in folders:
        files = sorted(
            f for f in folder.rglob("*")
            if f.is_file() and not (f.name.startswith("INDEX_") and f.suffix.lower() == ".csv")
        )
        rows = [build_row(f, manifest_by_base, db_by_base) for f in files]
        csv_path = folder / f"INDEX_{folder.name}.csv"
        write_csv(csv_path, rows)
        gems = sum(1 for r in rows if r["gem"] == "YES")
        enriched = sum(1 for r in rows if not r["description"].startswith("(no catalog"))
        print(f"  {folder.name}: {len(rows)} files -> {csv_path.name} "
              f"({enriched} catalogued, {gems} gems)")
        all_rows.extend(rows)

    write_csv(MASTER_CSV_PATH, all_rows)
    print(f"\nMASTER index: {len(all_rows)} rows -> {MASTER_CSV_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
