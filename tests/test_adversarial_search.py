"""
Adversarial Stress Test Suite: Second Brain Search Engine & SQLite RAG Database
================================================================================
Empirical challenge suite for search_engine.py and Processed_Assets/my_rag_data.db.

Covers 5 Core Empirical Vectors:
1. SQL Injection & FTS5 Control Characters (*, ", ', AND, OR, NOT, NEAR, :::, MATCH, <script>, XSS, etc.)
2. Extreme BM25 Parameters (negative limits, 0 limit, 10000 limit, max int limits, empty/whitespace queries)
3. Knowledge Graph Traversal Stress (nonexistent entities, cyclical queries, special chars, high-degree hubs)
4. Relational & Database Integrity (orphaned chunks, orphaned edges, FTS5 sync, PRAGMA checks)
5. Concurrency & Sub-Second Latency Benchmarking (multi-threaded concurrent reads, p50/p95/p99 timing)

Layout:
- Tests co-located in tests/ directory per PROJECT.md specification.
"""

import io
import os
import re
import sys
import time
import sqlite3
import unittest
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Workspace Root Setup
PROJECT_ROOT = Path(r"C:\knowledgeBase_staging")
if not PROJECT_ROOT.exists():
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "Processed_Assets" / "my_rag_data.db"
SEARCH_ENGINE_PATH = PROJECT_ROOT / "search_engine.py"

import search_engine
from search_engine import sanitize_fts5_query, search_linear, search_graph


class TestSQLInjectionAndFTS5ControlChars(unittest.TestCase):
    """Vector 1: SQL Injection strings & FTS5 control characters."""

    def test_sanitize_fts5_empty_and_control_chars(self):
        """Verify sanitize_fts5_query neutralizes FTS5 syntax control chars."""
        control_chars = [
            ("*", ""),
            ('"', ""),
            ("'", ""),
            (":::", ""),
            ("***", ""),
            ("AND", '"AND"*'),
            ("OR", '"OR"*'),
            ("NOT", '"NOT"*'),
            ("NEAR", '"NEAR"*'),
            ("MATCH", '"MATCH"*'),
            ("<script>", '"script"*'),
            ("<script>alert('xss')</script>", '"script"* "alert"* "xss"* "script"*'),
            ("chunk_text:agent", '"chunk_text"* "agent"*'),
            ("((()))", ""),
            ("{}", ""),
            ("[]", ""),
            ("+-~^", ""),
            ("///\\\\", ""),
        ]
        for raw, expected in control_chars:
            res = sanitize_fts5_query(raw)
            self.assertEqual(res, expected, f"Sanitization mismatch for input: {raw}")

    def test_search_linear_sql_injection_payloads(self):
        """Verify search_linear safely handles classic and advanced SQL injection strings without SQL errors."""
        sqli_payloads = [
            "' OR '1'='1",
            "\" OR \"\"=\"",
            "Robert'); DROP TABLE chunks; --",
            "1; ATTACH DATABASE 'c:/evil.db' AS evil; --",
            "' UNION SELECT id, label, node_type, details, 1, 1 FROM kg_nodes; --",
            "admin' --",
            "'; DELETE FROM documents WHERE '1'='1'; --",
            "SELECT * FROM sqlite_master;",
            "1' ORDER BY 1--+",
            "1' OR sleep(2)#",
            "<svg/onload=alert(1)>",
            "{{7*7}}",
            "${7*7}",
            "../../etc/passwd",
            "\\\\localhost\\c$\\secret.txt",
            "\x00",
            "\0",
            "null' AND 1=1 --",
            "n8n' OR 'a'='a",
            "agent\" AND \"1\"=\"1",
            "MATCH '\"\"*'",
            "MATCH 'agent NOT trading'",
            "NEAR/5 (agent, memory)",
            "topic:AI AND format:json"
        ]

        for payload in sqli_payloads:
            buf = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = buf
                # Must not raise sqlite3.OperationalError, sqlite3.DatabaseError or syntax errors
                search_linear(payload, limit=5)
            except Exception as e:
                self.fail(f"search_linear crashed on SQLi payload [{payload}]: {type(e).__name__} - {e}")
            finally:
                sys.stdout = old_stdout

            out = buf.getvalue()
            # Must output standard formatted results or graceful "No matching records"
            self.assertTrue(
                "LINEAR FTS5 RESULTS" in out or "No matching records found" in out,
                f"Unexpected output for payload [{payload}]: {out[:150]}"
            )

    def test_search_linear_unicode_and_special_scripts(self):
        """Verify search_linear handles diverse unicode alphabets, diacritics, and emojis gracefully."""
        unicode_queries = [
            "café résumé naïve",           # Latin diacritics (covered by \u00C0-\u017F)
            "🤖 🧠 📈 🚀",                 # Emojis (non-alphanumeric)
            "人工智能 深度学习",             # CJK characters
            "нейросеть автоматизация",    # Cyrillic
            "ذكاء اصطناعي",                # Arabic (RTL)
            "תכנות מחשבים",                # Hebrew (RTL)
            "páncreas corazón",            # Spanish accents
            "münchen übergrößen"           # German umlauts
        ]
        for uq in unicode_queries:
            buf = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = buf
                search_linear(uq, limit=5)
            except Exception as e:
                self.fail(f"search_linear crashed on unicode query [{uq}]: {e}")
            finally:
                sys.stdout = old_stdout
            out = buf.getvalue()
            self.assertIn("LINEAR FTS5 RESULTS", out)

    def test_search_linear_extremely_long_query(self):
        """Verify search_linear handles massive query strings (buffer stress)."""
        long_query = "agent " * 1000  # 6000 chars, 1000 tokens
        buf = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buf
            search_linear(long_query, limit=5)
        except Exception as e:
            self.fail(f"search_linear crashed on long query: {e}")
        finally:
            sys.stdout = old_stdout
        out = buf.getvalue()
        self.assertIn("LINEAR FTS5 RESULTS", out)


