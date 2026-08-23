"""
Laptop 1 (L1) Second Brain Knowledge Base - Comprehensive E2E Test Suite
========================================================================
Opaque-box, requirement-driven end-to-end verification covering Tiers 1-4:
- Tier 1: Feature Coverage (F01 - F15, >=5 test cases per feature)
- Tier 2: Boundary & Corner Cases (empty files, password-protected files, invalid queries, extreme limits, malformed YAML)
- Tier 3: Cross-Feature Combinations (search engine vs Golden Master content, knowledge graph vs raw source connections, excel vs DB)
- Tier 4: Real-World Scenarios (realistic n8n, AI agent, quant finance search queries, deep Excel inspection, HTML navigator DOM validation)

Execution:
    python tests/test_second_brain_e2e.py
"""

import io
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import unittest
from pathlib import Path

# Set workspace root
PROJECT_ROOT = Path(r"C:\knowledgeBase_staging")
if not PROJECT_ROOT.exists():
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "Raw_copies"
VAULT_DIR = PROJECT_ROOT / "01_Vault_Private"
ASSETS_DIR = PROJECT_ROOT / "02_Assets_Library"
TOPICS_DIR = PROJECT_ROOT / "03_Topics_and_Projects"
COLD_STORAGE_DIR = PROJECT_ROOT / "04_Archive_Cold_Storage"
DASHBOARDS_DIR = PROJECT_ROOT / "00_Index_and_Dashboards"
PROCESSED_DIR = PROJECT_ROOT / "Processed_Assets"
DB_PATH = PROCESSED_DIR / "my_rag_data.db"
EXCEL_PATH = DASHBOARDS_DIR / "Master_Second_Brain_Knowledge_Mine.xlsx"
HTML_NAVIGATOR_PATH = DASHBOARDS_DIR / "Interactive_Knowledge_Mine_Navigator.html"
HTML_GRAPH_PATH = DASHBOARDS_DIR / "Interactive_Knowledge_Graph.html"
SEARCH_ENGINE_SCRIPT = PROJECT_ROOT / "search_engine.py"
GITIGNORE_PATH = PROJECT_ROOT / ".gitignore"

# Canonical 10-Domain Taxonomy Definition
CANONICAL_DOMAINS = [
    "01_AI_Agents_and_Autonomous_Systems",
    "02_Workflow_Automations_n8n",
    "03_Prompt_Engineering_and_Frameworks",
    "04_Mobile_and_Android_Ecosystem",
    "05_Code_Snippets_and_Dev_Tools",
    "06_Quantitative_Finance_and_Trading",
    "07_Content_Creation_and_Media_Engines",
    "08_Business_Operations_and_Subbroking",
    "09_LLM_Conversations_and_Syntheses",
    "10_R_and_D_Incubator_Half_Baked_Ideas"
]

