#!/usr/bin/env python3
"""M6b: Tests for build_doc_anchors.py (document-level fingerprint embeddings).

Unit tests cover pure anchor-text composition.
E2E tests run the real builder against the live DB + Ollama and verify the
doc_anchors table is complete, well-formed, and idempotent.
"""
import math
import sqlite3
import sys
import unittest
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import build_doc_anchors as bda  # noqa: E402
import search_engine  # noqa: E402

BUILDER_SCRIPT = PROJECT_ROOT / "build_doc_anchors.py"
DB_PATH = PROJECT_ROOT / "Processed_Assets" / "my_rag_data.db"


class TestAnchorTextComposition(unittest.TestCase):
    def test_u01_includes_all_parts(self):
        row = {
            "asset_title": "Subbroking Growth Engine",
            "problem_solved": "How to find clients for finance advisory",
            "tags": "finance, clients",
            "rating_tier": "Must Keep - High Reusability",
            "topic": "08_Business_Operations_and_Subbroking",
        }
        txt = bda.build_anchor_text(row)
        for part in ("Subbroking Growth Engine", "find clients", "finance",
                     "Must Keep", "Business_Operations"):
            self.assertIn(part, txt)

    def test_u02_skips_empty_parts_no_double_separators(self):
        txt = bda.build_anchor_text({"asset_title": "Only Title", "topic": None})
        self.assertNotIn("||", txt)
        self.assertNotIn("| |", txt)
        self.assertIn("Only Title", txt)

    def test_u03_truncated_to_budget(self):
        big = {"asset_title": "x" * 5000}
        self.assertLessEqual(len(bda.build_anchor_text(big)), bda.ANCHOR_MAX_CHARS)


def _ollama_up() -> bool:
    try:
        search_engine._embed_query("ping")
        return True
    except Exception:
        return False


@unittest.skipUnless(DB_PATH.exists() and BUILDER_SCRIPT.exists(), "project data missing")
@unittest.skipUnless(_ollama_up(), "Ollama not running - embed tests skipped")
class TestEndToEndAnchorBuild(unittest.TestCase):
    """Runs the real builder twice; verifies completeness + idempotency."""

    @classmethod
    def setUpClass(cls):
        cls.proc1 = subprocess.run(
            [sys.executable, str(BUILDER_SCRIPT)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800,
        )
        cls.proc2 = subprocess.run(
            [sys.executable, str(BUILDER_SCRIPT)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600,
        )

    def _counts(self):
        conn = sqlite3.connect(DB_PATH)
        try:
            n_docs = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            n_anchor = conn.execute(
                "SELECT COUNT(*) FROM doc_anchors WHERE model=?", (bda.EMBED_MODEL,)
            ).fetchone()[0]
            sample = conn.execute(
                "SELECT embedding FROM doc_anchors WHERE model=? LIMIT 1", (bda.EMBED_MODEL,)
            ).fetchone()
        finally:
            conn.close()
        return n_docs, n_anchor, sample

    def test_e01_builder_exits_zero(self):
        self.assertEqual(self.proc1.returncode, 0, f"builder failed: {self.proc1.stderr[-800:]}")

    def test_e02_every_document_has_anchor(self):
        n_docs, n_anchor, _ = self._counts()
        self.assertEqual(n_docs, n_anchor, f"docs={n_docs} anchors={n_anchor}")

    def test_e03_embeddings_wellformed(self):
        _, _, sample = self._counts()
        self.assertIsNotNone(sample, "no anchor rows found")
        vec = __import__("numpy").frombuffer(sample[0], dtype=__import__("numpy").float32)
        self.assertEqual(len(vec), 768)
        self.assertAlmostEqual(float((vec ** 2).sum()) ** 0.5, 1.0, places=2)

    def test_e04_idempotent_rerun(self):
        self.assertEqual(self.proc2.returncode, 0)
        n_docs, n_anchor, _ = self._counts()
        self.assertEqual(n_docs, n_anchor, "rerun created duplicate/missing anchors")


if __name__ == "__main__":
    unittest.main()