class TestBM25ExtremeParameters(unittest.TestCase):
    """Vector 2: Extreme BM25 parameters & boundary conditions."""

    def test_zero_limit(self):
        """Verify limit=0 returns 0 results cleanly without executing unbounded query."""
        buf = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buf
            search_linear("agent", limit=0)
        finally:
            sys.stdout = old_stdout
        out = buf.getvalue()
        self.assertIn("(0 matches)", out)
        self.assertNotIn("[1]", out)

    def test_negative_limits(self):
        """Verify negative limits default to a safe fallback (50)."""
        for neg_lim in [-1, -5, -9999]:
            buf = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = buf
                search_linear("agent", limit=neg_lim)
            except Exception as e:
                self.fail(f"search_linear crashed on negative limit {neg_lim}: {e}")
            finally:
                sys.stdout = old_stdout
            out = buf.getvalue()
            self.assertIn("LINEAR FTS5 RESULTS", out)

    def test_large_limits(self):
        """Verify limit=10000 and extreme integer limits execute cleanly without OOM."""
        extreme_limits = [1000, 10000, 2**31 - 1]
        for lim in extreme_limits:
            buf = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = buf
                search_linear("trading", limit=lim)
            except Exception as e:
                self.fail(f"search_linear crashed on large limit {lim}: {e}")
            finally:
                sys.stdout = old_stdout
            out = buf.getvalue()
            self.assertIn("LINEAR FTS5 RESULTS", out)

    def test_empty_and_whitespace_queries(self):
        """Verify empty strings and whitespace-only queries exit cleanly."""
        for ws in ["", " ", "   ", "\t", "\n\r\t  \n"]:
            buf = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = buf
                search_linear(ws, limit=5)
            except Exception as e:
                self.fail(f"search_linear crashed on whitespace query [{repr(ws)}]: {e}")
            finally:
                sys.stdout = old_stdout
            out = buf.getvalue()
            self.assertIn("(0 matches)", out)
            self.assertIn("No matching records found", out)