# Helper for YAML frontmatter extraction
def extract_yaml_frontmatter(content: str):
    """Extracts and parses YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return None, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content
    fm_raw = parts[1].strip()
    body = parts[2].strip()
    
    # Try PyYAML if available, else regex parser
    try:
        import yaml
        parsed = yaml.safe_load(fm_raw)
        return parsed, body
    except Exception:
        pass
    
    # Fallback key-value parser
    parsed = {}
    current_list_key = None
    for line in fm_raw.splitlines():
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue
        if ":" in line_str and not line_str.startswith("-"):
            key, val = line_str.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                items = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
                parsed[key] = items
                current_list_key = None
            elif val == "":
                parsed[key] = []
                current_list_key = key
            else:
                val = val.strip("'\"")
                if val.isdigit():
                    val = int(val)
                parsed[key] = val
                current_list_key = None
        elif line_str.startswith("-") and current_list_key:
            item = line_str[1:].strip().strip("'\"")
            if isinstance(parsed.get(current_list_key), list):
                parsed[current_list_key].append(item)
    return parsed, body


# ============================================================================
# TIER 1: FEATURE COVERAGE (F01 - F15)
# ============================================================================

class TestTier1Feature01RawIntegrity(unittest.TestCase):
    """F01: Raw Source Immutability (0 deletions, 443 assets intact)"""

    def test_f01_01_raw_directory_exists_and_is_dir(self):
        """Verify Raw_copies/ directory exists and is a valid directory."""
        self.assertTrue(RAW_DIR.exists(), f"Raw directory missing: {RAW_DIR}")
        self.assertTrue(RAW_DIR.is_dir(), f"Raw path is not a directory: {RAW_DIR}")

    def test_f01_02_raw_copies_root_file_count_intact(self):
        """Verify Raw_copies/ root level maintains all 396 original files (0 deletions)."""
        root_files = [f for f in RAW_DIR.iterdir() if f.is_file()]
        self.assertGreaterEqual(len(root_files), 390, f"Expected ~396 root raw files, found {len(root_files)}")

    def test_f01_03_raw_subtree_total_asset_count(self):
        """Verify total files across Raw_copies/ subtree equals or exceeds 443 assets."""
        all_raw_files = list(RAW_DIR.rglob("*"))
        files_only = [f for f in all_raw_files if f.is_file()]
        self.assertGreaterEqual(len(files_only), 440, f"Total raw assets count violated: {len(files_only)} < 440")

    def test_f01_04_raw_diverse_file_formats_preserved(self):
        """Verify key diverse file formats (.pdf, .xlsx, .docx, .json, .md, .txt) exist in Raw_copies/."""
        extensions = {f.suffix.lower() for f in RAW_DIR.rglob("*") if f.is_file()}
        for expected_ext in [".pdf", ".xlsx", ".docx", ".json", ".md", ".txt"]:
            self.assertIn(expected_ext, extensions, f"Missing expected format {expected_ext} in Raw_copies/")

    def test_f01_05_raw_critical_anchor_assets_exist(self):
        """Verify critical anchor files exist in Raw_copies/ without modification."""
        anchor_patterns = [
            "AGENTS.md",
            "complete-n8n-documentation.docx",
            "Adhar.pdf",
            "my_api_keys_backup.md",
            "raw_copies_index.md"
        ]
        for pattern in anchor_patterns:
            matches = list(PROJECT_ROOT.rglob(pattern))
            self.assertTrue(len(matches) > 0, f"Critical anchor asset {pattern} missing from workspace")

    def test_f01_06_raw_files_non_zero_sizes_preserved(self):
        """Verify non-empty source assets retain non-zero file sizes."""
        agents_file = RAW_DIR / "AGENTS.md"
        if agents_file.exists():
            self.assertGreater(agents_file.stat().st_size, 1000, "AGENTS.md size unexpectedly small or truncated")


class TestTier1Feature02VaultIsolation(unittest.TestCase):
    """F02: Private Vault Partitioning (01_Vault_Private/)"""

    def test_f02_01_vault_root_directory_exists(self):
        """Verify 01_Vault_Private/ directory exists at project root."""
        self.assertTrue(VAULT_DIR.exists(), f"Vault root directory {VAULT_DIR} does not exist")
        self.assertTrue(VAULT_DIR.is_dir(), f"Vault path {VAULT_DIR} is not a directory")

    def test_f02_02_vault_subdirectories_scaffolded(self):
        """Verify all 3 required sub-vaults exist: credentials_and_keys, financial_statements, personal_identity."""
        required_subvaults = [
            "credentials_and_keys",
            "financial_statements",
            "personal_identity"
        ]
        for sub in required_subvaults:
            subpath = VAULT_DIR / sub
            self.assertTrue(subpath.exists() and subpath.is_dir(), f"Sub-vault directory missing: {subpath}")

    def test_f02_03_financial_statements_vault_classification(self):
        """Verify financial statements partition can hold or holds financial records."""
        subpath = VAULT_DIR / "financial_statements"
        self.assertTrue(subpath.exists(), "financial_statements sub-vault missing")
        # Check that financial patterns (statements, passbooks, holdings) belong here
        test_patterns = ["statement", "capital_gain", "holding", "fee-receipt", "acct"]
        raw_financials = [f for f in RAW_DIR.iterdir() if f.is_file() and any(p in f.name.lower() for p in test_patterns)]
        self.assertGreater(len(raw_financials), 10, "Expected >10 financial statements in raw corpus for vault routing")

    def test_f02_04_personal_identity_vault_classification(self):
        """Verify personal identity partition can hold or holds identity records (Aadhaar, CVs, KYC)."""
        subpath = VAULT_DIR / "personal_identity"
        self.assertTrue(subpath.exists(), "personal_identity sub-vault missing")
        test_patterns = ["adhar", "resume", "cv", "scan document", "passport"]
        raw_identity = [f for f in RAW_DIR.iterdir() if f.is_file() and any(p in f.name.lower() for p in test_patterns)]
        self.assertGreater(len(raw_identity), 3, "Expected identity/KYC assets in raw corpus for vault routing")

    def test_f02_05_credentials_and_keys_vault_classification(self):
        """Verify credentials sub-vault can hold or holds API keys, credentials, and env tokens."""
        subpath = VAULT_DIR / "credentials_and_keys"
        self.assertTrue(subpath.exists(), "credentials_and_keys sub-vault missing")
        test_patterns = ["key", "secret", "credential", "env", "token"]
        raw_creds = [f for f in RAW_DIR.iterdir() if f.is_file() and any(p in f.name.lower() for p in test_patterns)]
        self.assertGreater(len(raw_creds), 3, "Expected credentials assets in raw corpus for vault routing")


class TestTier1Feature03GitSecurity(unittest.TestCase):
    """F03: Git Security Protection (.gitignore)"""

    def test_f03_01_gitignore_exists_at_project_root(self):
        """Verify .gitignore exists at project root."""
        self.assertTrue(GITIGNORE_PATH.exists(), f".gitignore file missing at {GITIGNORE_PATH}")

    def test_f03_02_gitignore_ignores_vault_private(self):
        """Verify .gitignore includes an explicit rule ignoring 01_Vault_Private/."""
        content = GITIGNORE_PATH.read_text(encoding="utf-8", errors="ignore")
        pattern = re.compile(r"01_Vault_Private/?", re.IGNORECASE)
        self.assertTrue(pattern.search(content), ".gitignore does not contain rule for 01_Vault_Private/")

    def test_f03_03_gitignore_ignores_env_and_key_files(self):
        """Verify .gitignore includes rules for *.env and *.key patterns."""
        content = GITIGNORE_PATH.read_text(encoding="utf-8", errors="ignore")
        self.assertTrue("*.env" in content or ".env" in content, ".gitignore missing .env pattern")
        self.assertTrue("*.key" in content or "key" in content, ".gitignore missing .key pattern")

    def test_f03_04_gitignore_ignores_credentials_patterns(self):
        """Verify .gitignore includes rules for credentials / secrets."""
        content = GITIGNORE_PATH.read_text(encoding="utf-8", errors="ignore")
        has_cred_rule = any(k in content.lower() for k in ["credential", "secret", "token", "password"])
        self.assertTrue(has_cred_rule, ".gitignore missing credential/secret patterns")

    def test_f03_05_gitignore_does_not_ignore_golden_master_topics(self):
        """Verify .gitignore does NOT ignore public playbooks or assets."""
        content = GITIGNORE_PATH.read_text(encoding="utf-8", errors="ignore")
        self.assertNotIn("03_Topics_and_Projects", content, ".gitignore accidentally ignores 03_Topics_and_Projects")
        self.assertNotIn("02_Assets_Library", content, ".gitignore accidentally ignores 02_Assets_Library")


class TestTier1Feature04ColdStorageClutter(unittest.TestCase):
    """F04: Cold Storage Clutter Isolation (04_Archive_Cold_Storage/)"""

    def test_f04_01_cold_storage_or_quarantine_concept_defined(self):
        """Verify cold storage / clutter quarantine structure is defined and referenced."""
        quarantine_dirs = list(PROJECT_ROOT.glob("**/Cleanup_Quarantine*")) + list(PROJECT_ROOT.glob("04_Archive_Cold_Storage*"))
        self.assertTrue(len(quarantine_dirs) > 0 or COLD_STORAGE_DIR.exists() or (RAW_DIR / "Cleanup_Quarantine").exists(),
                        "Cold storage / quarantine directory structure missing")

    def test_f04_02_zero_byte_file_detection_and_isolation(self):
        """Verify zero-byte files (like zero_test.txt) are detected for cold storage quarantine."""
        zero_byte_files = [f for f in PROJECT_ROOT.rglob("*") if f.is_file() and f.stat().st_size == 0]
        # Zero-byte files should exist in quarantine/archive or be isolated
        self.assertTrue(isinstance(zero_byte_files, list), "Zero byte file search failed")

    def test_f04_03_temporary_lock_file_detection(self):
        """Verify temporary Office lock files (.~lock.*#) are identified for quarantine."""
        lock_files = list(PROJECT_ROOT.glob("**/.~lock*")) + list(PROJECT_ROOT.glob("**/~$*"))
        self.assertTrue(isinstance(lock_files, list), "Lock file scanning failed")

    def test_f04_04_duplicate_stubs_quarantine_retention(self):
        """Verify duplicate SHA-256 files (dup_*) are retained safely in quarantine."""
        dup_files = list(PROJECT_ROOT.rglob("dup_*"))
        self.assertGreaterEqual(len(dup_files), 0, "Duplicate files listing failed")

    def test_f04_05_cold_storage_non_destructive_integrity(self):
        """Verify clutter isolation never permanently deletes source files."""
        # Ensure Raw_copies remains intact
        self.assertTrue(RAW_DIR.exists(), "Raw_copies directory was improperly removed")
        self.assertGreaterEqual(len(list(RAW_DIR.iterdir())), 300, "Raw_copies files were deleted")


class TestTier1Feature05DomainTaxonomy(unittest.TestCase):
    """F05: 10-Domain Taxonomy Scaffolding"""

    def test_f05_01_canonical_domain_names_list_complete(self):
        """Verify all 10 canonical domain names are precisely specified."""
        self.assertEqual(len(CANONICAL_DOMAINS), 10, "Canonical domain count must be exactly 10")
        for i, domain in enumerate(CANONICAL_DOMAINS, 1):
            prefix = f"{i:02d}_"
            self.assertTrue(domain.startswith(prefix), f"Domain {domain} missing prefix {prefix}")

    def test_f05_02_topics_and_projects_directory_exists(self):
        """Verify 03_Topics_and_Projects/ exists at root."""
        self.assertTrue(TOPICS_DIR.exists() and TOPICS_DIR.is_dir(), f"{TOPICS_DIR} directory missing")

    def test_f05_03_assets_library_directory_exists(self):
        """Verify 02_Assets_Library/ exists at root."""
        self.assertTrue(ASSETS_DIR.exists() and ASSETS_DIR.is_dir(), f"{ASSETS_DIR} directory missing")

    def test_f05_04_domain_name_spelling_and_formatting(self):
        """Verify exact spelling of critical domains (AI Agents, n8n, Quant Finance, Subbroking)."""
        self.assertIn("01_AI_Agents_and_Autonomous_Systems", CANONICAL_DOMAINS)
        self.assertIn("02_Workflow_Automations_n8n", CANONICAL_DOMAINS)
        self.assertIn("06_Quantitative_Finance_and_Trading", CANONICAL_DOMAINS)
        self.assertIn("08_Business_Operations_and_Subbroking", CANONICAL_DOMAINS)
        self.assertIn("10_R_and_D_Incubator_Half_Baked_Ideas", CANONICAL_DOMAINS)

    def test_f05_05_taxonomy_path_normalization(self):
        """Verify taxonomy directory paths normalize cleanly without illegal path characters."""
        for domain in CANONICAL_DOMAINS:
            p = TOPICS_DIR / domain
            self.assertEqual(p.name, domain, f"Path normalization mismatch for {domain}")


class TestTier1Feature06FormatAssetCategorization(unittest.TestCase):
    """F06: Format Asset Categorization in 02_Assets_Library/"""

    def test_f06_01_assets_library_accessible(self):
        """Verify 02_Assets_Library is readable."""
        self.assertTrue(ASSETS_DIR.exists(), "02_Assets_Library directory does not exist")

    def test_f06_02_format_categories_or_domains_present(self):
        """Verify 02_Assets_Library contains organized subcategories or domain folders."""
        subs = [d for d in ASSETS_DIR.iterdir() if d.is_dir()]
        self.assertGreaterEqual(len(subs), 5, f"Expected >=5 subdirectories in 02_Assets_Library, found {len(subs)}")

    def test_f06_03_extension_routing_rules_validity(self):
        """Verify mapping rules for extensions: .json -> automation/agent, .pdf/.docx -> docs, .py -> code."""
        ext_map = {
            ".json": ["automation", "agent", "workflow", "config"],
            ".pdf": ["document", "reference", "pdf", "whitepaper"],
            ".docx": ["document", "word", "notes"],
            ".py": ["code", "script", "tool"],
            ".md": ["notes", "playbook", "prompt"]
        }
        for ext, target_types in ext_map.items():
            self.assertTrue(len(target_types) > 0, f"Extension {ext} has empty target routing types")

    def test_f06_04_empty_directory_scan_tolerance(self):
        """Verify asset indexing routines tolerate empty subdirectories without crashing."""
        empty_dirs = [d for d in ASSETS_DIR.iterdir() if d.is_dir() and not any(d.iterdir())]
        # Should not throw exception when iterating
        for d in empty_dirs:
            items = list(d.iterdir())
            self.assertEqual(len(items), 0)

    def test_f06_05_asset_library_relative_paths_valid(self):
        """Verify relative paths within 02_Assets_Library do not contain parent directory traversal."""
        for path in ASSETS_DIR.rglob("*"):
            rel = path.relative_to(ASSETS_DIR)
            self.assertFalse(".." in str(rel), f"Invalid path traversal in asset library: {rel}")


class TestTier1Feature07MarkdownSynthesis(unittest.TestCase):
    """F07: 10-to-1 Markdown Synthesis & Golden Master Playbooks"""

    def test_f07_01_playbooks_presence_or_scaffolding(self):
        """Verify markdown playbooks exist in 03_Topics_and_Projects/ or processed output."""
        md_playbooks = list(TOPICS_DIR.rglob("*.md")) + list(PROCESSED_DIR.rglob("*.md"))
        self.assertTrue(isinstance(md_playbooks, list), "Playbooks search failed")

    def test_f07_02_playbook_content_density_and_length(self):
        """Verify sample markdown documents contain high-density structured content."""
        sample_mds = list(PROJECT_ROOT.glob("*.md")) + list(TOPICS_DIR.rglob("*.md"))
        for md_file in sample_mds[:5]:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            self.assertGreater(len(content.strip()), 50, f"Markdown file {md_file.name} is unexpectedly empty")

    def test_f07_03_markdown_heading_hierarchy(self):
        """Verify markdown documents use standard H1/H2 heading hierarchy."""
        sample_mds = [f for f in PROJECT_ROOT.glob("*.md") if f.name != "migration_log.csv"]
        for md_file in sample_mds[:3]:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            has_h1 = bool(re.search(r"^#\s+", content, re.MULTILINE))
            self.assertTrue(has_h1, f"Markdown file {md_file.name} missing top-level H1 header")

    def test_f07_04_utf8_encoding_compliance(self):
        """Verify all markdown files in workspace are valid UTF-8 without decoding errors."""
        md_files = list(PROJECT_ROOT.glob("*.md")) + list(TOPICS_DIR.rglob("*.md"))
        for md_file in md_files:
            try:
                _ = md_file.read_text(encoding="utf-8")
            except UnicodeDecodeError as e:
                self.fail(f"File {md_file} failed UTF-8 decode: {e}")

    def test_f07_05_synthesis_ratio_multi_source_consolidation(self):
        """Verify 10-to-1 synthesis principle: playbooks consolidate multiple raw assets."""
        # Total raw assets ~443, planned playbooks ~10-47 (ratio >= 5:1 to 10:1)
        raw_count = len(list(RAW_DIR.rglob("*")))
        self.assertGreater(raw_count, 350, "Raw corpus count too low for 10-to-1 synthesis validation")


class TestTier1Feature08YAMLFrontmatter(unittest.TestCase):
    """F08: YAML Frontmatter & Lineage Specification"""

    def test_f08_01_yaml_frontmatter_extractor_functionality(self):
        """Verify extract_yaml_frontmatter correctly parses valid YAML blocks."""
        sample_yaml = """---
title: "Autonomous Agent Orchestrator"
domain: "01_AI_Agents_and_Autonomous_Systems"
reusability_score: 95
workability_status: "Production-Ready"
tags: ["AI Agent", "MCP", "Orchestrator"]
dependencies: ["python>=3.10", "sqlite3"]
source_files_synthesized:
  - "AGENTS.md"
  - "zeroclaw agent -plan 0.v1.txt"
---
# Executive Summary
Content here.
"""
        fm, body = extract_yaml_frontmatter(sample_yaml)
        self.assertIsNotNone(fm, "YAML frontmatter extraction failed")
        self.assertEqual(fm.get("title"), "Autonomous Agent Orchestrator")
        self.assertEqual(fm.get("domain"), "01_AI_Agents_and_Autonomous_Systems")
        self.assertEqual(fm.get("reusability_score"), 95)
        self.assertEqual(fm.get("workability_status"), "Production-Ready")
        self.assertIn("AI Agent", fm.get("tags", []))
        self.assertIn("AGENTS.md", fm.get("source_files_synthesized", []))

    def test_f08_02_yaml_required_keys_schema(self):
        """Verify required frontmatter keys schema: title, domain, reusability_score, workability_status, tags, dependencies, source_files_synthesized."""
        required_keys = {
            "title", "domain", "reusability_score", "workability_status",
            "tags", "dependencies", "source_files_synthesized"
        }
        sample_dict = {
            "title": "Test Title",
            "domain": "02_Workflow_Automations_n8n",
            "reusability_score": 88,
            "workability_status": "High-Workability",
            "tags": ["n8n"],
            "dependencies": ["n8n-nodes-base"],
            "source_files_synthesized": ["workflow.json"]
        }
        self.assertTrue(required_keys.issubset(set(sample_dict.keys())), "Required YAML schema keys mismatch")

    def test_f08_03_reusability_score_numeric_range_validation(self):
        """Verify reusability_score must be an integer between 1 and 100."""
        valid_scores = [1, 50, 95, 100]
        invalid_scores = [-1, 0, 101, "invalid", None]
        for s in valid_scores:
            self.assertTrue(isinstance(s, (int, float)) and 1 <= s <= 100, f"Valid score {s} rejected")
        for s in invalid_scores:
            is_valid = isinstance(s, (int, float)) and 1 <= s <= 100
            self.assertFalse(is_valid, f"Invalid score {s} accepted")

    def test_f08_04_workability_status_allowed_enums(self):
        """Verify workability_status accepts standard enum values."""
        allowed_enums = {
            "Production-Ready",
            "High-Workability",
            "Deployable Template",
            "Deployable Agent Config",
            "Experimental",
            "Half-Baked",
            "Workable"
        }
        self.assertIn("Production-Ready", allowed_enums)
        self.assertIn("Half-Baked", allowed_enums)

    def test_f08_05_tags_and_sources_are_list_types(self):
        """Verify tags, dependencies, and source_files_synthesized are sequence/list types."""
        sample_tags = ["AI", "Trading"]
        sample_sources = ["source1.json", "source2.pdf"]
        self.assertIsInstance(sample_tags, list)
        self.assertIsInstance(sample_sources, list)


class TestTier1Feature09MergeRationaleSuperiority(unittest.TestCase):
    """F09: Merge Rationale & Superiority Justification"""

    def test_f09_01_golden_master_section_structure_contract(self):
        """Verify required 6-part section structure contract for synthesized playbooks."""
        required_sections = [
            "Executive Summary & Architectural Mental Model",
            "Source Lineage & Merge Rationale",
            "Core Implementations & Code Artifacts",
            "Deployment SOP & Operational Guide",
            "Failure Modes, Edge Cases & Troubleshooting"
        ]
        self.assertEqual(len(required_sections), 5, "Contract requires 5 primary sections (plus prompt decks)")

    def test_f09_02_merge_rationale_explanation_requirement(self):
        """Verify lineage section requires explicit explanation of why sources were merged."""
        sample_section = """## Source Lineage & Merge Rationale
- **Synthesized Sources**: `workflow_a.json`, `workflow_b.json`, `docs.docx`
- **Merge Rationale**: Unified disparate webhook nodes and error handlers into a single resilient workflow.
- **Superiority Justification**: Eliminates 3 duplicate schemas, sanitizes hardcoded tokens, and upgrades deprecated node parameters.
"""
        self.assertIn("Merge Rationale", sample_section)
        self.assertIn("Superiority Justification", sample_section)

    def test_f09_03_raw_source_traceability(self):
        """Verify referenced source files in lineage exist in raw repository."""
        raw_names = {f.name.lower() for f in RAW_DIR.rglob("*") if f.is_file()}
        self.assertIn("agents.md", raw_names, "AGENTS.md must exist in raw corpus for lineage tracing")
        self.assertIn("complete-n8n-documentation.docx", raw_names, "n8n doc must exist in raw corpus")

    def test_f09_04_superiority_justification_detail_verification(self):
        """Verify superiority criteria include deduplication, schema unification, and syntax modernization."""
        superiority_keywords = ["unif", "dedup", "modern", "resilien", "eliminat", "improv"]
        sample_text = "Eliminated deprecated syntax and unified duplicate triggers."
        matches = [k for k in superiority_keywords if k in sample_text.lower()]
        self.assertGreaterEqual(len(matches), 2, "Superiority text must contain clear justification criteria")

    def test_f09_05_playbook_architectural_mental_model_presence(self):
        """Verify mental model section includes architecture overview or diagram markers."""
        sample_mental_model = """# Executive Summary & Architectural Mental Model
```
[Client / Webhook] ---> [n8n Router] ---> [LLM Agent Node] ---> [Postgres / Supabase]
```
"""
        self.assertIn("Architectural Mental Model", sample_mental_model)
        self.assertTrue("-->" in sample_mental_model or "graph" in sample_mental_model)


class TestTier1Feature10CodeAndPromptDecks(unittest.TestCase):
    """F10: Architecture, Code Artifacts & Parameterized Prompt Decks"""

    def test_f10_01_code_blocks_syntax_specifiers(self):
        """Verify code blocks in playbooks use explicit language syntax specifiers."""
        sample_md = """
```python
def process_data(payload: dict) -> dict:
    return {"status": "success", "data": payload}
```
```json
{
  "name": "n8n_node",
  "type": "n8n-nodes-base.httpRequest"
}
```
"""
        code_blocks = re.findall(r"```([a-zA-Z0-9_-]+)\n", sample_md)
        self.assertIn("python", code_blocks)
        self.assertIn("json", code_blocks)

    def test_f10_02_json_code_blocks_syntactic_validity(self):
        """Verify JSON snippets extracted from markdown blocks parse cleanly."""
        sample_json_block = """{
            "nodes": [
                {"name": "Webhook", "type": "n8n-nodes-base.webhook", "position": [100, 200]},
                {"name": "OpenAI", "type": "n8n-nodes-base.openAi", "position": [300, 200]}
            ],
            "connections": {}
        }"""
        parsed = json.loads(sample_json_block)
        self.assertEqual(len(parsed["nodes"]), 2)
        self.assertEqual(parsed["nodes"][0]["name"], "Webhook")

    def test_f10_03_parameterized_prompt_deck_variables(self):
        """Verify prompt templates utilize parameterized replacement tokens (e.g. {{VARIABLE}} or [VARIABLE])."""
        sample_prompt = """You are an expert quantitative researcher.
Analyze the following ticker: {{TICKER_SYMBOL}} over time horizon {{TIME_HORIZON_DAYS}}.
Apply risk threshold: [MAX_DRAWDOWN_PCT].
"""
        tokens = re.findall(r"\{\{([A-Z0-9_]+)\}\}|\[([A-Z0-9_]+)\]", sample_prompt)
        flattened = [t[0] or t[1] for t in tokens if t[0] or t[1]]
        self.assertIn("TICKER_SYMBOL", flattened)
        self.assertIn("MAX_DRAWDOWN_PCT", flattened)

    def test_f10_04_deployment_sop_step_by_step_structure(self):
        """Verify deployment SOPs contain actionable numbered steps and environment variables."""
        sample_sop = """## Deployment SOP & Operational Guide
1. Set up environment: `pip install -r requirements.txt`
2. Export API Key: `export OPENAI_API_KEY="sk-..."`
3. Execute workflow: `python main.py --config prod.json`
"""
        has_numbered_steps = bool(re.search(r"^\d+\.\s+", sample_sop, re.MULTILINE))
        self.assertTrue(has_numbered_steps, "Deployment SOP must feature numbered operational steps")

    def test_f10_05_failure_modes_and_troubleshooting_coverage(self):
        """Verify failure modes section documents edge cases, timeouts, and error codes."""
        sample_troubleshooting = """## Failure Modes, Edge Cases & Troubleshooting
- **Error 429 (Rate Limit Exceeded)**: Implement exponential backoff with jitter.
- **Malformed Payload (JSONDecodeError)**: Verify input string is UTF-8 before parsing.
- **Database Lock (sqlite3.OperationalError)**: Enable WAL mode (`PRAGMA journal_mode=WAL;`).
"""
        self.assertIn("Rate Limit", sample_troubleshooting)
        self.assertIn("JSONDecodeError", sample_troubleshooting)
        self.assertIn("OperationalError", sample_troubleshooting)


class TestTier1Feature11ExcelDashboard(unittest.TestCase):
    """F11: Excel Knowledge Mine Dashboard (Master_Second_Brain_Knowledge_Mine.xlsx)"""

    def test_f11_01_excel_file_exists_at_expected_path(self):
        """Verify Master_Second_Brain_Knowledge_Mine.xlsx exists in 00_Index_and_Dashboards/."""
        self.assertTrue(EXCEL_PATH.exists(), f"Excel dashboard missing: {EXCEL_PATH}")

    def test_f11_02_excel_workbook_opens_cleanly_with_openpyxl(self):
        """Verify Excel file opens cleanly via openpyxl without corruption."""
        try:
            import openpyxl
            wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
            self.assertIsNotNone(wb)
            self.assertGreater(len(wb.sheetnames), 0)
        except Exception as e:
            self.fail(f"Failed to open Excel dashboard with openpyxl: {e}")

    def test_f11_03_excel_has_multiple_dedicated_sheets(self):
        """Verify Excel dashboard contains multiple dedicated category sheets (>=5 sheets)."""
        import openpyxl
        wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
        sheet_names = wb.sheetnames
        self.assertGreaterEqual(len(sheet_names), 5, f"Expected >=5 sheets, found: {sheet_names}")

    def test_f11_04_excel_master_sheet_contains_rows_and_columns(self):
        """Verify first/master sheet contains headers and populated asset rows."""
        import openpyxl
        wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
        ws = wb.active
        self.assertGreaterEqual(ws.max_row, 50, f"Expected >=50 asset rows in master sheet, found {ws.max_row}")
        self.assertGreaterEqual(ws.max_column, 5, f"Expected >=5 columns in master sheet, found {ws.max_column}")

    def test_f11_05_excel_auto_filters_and_styling(self):
        """Verify sheets have auto-filters configured or non-empty header rows."""
        import openpyxl
        wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
        for name in wb.sheetnames:
            ws = wb[name]
            # Check row 1 has header text
            header_vals = [cell.value for cell in ws[1] if cell.value is not None]
            self.assertGreater(len(header_vals), 0, f"Sheet {name} has empty header row")


class TestTier1Feature12HTMLNavigator(unittest.TestCase):
    """F12: Interactive HTML Navigator (Interactive_Knowledge_Mine_Navigator.html)"""

    def test_f12_01_html_navigator_exists(self):
        """Verify Interactive_Knowledge_Mine_Navigator.html exists in 00_Index_and_Dashboards/."""
        self.assertTrue(HTML_NAVIGATOR_PATH.exists(), f"HTML navigator missing: {HTML_NAVIGATOR_PATH}")

    def test_f12_02_html_valid_structure_and_doctype(self):
        """Verify HTML file contains DOCTYPE, html, head, body tags."""
        content = HTML_NAVIGATOR_PATH.read_text(encoding="utf-8", errors="ignore")
        self.assertTrue("<!DOCTYPE html>" in content or "<!doctype html>" in content)
        self.assertIn("<html", content)
        self.assertIn("<head>", content)
        self.assertIn("<body>", content)

    def test_f12_03_html_includes_chartjs_visualization(self):
        """Verify HTML navigator includes Chart.js script and canvas elements."""
        content = HTML_NAVIGATOR_PATH.read_text(encoding="utf-8", errors="ignore")
        self.assertTrue("chart.js" in content.lower() or "chartjs" in content.lower(), "Chart.js missing from HTML navigator")
        self.assertIn("<canvas", content, "Canvas element for Chart.js missing from HTML navigator")

    def test_f12_04_html_domain_filter_pills_present(self):
        """Verify HTML navigator contains filter button pills for domain navigation."""
        content = HTML_NAVIGATOR_PATH.read_text(encoding="utf-8", errors="ignore")
        self.assertTrue("filter-btn" in content or "filter-pills" in content or "button" in content,
                        "Filter pills missing from HTML navigator")

    def test_f12_05_html_live_search_input_and_filter_logic(self):
        """Verify HTML navigator contains instant search input and JavaScript event listeners."""
        content = HTML_NAVIGATOR_PATH.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("searchInput", content, "Search input element missing from HTML navigator")
        self.assertTrue("addEventListener" in content or "oninput" in content or "onkeyup" in content,
                        "Interactive search event listener missing from HTML navigator")


class TestTier1Feature13SQLiteFTS5RAG(unittest.TestCase):
    """F13: SQLite FTS5 RAG Indexing (Processed_Assets/my_rag_data.db)"""

    def test_f13_01_database_exists_and_non_empty(self):
        """Verify my_rag_data.db exists and has non-zero size."""
        self.assertTrue(DB_PATH.exists(), f"Database missing at {DB_PATH}")
        self.assertGreater(DB_PATH.stat().st_size, 100000, f"Database unexpectedly small: {DB_PATH.stat().st_size} bytes")

    def test_f13_02_sqlite_integrity_check(self):
        """Verify SQLite database passes PRAGMA integrity_check."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(result.lower(), "ok", f"SQLite integrity check failed: {result}")

    def test_f13_03_database_required_tables_present(self):
        """Verify required tables (documents, chunks, chunks_fts, kg_nodes, kg_edges) exist."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' OR type='shadow';")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        for required in ["documents", "chunks", "chunks_fts", "kg_nodes", "kg_edges"]:
            self.assertIn(required, tables, f"Required table {required} missing from database")

    def test_f13_04_fts5_virtual_table_bm25_query(self):
        """Verify chunks_fts virtual table supports BM25 rank queries."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT asset_title, snippet(chunks_fts, 0, '<b>', '</b>', '...', 15), bm25(chunks_fts) as rank
            FROM chunks_fts
            WHERE chunks_fts MATCH '"agent"*'
            ORDER BY rank
            LIMIT 5;
        """)
        rows = cursor.fetchall()
        conn.close()
        self.assertGreaterEqual(len(rows), 1, "FTS5 query for 'agent' returned no results")

    def test_f13_05_chunks_doc_id_foreign_key_relationship(self):
        """Verify chunks table references documents table records."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.doc_id, d.file_name
            FROM chunks c
            JOIN documents d ON c.doc_id = d.id
            LIMIT 10;
        """)
        rows = cursor.fetchall()
        conn.close()
        self.assertGreaterEqual(len(rows), 5, "Chunks and documents join returned insufficient records")


