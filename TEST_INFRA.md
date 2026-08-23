# E2E Test Infra: Laptop 1 (L1) Second Brain

## Test Philosophy
- Opaque-box, requirement-driven. Derived from ORIGINAL_REQUEST.md.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial + Real-World Workloads.
- Non-destructive validation: Verifies Raw_copies/ integrity (443 total assets, 0 deletions).

## Feature Inventory Mapping
| # | Feature | Source | Tier 1 (Coverage) | Tier 2 (Boundary) | Tier 3 (Pairwise) | Tier 4 (Workload) |
|---|---------|--------|:-----------------:|:-----------------:|:-----------------:|:-----------------:|
| F01 | Raw Source Immutability | ORIGINAL_REQUEST §Constraints | >=5 checks | 0 deletions check | Integrity across moves | End-to-end immutability |
| F02 | Private Vault Partitioning | ORIGINAL_REQUEST §R1 | Sub-vault exists | Empty file handling | Permission & location | Sensitive file segregation |
| F03 | Git Security Protection | ORIGINAL_REQUEST §R1 | .gitignore exists | Wildcard patterns | Vault rule matching | Git status exclusion |
| F04 | Cold Storage Clutter Isolation | ORIGINAL_REQUEST §R1 | 04_ folder exists | Zero-byte isolation | Duplicate handling | Clutter sweep |
| F05 | 10-Domain Taxonomy Scaffolding | ORIGINAL_REQUEST §R2 | 10 dirs in 02_ & 03_ | Exact naming | Path normalization | Full tree inspection |
| F06 | Format Asset Categorization | ORIGINAL_REQUEST §R2 | Format subdirs | Empty dir tolerance | Asset routing | Library organization |
| F07 | 10-to-1 Markdown Synthesis | ORIGINAL_REQUEST §R3 | Playbooks present | Non-empty bodies | Multi-source merges | High-density content |
| F08 | YAML Frontmatter & Lineage | ORIGINAL_REQUEST §R3 | Valid YAML headers | Required keys | Schema types | Source files list |
| F09 | Merge Rationale & Superiority | ORIGINAL_REQUEST §R3 | Rationale section | Superiority text | Completeness | Lineage tracing |
| F10 | Architecture, Code & Prompt Decks | ORIGINAL_REQUEST §R3 | Code blocks format | JSON validity | Prompt parameters | Executable SOPs |
| F11 | Excel Knowledge Mine Dashboard | ORIGINAL_REQUEST §R4 | .xlsx opens cleanly | 7 styled sheets | Auto-filter enabled | KPI formulas & counts |
| F12 | Interactive HTML Navigator | ORIGINAL_REQUEST §R4 | .html exists & valid | Chart.js present | 10 domain pills | Live search script |
| F13 | SQLite FTS5 RAG Indexing | ORIGINAL_REQUEST §R4 | DB exists & valid | Porter tokenizer | BM25 rank scoring | Multi-chunk queries |
| F14 | Knowledge Graph DB & HTML | ORIGINAL_REQUEST §R4 | kg_nodes & kg_edges | Entity resolution | Edge weights | Vis.js graph HTML |
| F15 | CLI Search Engine Verification | ORIGINAL_REQUEST §R4 | Linear mode works | Graph mode works | Sub-second latency | Keyword matches |

## Test Architecture
- Test runner: `pytest` or standalone Python script `tests/test_second_brain_e2e.py`
- Invocations: `python tests/test_second_brain_e2e.py`
- Pass criteria: Exit code 0, 100% tests passing across Tiers 1-4.