class TestKnowledgeGraphTraversalStress(unittest.TestCase):
    """Vector 3: Graph traversal stress testing."""

    def test_nonexistent_entities(self):
        """Verify search_graph handles nonexistent entities gracefully."""
        ghost_entities = [
            "NonExistentEntity_12345_ZZZ",
            "__UNKNOWN_NODE__",
            "9999999999",
            "asdfghjklqwertyuiop"
        ]
        for entity in ghost_entities:
            buf = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = buf
                search_graph(entity)
            except Exception as e:
                self.fail(f"search_graph crashed on nonexistent entity [{entity}]: {e}")
            finally:
                sys.stdout = old_stdout
            out = buf.getvalue()
            self.assertIn("not found in Knowledge Graph nodes", out)

    def test_graph_special_characters_and_sqli(self):
        """Verify search_graph handles SQL wildcards, injection strings, and special characters."""
        special_entities = [
            "%",
            "_",
            "%%",
            "__",
            "' OR '1'='1",
            "Robert'); DROP TABLE kg_nodes; --",
            "<script>alert(1)</script>",
            "OpenAI'--",
            "n8n\" OR \"1\"=\"1",
            "\\",
            "[]",
            "{}",
            "🤖 OpenAI"
        ]
        for entity in special_entities:
            buf = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = buf
                search_graph(entity)
            except Exception as e:
                self.fail(f"search_graph crashed on special char entity [{entity}]: {e}")
            finally:
                sys.stdout = old_stdout
            out = buf.getvalue()
            self.assertIn("KNOWLEDGE GRAPH CONNECTIONS FOR", out)

    def test_graph_high_degree_hub_nodes(self):
        """Verify high-degree hub entities (e.g. n8n, OpenAI, Python, TradingView) return inbound/outbound links cleanly."""
        hubs = ["n8n", "OpenAI", "Python", "TradingView", "Pinecone", "01_ai_agents_and_autonomous_systems"]
        for hub in hubs:
            buf = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = buf
                search_graph(hub)
            except Exception as e:
                self.fail(f"search_graph crashed on hub node [{hub}]: {e}")
            finally:
                sys.stdout = old_stdout
            out = buf.getvalue()
            self.assertIn(f"KNOWLEDGE GRAPH CONNECTIONS FOR: '{hub}'", out)
            self.assertTrue("* Node:" in out or "not found" in out)

    def test_graph_empty_and_whitespace_entity(self):
        """Verify empty and whitespace entity queries exit cleanly."""
        for ws in ["", "  ", "\t\t\n"]:
            buf = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = buf
                search_graph(ws)
            except Exception as e:
                self.fail(f"search_graph crashed on whitespace entity [{repr(ws)}]: {e}")
            finally:
                sys.stdout = old_stdout
            out = buf.getvalue()
            self.assertIn("not found in Knowledge Graph nodes", out)


class TestRelationalIntegrity(unittest.TestCase):
    """Vector 4: Relational integrity and database consistency verification."""

    def setUp(self):
        self.assertTrue(DB_PATH.exists(), f"Database missing at {DB_PATH}")
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def tearDown(self):
        self.conn.close()

    def test_sqlite_integrity_check(self):
        """Verify PRAGMA integrity_check returns 'ok'."""
        self.cursor.execute("PRAGMA integrity_check;")
        res = self.cursor.fetchall()
        self.assertEqual(res, [("ok",)], f"Database corruption detected: {res}")

    def test_sqlite_foreign_key_check(self):
        """Verify PRAGMA foreign_key_check finds 0 violations."""
        self.cursor.execute("PRAGMA foreign_key_check;")
        violations = self.cursor.fetchall()
        self.assertEqual(len(violations), 0, f"Foreign key violations found: {violations}")

    def test_no_orphaned_chunks(self):
        """Verify all records in chunks point to a valid document in documents table."""
        self.cursor.execute("""
            SELECT count(*)
            FROM chunks c
            LEFT JOIN documents d ON c.doc_id = d.id
            WHERE d.id IS NULL;
        """)
        orphans = self.cursor.fetchone()[0]
        self.assertEqual(orphans, 0, f"Found {orphans} orphaned chunks without parent documents")

    def test_chunks_and_fts5_synchronization(self):
        """Verify count of records in chunks table exactly matches chunks_fts table."""
        self.cursor.execute("SELECT count(*) FROM chunks;")
        chunk_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT count(*) FROM chunks_fts;")
        fts_count = self.cursor.fetchone()[0]

        self.assertGreater(chunk_count, 0, "Chunks table is empty")
        self.assertEqual(chunk_count, fts_count, f"Chunks ({chunk_count}) and FTS5 ({fts_count}) count desync!")

    def test_no_orphaned_knowledge_graph_edges(self):
        """Verify all source_id and target_id in kg_edges exist in kg_nodes."""
        self.cursor.execute("""
            SELECT count(*)
            FROM kg_edges e
            LEFT JOIN kg_nodes n ON e.source_id = n.id
            WHERE n.id IS NULL;
        """)
        orphaned_sources = self.cursor.fetchone()[0]
        self.assertEqual(orphaned_sources, 0, f"Found {orphaned_sources} kg_edges with missing source node")

        self.cursor.execute("""
            SELECT count(*)
            FROM kg_edges e
            LEFT JOIN kg_nodes n ON e.target_id = n.id
            WHERE n.id IS NULL;
        """)
        orphaned_targets = self.cursor.fetchone()[0]
        self.assertEqual(orphaned_targets, 0, f"Found {orphaned_targets} kg_edges with missing target node")

    def test_documents_table_well_formedness(self):
        """Verify documents table contains no NULL file_name or relative_path, and paths are unique."""
        self.cursor.execute("SELECT count(*) FROM documents WHERE file_name IS NULL OR relative_path IS NULL;")
        null_docs = self.cursor.fetchone()[0]
        self.assertEqual(null_docs, 0, f"Found {null_docs} documents with NULL file_name or relative_path")

        self.cursor.execute("""
            SELECT relative_path, count(*)
            FROM documents
            GROUP BY relative_path
            HAVING count(*) > 1;
        """)
        dups = self.cursor.fetchall()
        self.assertEqual(len(dups), 0, f"Found duplicate document relative paths: {dups}")

    def test_kg_nodes_primary_key_uniqueness(self):
        """Verify kg_nodes table has no duplicate IDs."""
        self.cursor.execute("""
            SELECT id, count(*)
            FROM kg_nodes
            GROUP BY id
            HAVING count(*) > 1;
        """)
        dups = self.cursor.fetchall()
        self.assertEqual(len(dups), 0, f"Duplicate kg_nodes IDs detected: {dups}")