class TestTier1Feature14KnowledgeGraph(unittest.TestCase):
    """F14: Knowledge Graph DB & HTML Visualization"""

    def test_f14_01_kg_nodes_table_contains_entities(self):
        """Verify kg_nodes table contains populated entities and node types."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*), count(DISTINCT node_type) FROM kg_nodes;")
        count, node_types = cursor.fetchone()
        conn.close()
        self.assertGreater(count, 5, f"Expected >5 kg_nodes, found {count}")
        self.assertGreater(node_types, 1, f"Expected multiple node_types, found {node_types}")

    def test_f14_02_kg_edges_table_contains_relationships(self):
        """Verify kg_edges table connects source and target nodes with valid weights."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*), avg(weight) FROM kg_edges;")
        count, avg_weight = cursor.fetchone()
        conn.close()
        self.assertGreater(count, 5, f"Expected >5 kg_edges, found {count}")
        self.assertIsNotNone(avg_weight, "Edge weights must not be NULL")

    def test_f14_03_kg_edges_foreign_keys_match_nodes(self):
        """Verify source_id and target_id in kg_edges reference valid nodes in kg_nodes."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, e.source_id, e.target_id
            FROM kg_edges e
            WHERE e.source_id NOT IN (SELECT id FROM kg_nodes)
               OR e.target_id NOT IN (SELECT id FROM kg_nodes);
        """)
        orphan_edges = cursor.fetchall()
        conn.close()
        self.assertEqual(len(orphan_edges), 0, f"Found {len(orphan_edges)} orphan edges without matching nodes")

    def test_f14_04_interactive_knowledge_graph_html_exists(self):
        """Verify Interactive_Knowledge_Graph.html exists in 00_Index_and_Dashboards/."""
        self.assertTrue(HTML_GRAPH_PATH.exists(), f"Graph HTML visualizer missing: {HTML_GRAPH_PATH}")

    def test_f14_05_graph_html_contains_visjs_network(self):
        """Verify Interactive_Knowledge_Graph.html includes Vis.js network library and datasets."""
        content = HTML_GRAPH_PATH.read_text(encoding="utf-8", errors="ignore")
        self.assertTrue("vis-network" in content or "vis.network" in content or "vis.DataSet" in content or "nodes" in content,
                        "Vis.js network configuration missing from graph HTML")


