## 2026-08-16T12:36:32Z
You are teamwork_preview_worker_m2_part2.
Your working directory is: C:\knowledgeBase_staging\.agents\teamwork_preview_worker_m2_part2
Project root: C:\knowledgeBase_staging
Specification: C:\knowledgeBase_staging\ORIGINAL_REQUEST.md
Project Plan: C:\knowledgeBase_staging\PROJECT.md
Survey 2 Report: C:\knowledgeBase_staging\.agents\teamwork_preview_explorer_survey_2\survey_report.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Task:
Execute Milestone 2 (Part 2): Scaffold Taxonomy & 10-to-1 Golden Markdown Synthesis for Domains 6 to 10:
6. `06_Quantitative_Finance_and_Trading`
7. `07_Content_Creation_and_Media_Engines`
8. `08_Business_Operations_and_Subbroking`
9. `09_LLM_Conversations_and_Syntheses`
10. `10_R_and_D_Incubator_Half_Baked_Ideas`

Requirements:
1. Scaffold taxonomy directories in both:
   - `02_Assets_Library/<domain_name>/`
   - `03_Topics_and_Projects/<domain_name>/`
2. For each assigned domain, analyze the raw assets in `Raw_copies/` and synthesize them into high-density Golden Master Playbooks in `03_Topics_and_Projects/<domain_name>/` (produce comprehensive playbooks covering all major clusters identified in Survey 2 report).
3. Each Golden Master playbook MUST include:
   - Complete YAML frontmatter (`title`, `domain`, `reusability_score` [1-100], `workability_status` [Production-Ready | High-Workability | Experimental | Half-Baked], `tags`, `dependencies`, `source_files_synthesized`).
   - Section 1: Executive Summary & Architectural Mental Model (ASCII/Mermaid diagram).
   - Section 2: Source Lineage & Merge Rationale (exact list of raw files, rationale for combining, superiority justification explaining why/how the Golden Master is superior to the separate raw inputs).
   - Section 3: Core Implementations & Code Artifacts (clean, copy-paste ready scripts / n8n JSON nodes / configs without placeholder stubs).
   - Section 4: Parameterized Prompt Decks & Templates (with variables like {{VAR}}).
   - Section 5: Deployment SOP & Operational Guide (actionable step-by-step).
   - Section 6: Failure Modes, Edge Cases & Troubleshooting.
4. Populate format library references in `02_Assets_Library/<domain_name>/` if appropriate.
5. Strict Non-Destructive Operation: Do NOT delete or modify files in `Raw_copies/`.
6. Write your handoff report to `C:\knowledgeBase_staging\.agents\teamwork_preview_worker_m2_part2\handoff.md` and notify orchestrator.