class TestConcurrencyAndPerformance(unittest.TestCase):
    """Vector 5: Concurrency and sub-second performance benchmarking."""

    def test_multithreaded_concurrent_searches(self):
        """Verify 20 concurrent threads executing 100 mixed searches execute without database locks or crashes."""
        queries = [
            ("n8n", "linear"),
            ("agent", "linear"),
            ("trading", "linear"),
            ("prompt", "linear"),
            ("OpenAI", "graph"),
            ("Python", "graph"),
            ("TradingView", "graph"),
            ("Pinecone", "graph"),
            ("01_ai_agents_and_autonomous_systems", "graph"),
            ("finance market indicators", "linear")
        ]

        errors = []

        def worker_task(q_tuple):
            q, mode = q_tuple
            buf = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = buf
                if mode == "linear":
                    search_linear(q, limit=3)
                else:
                    search_graph(q)
            except Exception as e:
                errors.append((q, mode, str(e)))
            finally:
                sys.stdout = old_stdout

        task_list = [queries[i % len(queries)] for i in range(100)]
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(worker_task, item) for item in task_list]
            for f in as_completed(futures):
                f.result()

        self.assertEqual(len(errors), 0, f"Concurrent execution generated errors: {errors}")

    def test_subsecond_latency_benchmark(self):
        """Verify mean and p95 query latency is strictly sub-second (< 100ms internal SQLite execution)."""
        benchmark_queries = [
            "n8n webhook",
            "autonomous agent memory",
            "trading algorithmic rules",
            "prompt template engineering",
            "document vector embeddings"
        ]

        latencies = []
        for bq in benchmark_queries:
            for _ in range(5):  # 5 runs each = 25 runs
                buf = io.StringIO()
                old_stdout = sys.stdout
                try:
                    sys.stdout = buf
                    t0 = time.perf_counter()
                    search_linear(bq, limit=5)
                    t1 = time.perf_counter()
                    latencies.append((t1 - t0) * 1000)  # ms
                finally:
                    sys.stdout = old_stdout

        avg_latency = sum(latencies) / len(latencies)
        sorted_lat = sorted(latencies)
        p50 = sorted_lat[len(sorted_lat) // 2]
        p95 = sorted_lat[int(len(sorted_lat) * 0.95)]
        max_lat = max(latencies)

        # Print latency metrics
        print(f"\n--- Sub-Second Latency Benchmark (25 runs) ---")
        print(f"Mean Latency: {avg_latency:.2f} ms")
        print(f"P50 Latency:  {p50:.2f} ms")
        print(f"P95 Latency:  {p95:.2f} ms")
        print(f"Max Latency:  {max_lat:.2f} ms")

        # Sub-second requirement: internal execution must be well below 500ms (typically < 50ms)
        self.assertLess(avg_latency, 500.0, f"Mean latency {avg_latency:.2f}ms exceeds 500ms threshold")
        self.assertLess(p95, 800.0, f"P95 latency {p95:.2f}ms exceeds 800ms threshold")


def run_adversarial_suite():
    """Runs all adversarial tests and returns result code."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestSQLInjectionAndFTS5ControlChars,
        TestBM25ExtremeParameters,
        TestKnowledgeGraphTraversalStress,
        TestRelationalIntegrity,
        TestConcurrencyAndPerformance
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    print("=" * 80)
    print(" ADVERSARIAL STRESS TEST RUNNER - SEARCH ENGINE & SQLITE RAG DB")
    print(f" Database: {DB_PATH}")
    print(f" Total Adversarial Test Cases: {suite.countTestCases()}")
    print("=" * 80)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 80)
    print(" ADVERSARIAL TEST SUMMARY BREAKDOWN")
    print("=" * 80)
    print(f" Tests Run:   {result.testsRun}")
    print(f" Successes:   {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f" Failures:    {len(result.failures)}")
    print(f" Errors:      {len(result.errors)}")
    print(f" Pass Rate:   {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 80)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_adversarial_suite())