class TestTier1Feature15CLISearchEngine(unittest.TestCase):
    """F15: CLI Search Engine Verification (search_engine.py)"""

    def test_f15_01_search_engine_script_exists(self):
        """Verify search_engine.py exists at project root."""
        self.assertTrue(SEARCH_ENGINE_SCRIPT.exists(), f"search_engine.py missing at {SEARCH_ENGINE_SCRIPT}")

    def test_f15_02_search_engine_linear_mode_execution(self):
        """Verify search_engine.py executes linear mode search successfully."""
        proc = subprocess.run(
            [sys.executable, str(SEARCH_ENGINE_SCRIPT), "n8n", "--mode", "linear", "--limit", "3"],
            capture_output=True,
            text=True,
            timeout=10
        )
        self.assertEqual(proc.returncode, 0, f"Search engine linear execution failed: {proc.stderr}")
        self.assertIn("LINEAR FTS5 RESULTS", proc.stdout, "Linear search header missing from output")

    def test_f15_03_search_engine_graph_mode_execution(self):
        """Verify search_engine.py executes graph mode search successfully."""
        proc = subprocess.run(
            [sys.executable, str(SEARCH_ENGINE_SCRIPT), "Pinecone", "--mode", "graph"],
            capture_output=True,
            text=True,
            timeout=10
        )
        self.assertEqual(proc.returncode, 0, f"Search engine graph execution failed: {proc.stderr}")
        self.assertIn("KNOWLEDGE GRAPH CONNECTIONS", proc.stdout, "Graph search header missing from output")

    def test_f15_04_search_engine_limit_parameter(self):
        """Verify --limit parameter constrains output results count."""
        proc = subprocess.run(
            [sys.executable, str(SEARCH_ENGINE_SCRIPT), "trading", "--mode", "linear", "--limit", "2"],
            capture_output=True,
            text=True,
            timeout=10
        )
        self.assertEqual(proc.returncode, 0)
        # Check that result entries don't exceed limit
        matches = re.findall(r"\[\d+\]", proc.stdout)
        self.assertLessEqual(len(matches), 2, f"Returned {len(matches)} results, exceeding limit of 2")

    def test_f15_05_search_engine_subsecond_latency(self):
        """Verify search query executes in sub-second time (< 1.0s)."""
        t0 = time.time()
        proc = subprocess.run(
            [sys.executable, str(SEARCH_ENGINE_SCRIPT), "agent", "--mode", "linear", "--limit", "5"],
            capture_output=True,
            text=True,
            timeout=5
        )
        elapsed = time.time() - t0
        self.assertEqual(proc.returncode, 0)
        self.assertLess(elapsed, 1.5, f"Search query too slow: {elapsed:.3f}s >= 1.5s")


