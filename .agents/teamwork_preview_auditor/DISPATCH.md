## 2026-08-16T12:51:03Z
You are teamwork_preview_auditor.
Your working directory is: C:\knowledgeBase_staging\.agents\teamwork_preview_auditor
Project root: C:\knowledgeBase_staging
Specification: C:\knowledgeBase_staging\ORIGINAL_REQUEST.md
Project Spec: C:\knowledgeBase_staging\PROJECT.md

Task:
Perform a comprehensive FORENSIC INTEGRITY AUDIT across the entire Second Brain project at `C:\knowledgeBase_staging`.

Audit checks:
1. Non-Destructive Raw Integrity: Verify all 443 raw assets in `Raw_copies/` (396 root + 47 quarantine) are 100% intact with 0 deletions, modifications, or renames.
2. Anti-Cheating & Authenticity: Verify all implementations are genuine. Ensure no hardcoded test mocks, no fake empty files, no dummy facade implementations, and no bypasses.
3. Vault Isolation & Security: Verify `01_Vault_Private/` holds the 73 sensitive assets, and root `.gitignore` properly excludes `01_Vault_Private/`, `*.env`, `*.key`, `*secret*`, `*credential*`.
4. Cold Storage Quarantine: Verify `04_Archive_Cold_Storage/` contains zero-byte files, temporary lock files, duplicate stubs, and empty boilerplates.
5. 10-Domain Taxonomy & Golden Markdown Synthesis: Verify 10 canonical domains in `02_Assets_Library/` and `03_Topics_and_Projects/`, and all 46 Golden Master playbooks have complete YAML frontmatter, 6-part contract, source lineage, merge rationale, superior draft justification, mental models, code blocks, prompt decks, and SOPs.
6. Dashboards, DB & Search: Verify `Processed_Assets/my_rag_data.db` (real SQLite FTS5 table, real chunks, real kg_nodes/kg_edges), `Master_Second_Brain_Knowledge_Mine.xlsx` (real openpyxl workbook with auto-filters & 7+ sheets), `Interactive_Knowledge_Mine_Navigator.html` (real Chart.js charts & 10 domain pills), `Interactive_Knowledge_Graph.html` (real Vis.js network), and `search_engine.py` (real working CLI).
7. Run the full E2E test suite: `python tests/test_second_brain_e2e.py`.

Deliver a structured binary verdict: **CLEAN** or **INTEGRITY VIOLATION**.
Author your detailed audit report in `C:\knowledgeBase_staging\.agents\teamwork_preview_auditor\handoff.md` and notify orchestrator.
