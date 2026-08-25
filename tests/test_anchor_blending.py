#!/usr/bin/env python3
"""M6c: Tests for document-anchor blending in search_engine.py ranking.

Unit tests cover the pure blend maths.
E2E tests verify that vague business queries surface the right playbook
(the acceptance case: 'find clients for finance advisory' must rank the
subbroking playbook near the top instead of regulatory PDFs/CVs).
"""
import sys
import unittest
import subprocess
from pathlib import Path
from unittest import mock

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import search_engine  # noqa: E402

SEARCH_ENGINE_SCRIPT = PROJECT_ROOT / "search_engine.py"
DB_PATH = PROJECT_ROOT / "Processed_Assets" / "my_rag_data.db"

SUBPROC_KWARGS = dict(capture_output=True, text=True, encoding="utf-8",
                      errors="replace", timeout=120)


def run_cli(*args):
    return subprocess.run([sys.executable, str(SEARCH_ENGINE_SCRIPT), *args], **SUBPROC_KWARGS)


def _ollama_up() -> bool:
    try:
        search_engine._embed_query("ping")
        return True
    except Exception:
        return False


class TestFuseMaths(unittest.TestCase):
    def _fuse(self, chunk_sims, doc_ids, ranks):
        return search_engine.fuse_chunk_anchor_scores(
            np.asarray(chunk_sims, dtype=np.float32), doc_ids, ranks
        )

    def test_u01_better_document_outranks_higher_chunk_score(self):
        # Chunk A scores higher on raw text similarity but belongs to a
        # mediocre document; chunk B's document is anchor-ranked #1.
        sims = [0.90, 0.80]
        docs = [111, 222]
        ranks = {111: 50, 222: 1}
        out = self._fuse(sims, docs, ranks)
        self.assertGreater(out[1], out[0])

    def test_u02_zero_weight_is_pure_chunk_ranking(self):
        rng = np.random.default_rng(7)
        sims = rng.random(20).astype(np.float32)
        out = self._fuse(sims, [None] * 20, {5: 1})
        expected_order = np.argsort(-sims)
        np.testing.assert_array_equal(np.argsort(-out), expected_order)

    def test_u03_unknown_documents_get_no_bonus(self):
        base = self._fuse([0.5], [999], {})
        boosted = self._fuse([0.5], [999], {999: 1})
        self.assertEqual(float(base[0]), 1.0 / (search_engine.RRF_K + 1))
        self.assertGreater(float(boosted[0]), float(base[0]))

    def test_u04_diversity_cap_limits_document_hogging(self):
        chunk_ids = np.array([1, 2, 3, 4, 5, 6])
        doc_map = {1: "A", 2: "A", 3: "A", 4: "B", 5: "B", 6: "C"}
        picked = search_engine.diverse_top(
            iter(range(6)), chunk_ids, doc_map, limit=4, max_per_doc=2
        )
        self.assertEqual(picked, [0, 1, 3, 4])


@unittest.skipUnless(DB_PATH.exists(), "RAG database not found")
class TestAnchorInfrastructure(unittest.TestCase):
    def test_i01_anchor_loader_returns_aligned_arrays(self):
        doc_ids, matrix = search_engine._load_anchor_matrix()
        self.assertGreater(len(doc_ids), 400)
        self.assertEqual(matrix.shape[0], len(doc_ids))
        self.assertEqual(matrix.shape[1], 768)

    def test_i02_graceful_when_no_anchors(self):
        with mock.patch.object(search_engine, "_load_anchor_matrix", return_value=(None, None)), \
             mock.patch.object(search_engine, "_load_chunk_doc_map", return_value={}):
            proc = run_cli("any query at all", "--mode", "semantic", "--limit", "2")
            self.assertEqual(proc.returncode, 0)
            self.assertIn("SEMANTIC RESULTS", proc.stdout)


def _result_titles(stdout):
    titles = []
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("[") and "]" in line:
            titles.append(line.split("]", 1)[1].strip().lower())
    return titles


@unittest.skipUnless(DB_PATH.exists() and _ollama_up(), "DB or Ollama unavailable")
class TestAcceptanceVagueBusinessQuery(unittest.TestCase):
    """The original weak spot must be fixed by anchor blending."""

    QUERY = ["find", "clients", "for", "finance", "advisory"]

    def test_a01_semantic_top5_includes_subbroking_playbook(self):
        proc = run_cli(" ".join(self.QUERY), "--mode", "semantic", "--limit", "5")
        self.assertEqual(proc.returncode, 0)
        titles = "\n".join(_result_titles(proc.stdout))
        self.assertIn("subbroking", titles,
                      f"subbroking playbook not in top-5:\n{titles}")

    def test_a02_hybrid_top5_includes_subbroking_playbook(self):
        proc = run_cli(" ".join(self.QUERY), "--mode", "hybrid", "--limit", "5")
        self.assertEqual(proc.returncode, 0)
        titles = "\n".join(_result_titles(proc.stdout))
        self.assertIn("subbroking", titles,
                      f"subbroking playbook not in top-5:\n{titles}")

    def test_a03_no_cv_in_semantic_top5(self):
        proc = run_cli(" ".join(self.QUERY), "--mode", "semantic", "--limit", "5")
        titles = "\n".join(_result_titles(proc.stdout))
        self.assertNotIn("cv_", titles)
        self.assertNotIn("abhishek", titles)


if __name__ == "__main__":
    unittest.main()