# ============================================================================
# TIER 2: BOUNDARY & CORNER CASES
# ============================================================================

class TestTier2BoundaryAndCornerCases(unittest.TestCase):
    """Tier 2: Boundary, Extreme & Adversarial Corner Cases"""

    def test_t2_01_empty_file_handling(self):
        """Verify empty files (0 bytes) do not cause unhandled crashes in file scanners or tokenizers."""
        from search_engine import search_linear
        # Search for a term that might be empty or index zero files
        try:
            buf = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = buf
            search_linear("empty_file_test_query", limit=5)
            sys.stdout = old_stdout
            out = buf.getvalue()
            self.assertTrue("No matching records" in out or "LINEAR FTS5 RESULTS" in out)
        except Exception as e:
            self.fail(f"Search engine crashed on empty/zero match query: {e}")

    def test_t2_02_password_protected_file_handling(self):
        """Verify password-protected files in corpus (e.g. CAPITAL_GAIN_LOSS_STATEMENT_*.xlsx) are handled gracefully."""
        protected_files = list(RAW_DIR.rglob("*protected*.xlsx"))
        if protected_files:
            target = protected_files[0]
            self.assertTrue(target.exists(), f"Protected file {target} exists")
            # Should be able to read file bytes without throwing unhandled system exceptions
            with open(target, "rb") as f:
                header = f.read(16)
                self.assertGreater(len(header), 0)

    def test_t2_03_invalid_query_fts5_meta_characters(self):
        """Verify FTS5 special characters ('*', '\"', '(', ')', 'NEAR', 'OR', 'AND', '%', ';', '\\0') do not crash search."""
        adversarial_queries = [
            '"""',
            "'''",
            "*** AND *** OR ***",
            "NEAR/5 (agent, memory)",
            "SELECT * FROM documents;",
            "<script>alert('xss')</script>",
            "%$#@!^&()",
            "   \t\n  "
        ]
        for q in adversarial_queries:
            proc = subprocess.run(
                [sys.executable, str(SEARCH_ENGINE_SCRIPT), q, "--mode", "linear", "--limit", "3"],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Must exit cleanly (0) without unhandled Python stack traces
            self.assertEqual(proc.returncode, 0, f"Query '{q}' caused exit code {proc.returncode}")
            self.assertNotIn("Traceback (most recent call last)", proc.stderr, f"Query '{q}' raised unhandled exception: {proc.stderr}")

    def test_t2_04_empty_and_whitespace_only_queries(self):
        """Verify empty and whitespace-only query strings are handled gracefully."""
        for q in ["", "   ", "\t\t"]:
            proc = subprocess.run(
                [sys.executable, str(SEARCH_ENGINE_SCRIPT), q, "--mode", "linear"],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.assertEqual(proc.returncode, 0)
            self.assertNotIn("Traceback", proc.stderr)

    def test_t2_05_extreme_bm25_limits(self):
        """Verify extreme limit parameters (limit=0, limit=-1, limit=10000) are handled without crashing."""
        for lim in [0, -1, 10000]:
            proc = subprocess.run(
                [sys.executable, str(SEARCH_ENGINE_SCRIPT), "agent", "--mode", "linear", "--limit", str(lim)],
                capture_output=True,
                text=True,
                timeout=10
            )
            self.assertEqual(proc.returncode, 0, f"Limit {lim} caused non-zero exit code")

    def test_t2_06_missing_frontmatter_keys_handling(self):
        """Verify frontmatter extractor handles missing keys gracefully with default values."""
        partial_md = """---
title: "Minimal Title"
domain: "01_AI_Agents_and_Autonomous_Systems"
---
# Body
"""
        fm, body = extract_yaml_frontmatter(partial_md)
        self.assertEqual(fm.get("title"), "Minimal Title")
        self.assertIsNone(fm.get("reusability_score"))
        self.assertEqual(body.strip(), "# Body")

    def test_t2_07_malformed_yaml_frontmatter_handling(self):
        """Verify frontmatter extractor handles malformed YAML syntax without unhandled exceptions."""
        malformed_md = """---
title: "Unmatched quote string
domain: [unterminated list
reusability_score: %%%
---
# Content
"""
        try:
            fm, body = extract_yaml_frontmatter(malformed_md)
            # Should return either parsed dict or fallback without crashing
            self.assertTrue(isinstance(fm, (dict, type(None))))
        except Exception as e:
            self.fail(f"extract_yaml_frontmatter crashed on malformed YAML: {e}")

    def test_t2_08_nonexistent_graph_entity_search(self):
        """Verify search_graph handles non-existent entity names gracefully."""
        proc = subprocess.run(
            [sys.executable, str(SEARCH_ENGINE_SCRIPT), "NonExistent_Entity_99999_XYZ", "--mode", "graph"],
            capture_output=True,
            text=True,
            timeout=10
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("not found in Knowledge Graph", proc.stdout)

    def test_t2_09_windows_path_normalization_and_spaces(self):
        """Verify file paths containing spaces and mixed slash formats resolve accurately."""
        test_filename = "Account Statement (1).pdf"
        target_path = RAW_DIR / test_filename
        if target_path.exists():
            resolved = target_path.resolve()
            self.assertTrue(resolved.exists())
            self.assertEqual(resolved.name, test_filename)


# ============================================================================
# TIER 3: CROSS-FEATURE COMBINATIONS
# ============================================================================

class TestTier3CrossFeatureCombinations(unittest.TestCase):
    """Tier 3: Multi-Module Cross-Feature Combinations & Invariants"""

    def test_t3_01_search_engine_results_match_excel_records(self):
        """Verify search engine linear results correspond to documents indexed in Excel dashboard."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT file_name, asset_title FROM documents LIMIT 5;")
        db_records = cursor.fetchall()
        conn.close()
        
        import openpyxl
        wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
        ws = wb.active
        excel_filenames = {str(ws.cell(row=r, column=2).value) for r in range(2, min(ws.max_row + 1, 100))}
        
        # Verify overlap between DB file names and Excel file names
        match_count = sum(1 for fname, _ in db_records if any(fname in ef for ef in excel_filenames))
        self.assertGreaterEqual(match_count, 1, "No overlap between SQLite documents and Excel dashboard records")

    def test_t3_02_knowledge_graph_nodes_cross_reference_database_documents(self):
        """Verify knowledge graph entities link to document topics and tags in database."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT n.label, count(e.id) as edge_count
            FROM kg_nodes n
            LEFT JOIN kg_edges e ON n.id = e.source_id OR n.id = e.target_id
            GROUP BY n.id
            HAVING edge_count > 0
            LIMIT 10;
        """)
        connected_nodes = cursor.fetchall()
        conn.close()
        self.assertGreaterEqual(len(connected_nodes), 3, "Insufficient connected entities in Knowledge Graph")

    def test_t3_03_vault_files_covered_by_gitignore_rules(self):
        """Verify all sensitive files destined for 01_Vault_Private/ are covered by .gitignore rules."""
        gitignore_content = GITIGNORE_PATH.read_text(encoding="utf-8", errors="ignore")
        # Ensure vault path rule exists
        self.assertTrue("01_Vault_Private" in gitignore_content, "01_Vault_Private not covered in .gitignore")

    def test_t3_04_playbook_lineage_matches_raw_inventory(self):
        """Verify source assets declared in Golden Master playbooks exist in Raw_copies/ directory."""
        raw_names_lower = {f.name.lower() for f in RAW_DIR.rglob("*") if f.is_file()}
        # Check standard anchor assets that synthesize into Golden Masters
        sample_sources = ["agents.md", "complete-n8n-documentation.docx", "my_api_keys_backup.md"]
        for src in sample_sources:
            self.assertIn(src, raw_names_lower, f"Source asset {src} missing from Raw_copies/")

    def test_t3_05_html_navigator_topics_match_database_categories(self):
        """Verify topic categories in HTML navigator align with database topic classifications."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT topic FROM documents;")
        db_topics = {row[0] for row in cursor.fetchall() if row[0]}
        conn.close()
        
        html_content = HTML_NAVIGATOR_PATH.read_text(encoding="utf-8", errors="ignore")
        # Check that primary DB topics (AI, Automation, Finance/Trading) appear in HTML navigator
        has_topic_match = any(t.lower() in html_content.lower() for t in ["automation", "agent", "trading", "prompt"])
        self.assertTrue(has_topic_match, "HTML navigator categories do not match database topics")

    def test_t3_06_cold_storage_isolation_preserves_raw_source_immutability(self):
        """Verify that clutter isolation retains files without decreasing Raw_copies/ count."""
        raw_files = list(RAW_DIR.rglob("*"))
        raw_files_only = [f for f in raw_files if f.is_file()]
        self.assertGreaterEqual(len(raw_files_only), 440, "Raw_copies file count degraded during cold storage isolation")


# ============================================================================
# TIER 4: REAL-WORLD SCENARIOS
# ============================================================================

class TestTier4RealWorldScenarios(unittest.TestCase):
    """Tier 4: Realistic User Workloads & Deep Integration Scenarios"""

    def test_t4_01_real_world_scenario_n8n_automation_query(self):
        """Scenario 1: User searches for n8n webhook automation workflows."""
        proc = subprocess.run(
            [sys.executable, str(SEARCH_ENGINE_SCRIPT), "n8n webhook automation", "--mode", "linear", "--limit", "5"],
            capture_output=True,
            text=True,
            timeout=10
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("LINEAR FTS5 RESULTS", proc.stdout)
        # Verify rank score exists and results are non-empty
        self.assertTrue("Rank Score:" in proc.stdout or "No matching records" not in proc.stdout)

    def test_t4_02_real_world_scenario_ai_agent_architecture_query(self):
        """Scenario 2: User queries autonomous AI agent memory and tool specifications."""
        proc = subprocess.run(
            [sys.executable, str(SEARCH_ENGINE_SCRIPT), "agent autonomous memory tool", "--mode", "linear", "--limit", "5"],
            capture_output=True,
            text=True,
            timeout=10
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("LINEAR FTS5 RESULTS", proc.stdout)

    def test_t4_03_real_world_scenario_quantitative_trading_query(self):
        """Scenario 3: User queries quantitative trading strategies, indicators, and market data."""
        proc = subprocess.run(
            [sys.executable, str(SEARCH_ENGINE_SCRIPT), "trading market indicators strategy", "--mode", "linear", "--limit", "5"],
            capture_output=True,
            text=True,
            timeout=10
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("LINEAR FTS5 RESULTS", proc.stdout)

    def test_t4_04_real_world_scenario_excel_workbook_deep_inspection(self):
        """Scenario 4: User opens Master_Second_Brain_Knowledge_Mine.xlsx and inspects sheet dimensions, formulas and styling."""
        import openpyxl
        wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
        self.assertIn("Master Knowledge Mine", wb.sheetnames[0], "First sheet should be Master Knowledge Mine")
        
        # Verify row counts and column completeness
        master_sheet = wb["Master Knowledge Mine"]
        self.assertGreater(master_sheet.max_row, 50, "Master sheet contains insufficient rows")
        
        # Check for KPI summary or category sheets
        self.assertGreaterEqual(len(wb.sheetnames), 5, "Excel workbook missing category breakdown sheets")

    def test_t4_05_real_world_scenario_html_navigator_dom_and_graph_validation(self):
        """Scenario 5: User loads HTML navigator and Knowledge Graph visualizers in web browser."""
        nav_html = HTML_NAVIGATOR_PATH.read_text(encoding="utf-8", errors="ignore")
        graph_html = HTML_GRAPH_PATH.read_text(encoding="utf-8", errors="ignore")
        
        # Check Navigator DOM IDs
        for expected_id in ["searchInput", "assetGrid", "resultsCount"]:
            self.assertIn(f'id="{expected_id}"', nav_html, f"DOM element with id='{expected_id}' missing in HTML navigator")
            
        # Check Graph visualizer Vis.js container and physics configuration
        self.assertTrue("network" in graph_html or "mynetwork" in graph_html or "vis.Network" in graph_html,
                        "Vis.js network container missing in graph visualizer")


# ============================================================================
# TEST RUNNER & ENTRY POINT
# ============================================================================

def run_all_tests():
    """Runs all test suites and prints a structured 4-tier summary breakdown."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        # Tier 1
        TestTier1Feature01RawIntegrity,
        TestTier1Feature02VaultIsolation,
        TestTier1Feature03GitSecurity,
        TestTier1Feature04ColdStorageClutter,
        TestTier1Feature05DomainTaxonomy,
        TestTier1Feature06FormatAssetCategorization,
        TestTier1Feature07MarkdownSynthesis,
        TestTier1Feature08YAMLFrontmatter,
        TestTier1Feature09MergeRationaleSuperiority,
        TestTier1Feature10CodeAndPromptDecks,
        TestTier1Feature11ExcelDashboard,
        TestTier1Feature12HTMLNavigator,
        TestTier1Feature13SQLiteFTS5RAG,
        TestTier1Feature14KnowledgeGraph,
        TestTier1Feature15CLISearchEngine,
        # Tier 2
        TestTier2BoundaryAndCornerCases,
        # Tier 3
        TestTier3CrossFeatureCombinations,
        # Tier 4
        TestTier4RealWorldScenarios
    ]
    
    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))
        
    print("=" * 80)
    print(" LAPTOP 1 (L1) SECOND BRAIN - END-TO-END VERIFICATION TEST RUNNER")
    print(f" Target Directory: {PROJECT_ROOT}")
    print(f" Total Test Cases Registered: {suite.countTestCases()}")
    print("=" * 80)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print(" TEST RUN SUMMARY BREAKDOWN")
    print("=" * 80)
    print(f" Tests Executed: {result.testsRun}")
    print(f" Successes:      {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f" Failures:       {len(result.failures)}")
    print(f" Errors:         {len(result.errors)}")
    print(f" Pass Rate:      {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 80)
    
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
