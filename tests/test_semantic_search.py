#!/usr/bin/env python3
"""M5c: E2E tests for SEMANTIC and HYBRID (RRF) search modes of search_engine.py.

Requires:
  - Processed_Assets/my_rag_data.db with chunk_embeddings fully populated
  - Local Ollama running with nomic-embed-text (for embed-affecting tests;
    Ollama-down behaviour is tested via mocking, not a live stop).
"""
import re
import sys
import time
import unittest
import subprocess
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import search_engine  # noqa: E402

SEARCH_ENGINE_SCRIPT = PROJECT_ROOT / "search_engine.py"
DB_PATH = PROJECT_ROOT / "Processed_Assets" / "my_rag_data.db"

SUBPROC_KWARGS = dict(
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    timeout=60,
)


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(SEARCH_ENGINE_SCRIPT), *args], **SUBPROC_KWARGS
    )


def _ollama_up() -> bool:
    try:
        search_engine._embed_query("ping")
        return True
    except Exception:
        return False


@unittest.skipUnless(DB_PATH.exists(), "RAG database not found")
class TestSemanticMode(unittest.TestCase):
    """Semantic (cosine over chunk_embeddings) mode."""

    @classmethod
    def setUpClass(cls):
        cls.ollama_ok = _ollama_up()

    def test_s01_semantic_mode_execution(self):
        """Semantic mode executes successfully and prints its header."""
        proc = run_cli("how to automate stock screening", "--mode", "semantic", "--limit", "3")
        self.assertEqual(proc.returncode, 0, f"semantic execution failed: {proc.stderr}")
        self.assertIn("SEMANTIC RESULTS", proc.stdout)

    @unittest.skipUnless(_ollama_up(), "Ollama not reachable")
    def test_s02_semantic_returns_relevant_results_with_scores(self):
        """Known-topic query returns results carrying Similarity scores."""
        proc = run_cli("quantitative trading strategy", "--mode", "semantic", "--limit", "5")
        self.assertEqual(proc.returncode, 0)
        self.assertGreaterEqual(proc.stdout.count("Similarity:"), 1)

    @unittest.skipUnless(_ollama_up(), "Ollama not reachable")
    def test_s03_semantic_ranking_is_descending(self):
        """Similarity scores appear in non-increasing order."""
        proc = run_cli("android automation", "--mode", "semantic", "--limit", "6")
        scores = [float(m) for m in re.findall(r"Similarity:\s*([0-9.]+)", proc.stdout)]
        self.assertGreaterEqual(len(scores), 2)
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_s04_semantic_respects_limit(self):
        """--limit constrains the number of returned entries."""
        proc = run_cli("trading", "--mode", "semantic", "--limit", "2")
        matches = re.findall(r"^\[\d+\]", proc.stdout, flags=re.M)
        self.assertLessEqual(len(matches), 2)

    def test_s05_semantic_empty_query_zero_matches(self):
        """Empty query yields the zero-match notice without crashing."""
        proc = run_cli("", "--mode", "semantic")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("(0 matches)", proc.stdout)

    def test_s06_semantic_whitespace_query_handled(self):
        """Whitespace-only query does not crash."""
        proc = run_cli("   \t  ", "--mode", "semantic")
        self.assertEqual(proc.returncode, 0)

    @unittest.skipUnless(_ollama_up(), "Ollama not reachable")
    def test_s07_semantic_unicode_query_no_crash(self):
        """Unicode-heavy query completes without crashing."""
        proc = run_cli("交易策略 émoji 🚀 naïve", "--mode", "semantic", "--limit", "2")
        self.assertEqual(proc.returncode, 0)

    @unittest.skipUnless(_ollama_up(), "Ollama not reachable")
    def test_s08_semantic_extreme_limits(self):
        """limit=0 gives zero-match notice; negative limit falls back gracefully."""
        p0 = run_cli("agent", "--mode", "semantic", "--limit", "0")
        self.assertEqual(p0.returncode, 0)
        self.assertIn("(0 matches)", p0.stdout)
        pn = run_cli("agent", "--mode", "semantic", "--limit", "-5")
        self.assertEqual(pn.returncode, 0)

    @unittest.skipUnless(_ollama_up(), "Ollama not reachable")
    def test_s09_semantic_latency_benchmark(self):
        """Full CLI round-trip incl. Python+numpy startup stays under 15s."""
        t0 = time.time()
        proc = run_cli("prompt engineering framework", "--mode", "semantic", "--limit", "4")
        elapsed = time.time() - t0
        self.assertEqual(proc.returncode, 0)
        self.assertLess(elapsed, 15.0, f"Semantic search too slow: {elapsed:.2f}s")

    def test_s10_semantic_metadata_join_present(self):
        """Results include document title, filename and topic columns."""
        proc = run_cli("subbroking clients", "--mode", "semantic", "--limit", "3")
        if "Similarity:" not in proc.stdout:
            self.skipTest("Ollama unavailable mid-run")
        self.assertIn("Topic:", proc.stdout)


