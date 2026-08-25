#!/usr/bin/env python3
"""M6a: Tests for build_folder_indexes.py (per-folder CSV indexes + master CSV).

Unit tests use synthetic fixtures (pure functions).
E2E tests run the builder against the real project tree (read-only inputs,
writes only new INDEX_*.csv / MASTER_ASSET_INDEX.csv files).
"""
import csv
import sys
import unittest
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import build_folder_indexes as bfi  # noqa: E402

BUILDER_SCRIPT = PROJECT_ROOT / "build_folder_indexes.py"


class TestBuildRowSynthetic(unittest.TestCase):
    """Pure-function behaviour of build_row."""

    def setUp(self):
        self.manifest = {
            "wf.json": {
                "raw_path": "Raw_copies/wf.json",
                "domain": "02_Workflow_Automations_n8n",
                "content_summary": "n8n workflow for personal assistant AI agent",
                "reusability_score": 8,
                "target_gm": "GM_AI_Agent_Army.md",
            }
        }
        self.db = {
            "wf.json": {
                "asset_title": "Personal Assistant Workflow",
                "problem_solved": "Automates daily assistant tasks",
                "rating_tier": "Must Keep - High Reusability",
                "tags": "n8n, agent",
                "workability": "ready_to_use",
            }
        }

    def _row(self, name="wf.json"):
        p = Path("02_Workflow_Automations_n8n") / name
        return bfi.build_row(p, self.manifest, self.db)

    def test_s01_full_enrichment(self):
        r = self._row()
        self.assertEqual(r["file_name"], "wf.json")
        self.assertEqual(r["title"], "Personal Assistant Workflow")
        self.assertEqual(r["description"], "n8n workflow for personal assistant AI agent")
        self.assertEqual(r["problem_solved"], "Automates daily assistant tasks")
        self.assertEqual(r["rating"], "8")
        self.assertEqual(r["gem"], "YES")
        self.assertEqual(r["tags"], "n8n, agent")
        self.assertEqual(r["workability"], "ready_to_use")
        self.assertEqual(r["domain"], "02_Workflow_Automations_n8n")
        self.assertEqual(r["format"], ".json")
        self.assertEqual(r["related_files"], "GM_AI_Agent_Army.md")
        self.assertEqual(r["source_path"], "Raw_copies/wf.json")

    def test_s02_low_rating_not_gem(self):
        self.manifest["wf.json"]["reusability_score"] = 5
        r = self._row()
        self.assertEqual(r["rating"], "5")
        self.assertEqual(r["gem"], "")

    def test_s02b_no_numeric_score_falls_back_to_tier(self):
        del self.manifest["wf.json"]["reusability_score"]
        self.assertEqual(self._row()["rating"], "Must Keep - High Reusability")
        self.assertEqual(self._row()["gem"], "")

    def test_s03_unknown_file_falls_back_gracefully(self):
        r = self._row("brand_new_thing.md")
        self.assertEqual(r["file_name"], "brand_new_thing.md")
        self.assertIn("no catalog entry", r["description"])
        self.assertEqual(r["rating"], "")
        self.assertEqual(r["gem"], "")
        self.assertTrue(str(r["title"]))


@unittest.skipUnless(
    BUILDER_SCRIPT.exists()
    and (PROJECT_ROOT / "02_Assets_Library").exists()
    and (PROJECT_ROOT / "Processed_Assets" / "file_classification_manifest.json").exists(),
    "project data not found",
)
class TestEndToEndRealRepo(unittest.TestCase):
    """Runs the real builder and validates its outputs."""

    @classmethod
    def setUpClass(cls):
        cls.proc = subprocess.run(
            [sys.executable, str(BUILDER_SCRIPT)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
        )

    def test_e01_builder_exits_zero(self):
        self.assertEqual(self.proc.returncode, 0, f"builder failed: {self.proc.stderr}")

    def test_e02_all_ten_folder_csvs_exist_nonzero(self):
        lib = PROJECT_ROOT / "02_Assets_Library"
        csvs = sorted(lib.glob("*/INDEX_*.csv"))
        self.assertEqual(len(csvs), 10, f"expected 10 folder CSVs, got {len(csvs)}")
        for p in csvs:
            self.assertGreater(p.stat().st_size, 0, f"{p.name} is zero-size")

    def test_e03_master_csv_exists_with_all_rows(self):
        master = PROJECT_ROOT / "00_Index_and_Dashboards" / "MASTER_ASSET_INDEX.csv"
        self.assertTrue(master.exists(), "master CSV missing")
        self.assertGreater(master.stat().st_size, 0, "master CSV is zero-size")
        with open(master, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        lib = PROJECT_ROOT / "02_Assets_Library"
        n_files = sum(
            1 for d in lib.iterdir() if d.is_dir()
            for f in d.rglob("*")
            if f.is_file() and not (f.name.startswith("INDEX_") and f.suffix.lower() == ".csv")
        )
        self.assertEqual(len(rows), n_files, "master row count != files on disk")
        for r in rows[:50]:
            self.assertTrue(r.get("file_name"), f"row missing file_name: {r}")

    def test_e04_known_file_has_description(self):
        master = PROJECT_ROOT / "00_Index_and_Dashboards" / "MASTER_ASSET_INDEX.csv"
        with open(master, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        by_name = {r["file_name"]: r for r in rows}
        target = next((k for k in by_name if k.lower().startswith("n8n_trading_system")), None)
        if target is None:
            self.skipTest("known sample file not present in library")
        self.assertTrue(by_name[target]["description"].strip())
        self.assertNotEqual(by_name[target]["gem"].strip(), "", "high-rated trading file should be a gem")


if __name__ == "__main__":
    unittest.main()
