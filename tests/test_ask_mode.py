#!/usr/bin/env python3
"""M6e: Tests for Ask mode (funnel retrieval + local LLM synthesis).

Unit tests cover pure helpers (prompt building, passage selection, briefing
file writing) without any network calls.
E2E tests run real Ask queries against local Ollama (skipped when down).
"""
import sys
import unittest
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import search_engine as se  # noqa: E402

SEARCH_ENGINE_SCRIPT = PROJECT_ROOT / "search_engine.py"
DB_PATH = PROJECT_ROOT / "Processed_Assets" / "my_rag_data.db"

SUBPROC_KWARGS = dict(capture_output=True, text=True, encoding="utf-8",
                      errors="replace", timeout=600)


def run_cli(*args):
    return subprocess.run([sys.executable, str(SEARCH_ENGINE_SCRIPT), *args], **SUBPROC_KWARGS)


def _ollama_up() -> bool:
    try:
        se._embed_query("ping")
        return True
    except Exception:
        return False


class TestAskHelpers(unittest.TestCase):
    def test_u01_select_passages_caps_and_diversifies(self):
        ranked = [(i, 0.9 - i * 0.01) for i in range(40)]
        doc_map = {i: ("A" if i < 30 else "B") for i in range(40)}
        picked = se._select_passages(ranked, doc_map, max_passages=6,
                                     max_per_doc=se.MAX_PER_DOC)
        self.assertLessEqual(len(picked), 6)
        docs = [doc_map[cid] for cid, _ in picked]
        self.assertLessEqual(max(docs.count(d) for d in set(docs)), se.MAX_PER_DOC)

    def test_u02_prompt_contains_sources_and_rule(self):
        sources = [("Title One", "topic-x", "chunk text one"),
                   ("Title Two", "topic-y", "chunk text two")]
        system, user = se.build_ask_prompt("what is the funnel?", sources)
        prompt = system + "\n" + user
        self.assertIn("[S1]", prompt)
        self.assertIn("[S2]", prompt)
        self.assertIn("chunk text one", prompt)
        self.assertIn("what is the funnel?", prompt)
        self.assertIn("only", prompt.lower())  # grounded-answer instruction

    def test_u03_save_briefing_writes_nonzero_markdown(self):
        import tempfile
        out_dir = Path(tempfile.mkdtemp())
        path = se.save_briefing(
            out_dir, "test question about trading",
            "ANSWER TEXT HERE", [("T", "top", "exc")], model="unit-test-model",
        )
        self.assertTrue(path.exists())
        self.assertGreater(path.stat().st_size, 0)
        content = path.read_text(encoding="utf-8")
        self.assertIn("ANSWER TEXT HERE", content)
        self.assertIn("---", content[:4])  # YAML frontmatter start
        self.assertIn("tags:", content)


def _llm_runnable() -> tuple:
    """(bool, reason): can the default brain answer right now?

    Tries the Groq cloud brain first (the default), then mirrors the
    production local RAM ladder as fallback. Skips only when both fail.
    """
    last_err = None
    try:
        se._groq_chat(se.CLOUD_ALIASES["groq"], "reply OK only.", "ping")
        return True, ""
    except Exception as e:
        last_err = e
    for ctx in (se.ASK_NUM_CTX, 2048, 1024):
        try:
            se._ollama_chat("phi3:mini", "reply OK only.", "ping", num_ctx=ctx)
            return True, ""
        except Exception as e:
            last_err = e
    return False, f"neither cloud nor local brain loadable right now: {last_err}"


@unittest.skipUnless(DB_PATH.exists() and _ollama_up(), "DB or Ollama unavailable")
class TestAskEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ok, reason = _llm_runnable()
        if not ok:
            raise unittest.SkipTest(reason)
    def test_e01_ask_answers_with_sources(self):
        proc = run_cli("What do I have about building an automated stock screening system?",
                       "--mode", "ask")
        self.assertEqual(proc.returncode, 0, proc.stderr[-500:])
        self.assertIn("ANSWER", proc.stdout)
        self.assertIn("SOURCE", proc.stdout.upper())

    def test_e02_ask_respects_topic_filter(self):
        proc = run_cli("how to get clients?", "--mode", "ask",
                       "--topic", "subbroking")
        self.assertEqual(proc.returncode, 0)
        src_section = proc.stdout.split("SOURCE")[-1].lower()
        # at least one cited source belongs to subbroking domain files
        self.assertTrue(any(k in src_section for k in
                        ("subbroking", "client acquisition", "growth engine")),
                        f"no subbroking source cited:\n{src_section[:400]}")

    def test_e03_ask_save_creates_briefing(self):
        import re
        before = set((PROJECT_ROOT / "Briefings").glob("*.md")) if \
            (PROJECT_ROOT / "Briefings").exists() else set()
        proc = run_cli("summarise my n8n assets briefly", "--mode", "ask", "--save")
        self.assertEqual(proc.returncode, 0)
        after = set((PROJECT_ROOT / "Briefings").glob("*.md")) if \
            (PROJECT_ROOT / "Briefings").exists() else set()
        new = after - before
        self.assertEqual(len(new), 1, f"expected exactly one new briefing, got {new}")
        p = new.pop()
        self.assertGreater(p.stat().st_size, 0)

    def test_e04_model_alias_resolution(self):
        self.assertEqual(se.resolve_model_name("groq"), "openai/gpt-oss-120b")
        self.assertEqual(se.resolve_model_name("groq-fast"), "qwen/qwen3.6-27b")
        self.assertEqual(se.resolve_model_name("groq/custom-id"), "custom-id")
        self.assertTrue(se.is_cloud_model("groq"))
        self.assertFalse(se.is_cloud_model("phi3"))
        self.assertEqual(se.resolve_model_name("llama"), "llama3.2")
        self.assertEqual(se.resolve_model_name("mistral").startswith("mistral"), True)
        with self.assertRaises(SystemExit):
            se.resolve_model_name("not-a-real-model-zz")


if __name__ == "__main__":
    unittest.main()
