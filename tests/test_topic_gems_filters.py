#!/usr/bin/env python3
"""M6d: Tests for --topic / --topics filters and --gems quality filter."""
import sys
import unittest
import subprocess
from pathlib import Path

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


@unittest.skipUnless(DB_PATH.exists(), "RAG database not found")
class TestTopicInfrastructure(unittest.TestCase):
    def test_i01_resolve_known_topic(self):
        ids = search_engine._resolve_topic_filter("subbroking")
        self.assertGreater(len(ids), 0)

    def test_i02_unknown_topic_is_empty(self):
        self.assertEqual(search_engine._resolve_topic_filter("zzz-no-such-zzz"), set())

    def test_i03_gem_ids_loaded_from_manifest(self):
        gems = search_engine._load_gem_doc_ids()
        self.assertGreater(len(gems), 50, "expected ~100+ gem-rated documents")

    def test_i04_list_topics_prints_counts(self):
        proc = run_cli("--topics")
        self.assertEqual(proc.returncode, 0)
        self.assertGreaterEqual(proc.stdout.count("|"), 10)
        self.assertIn("documents", proc.stdout.lower())


@unittest.skipUnless(DB_PATH.exists(), "RAG database not found")
class TestLinearTopicFilter(unittest.TestCase):
    def test_l01_results_confined_to_topic(self):
        proc = run_cli("workflow automation", "--mode", "linear",
                       "--topic", "n8n", "--limit", "6")
        self.assertEqual(proc.returncode, 0)
        topics = [ln.split("Topic:")[1].split("|")[0].strip().lower()
                  for ln in proc.stdout.splitlines() if "Topic:" in ln]
        self.assertGreater(len(topics), 0)
        for t in topics:
            self.assertIn("n8n", t, f"result outside n8n topic: {t}")

    def test_l02_impossible_topic_yields_zero_matches(self):
        proc = run_cli("anything", "--mode", "linear",
                       "--topic", "zzz-no-such-zzz", "--limit", "6")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("(0 matches)", proc.stdout)


@unittest.skipUnless(DB_PATH.exists() and _ollama_up(), "DB or Ollama unavailable")
class TestSemanticTopicAndGems(unittest.TestCase):
    def test_s01_semantic_respects_topic_filter(self):
        proc = run_cli("how to acquire high paying clients", "--mode", "semantic",
                       "--topic", "subbroking", "--limit", "5")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("SEMANTIC RESULTS", proc.stdout)
        topics = [ln.split("Topic:")[1].split("|")[0].strip().lower()
                  for ln in proc.stdout.splitlines() if "Topic:" in ln]
        for t in topics:
            self.assertIn("subbroking", t)

    def test_s02_hybrid_gems_only_returns_gem_docs(self):
        proc = run_cli("trading system", "--mode", "hybrid", "--gems",
                       "--limit", "6")
        self.assertEqual(proc.returncode, 0)
        # every returned file must exist in the gem set
        gems = search_engine._load_gem_doc_ids()
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        try:
            for ln in proc.stdout.splitlines():
                ln = ln.strip()
                if ln.startswith("[") and "(" in ln and ")" in ln:
                    fname = ln[ln.index("(") + 1:ln.rindex(")")].strip().lower()
                    did = conn.execute(
                        "SELECT id FROM documents WHERE lower(file_name)=?",
                        (fname,),
                    ).fetchone()
                    if did:
                        self.assertIn(did[0], gems,
                                      f"non-gem document leaked through: {fname}")
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