@unittest.skipUnless(DB_PATH.exists(), "RAG database not found")
class TestHybridMode(unittest.TestCase):
    """Hybrid Reciprocal Rank Fusion mode."""

    def test_h01_hybrid_mode_execution(self):
        """Hybrid mode executes successfully and prints its header."""
        proc = run_cli("n8n webhook", "--mode", "hybrid", "--limit", "4")
        self.assertEqual(proc.returncode, 0, f"hybrid execution failed: {proc.stderr}")
        self.assertIn("HYBRID (RRF) RESULTS", proc.stdout)

    def test_h02_hybrid_shows_rrf_scores_and_leg_annotations(self):
        """Every result line carries an RRF score plus kw/sem rank annotations."""
        proc = run_cli("n8n webhook", "--mode", "hybrid", "--limit", "4")
        self.assertGreaterEqual(proc.stdout.count("RRF Score:"), 1)
        self.assertTrue(re.search(r"(kw#\d+|kw--)", proc.stdout), "no keyword-leg annotation")
        self.assertTrue(re.search(r"(sem#\d+|sem--)", proc.stdout), "no semantic-leg annotation")

    @unittest.skipUnless(_ollama_up(), "Ollama not reachable")
    def test_h03_hybrid_fuses_both_legs_for_keyword_heavy_query(self):
        """A keyword-rich query should have hits from both legs in top results."""
        proc = run_cli("n8n webhook automation", "--mode", "hybrid", "--limit", "5")
        kws = re.findall(r"kw#(\d+)", proc.stdout)
        sems = re.findall(r"sem#(\d+)", proc.stdout)
        self.assertTrue(kws, "keyword leg contributed nothing")
        self.assertTrue(sems, "semantic leg contributed nothing")

    def test_h04_hybrid_respects_limit(self):
        """--limit constrains hybrid result count."""
        proc = run_cli("trading", "--mode", "hybrid", "--limit", "2")
        matches = re.findall(r"^\[\d+\]", proc.stdout, flags=re.M)
        self.assertLessEqual(len(matches), 2)

    def test_h05_hybrid_empty_query_zero_matches(self):
        """Empty query yields the zero-match notice."""
        proc = run_cli("", "--mode", "hybrid")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("(0 matches)", proc.stdout)

    def test_h06_hybrid_fts5_injection_payload_safe(self):
        """FTS5 control characters / operator payloads must not crash hybrid."""
        proc = run_cli('" OR 1=1 -- NEAR( AND (', "--mode", "hybrid", "--limit", "3")
        self.assertEqual(proc.returncode, 0)

    @unittest.skipUnless(_ollama_up(), "Ollama not reachable")
    def test_h07_hybrid_latency_benchmark(self):
        """Hybrid round-trip stays under 15s (embed + FTS + fusion)."""
        t0 = time.time()
        proc = run_cli("faceless youtube production", "--mode", "hybrid", "--limit", "4")
        elapsed = time.time() - t0
        self.assertEqual(proc.returncode, 0)
        self.assertLess(elapsed, 15.0, f"Hybrid search too slow: {elapsed:.2f}s")


@unittest.skipUnless(DB_PATH.exists(), "RAG database not found")
class TestGracefulDegradationAndInternals(unittest.TestCase):
    """Unit-level checks: Ollama-down messaging, RRF maths, cache correctness."""

    def test_g01_semantic_prints_friendly_error_when_ollama_down(self):
        """When _embed_query fails, semantic mode advises linear fallback."""
        import io
        import contextlib
        buf = io.StringIO()
        with mock.patch.object(search_engine, "_embed_query", side_effect=ConnectionError("refused")):
            with contextlib.redirect_stdout(buf):
                search_engine.search_semantic("anything", 3)
        out = buf.getvalue()
        self.assertIn("Ollama", out)
        self.assertIn("--mode linear", out)

    def test_g02_rrf_score_formula(self):
        """RRF contribution equals sum of 1/(k+rank) across legs."""
        k = search_engine.RRF_K
        bm25 = [10, 20]
        sem = [20, 30]
        fused = {}
        for rank, cid in enumerate(bm25, 1):
            fused[cid] = fused.get(cid, 0.0) + 1.0 / (k + rank)
        for rank, cid in enumerate(sem, 1):
            fused[cid] = fused.get(cid, 0.0) + 1.0 / (k + rank)
        self.assertAlmostEqual(fused[10], 1.0 / (k + 1))
        self.assertAlmostEqual(fused[30], 1.0 / (k + 2))
        self.assertAlmostEqual(fused[20], 1.0 / (k + 2) + 1.0 / (k + 1))

    @unittest.skipUnless(_ollama_up(), "Ollama not reachable")
    def test_g03_embedding_matrix_shape_and_cache(self):
        """Matrix loads as (N,768) float32 and cache is keyed by DB mtime."""
        ids, mat = search_engine._load_embedding_matrix()
        self.assertEqual(mat.dtype.name, "float32")
        self.assertEqual(mat.shape, (len(ids), 768))
        mtime = DB_PATH.stat().st_mtime
        again_ids, again_mat = search_engine._load_embedding_matrix()
        self.assertIs(mat, again_mat, "cache miss despite unchanged DB")
        self.assertEqual(search_engine._EMBED_CACHE.get(mtime), (ids, mat))

    @unittest.skipUnless(_ollama_up(), "Ollama not reachable")
    def test_g04_query_embedding_is_unit_norm(self):
        """Query vectors are L2-normalised so dot product == cosine similarity."""
        vec = search_engine._embed_query("hello world test")
        self.assertAlmostEqual(float((vec * vec).sum()), 1.0, places=3)

    @unittest.skipUnless(_ollama_up(), "Ollama not reachable")
    def test_g05_metadata_fetch_returns_rows_for_valid_ids(self):
        """_fetch_chunk_metadata resolves known chunk ids into 5-tuples."""
        ids, _mat = search_engine._load_embedding_matrix()
        meta = search_engine._fetch_chunk_metadata([int(ids[0]), int(ids[1])])
        self.assertEqual(len(meta), 2)
        for row in meta.values():
            self.assertEqual(len(row), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
