---
title: "R&D Incubator Backlog, Rapid Prototyping & Idea Promotion Framework"
domain: "10_R_and_D_Incubator_Half_Baked_Ideas"
reusability_score: 88
workability_status: "Experimental"
tags:
  - "rd-incubator"
  - "idea-backlog"
  - "rapid-prototyping"
  - "maps-of-content"
  - "proof-of-concept"
  - "incubation-scorecard"
dependencies:
  - "obsidian"
  - "python >= 3.10"
  - "sqlite3"
source_files_synthesized:
  - "Raw_copies/moc_template.md"
  - "Raw_copies/content_template.md"
  - "Raw_copies/Untitled document.pdf"
  - "Raw_copies/4QsExsft5X.pdf"
  - "Raw_copies/D155472913 (1).pdf"
  - "Raw_copies/24feb2026.txt"
last_updated: "2026-08-16"
version: "1.0.0"
---

# Executive Summary & Architectural Mental Model

The **R&D Incubator Backlog, Rapid Prototyping & Idea Promotion Framework** is an innovation management engine and stage-gate evaluation system for capturing, scoring, incubating, and promoting half-baked ideas, speculative research papers, and technical experiments into verified production projects.

Solo innovators and research engineers often suffer from "Idea Hoarding": capturing hundreds of brainstorms and research PDFs that languish in unstructured folders without a clear path to execution. This Golden Master establishes the **3-Stage Incubation Funnel**:
1. **Stage 1: Raw Idea Capture & Map of Content (MOC) Indexing**: Ingests raw brainstorms, unstructured notes, and external PDFs, applying structured metadata and linking relationships.
2. **Stage 2: Idea Scorecard & Feasibility Sieve**: Evaluates each candidate idea across 4 objective metrics (Technical Feasibility, Speed to MVP, Monetization Potential, and Strategic Synergy) to calculate an Incubation Viability Score (0–100).
3. **Stage 3: Rapid 48-Hour Spike Prototyping**: Builds a minimal proof-of-concept (POC) script or test harness to validate core assumptions before allocating significant engineering bandwidth.
4. **Stage 4: Graduation to Production Domain**: Promotes validated POCs into one of the 9 canonical production domains or archives unworkable experiments.

```
+--------------------------------------------------------------------------------------------------+
|                    R&D INCUBATOR & IDEA PROMOTION STAGE-GATE FUNNEL                              |
+--------------------------------------------------------------------------------------------------+
                                                 |
                                     [ Uncurated Raw Brainstorm / PDF ]
                                                 |
                                                 v
                     +-------------------------------------------------------+
                     |         Stage 1: Map of Content (MOC) Ingestion       |
                     |  - Metadata Tagging (Topic, Format, Urgency)          |
                     |  - Auto-linked into Obsidian Second Brain Graph       |
                     +-------------------------------------------------------+
                                                 |
                                                 v
                     +-------------------------------------------------------+
                     |         Stage 2: 4-Factor Idea Viability Scorecard    |
                     |  - Technical Feasibility (Weight: 30%)                |
                     |  - Speed to Working MVP < 48 Hours (Weight: 30%)      |
                     |  - Direct Monetization Potential (Weight: 25%)        |
                     |  - Strategic Synergy with Core Vision (Weight: 15%)   |
                     +-------------------------------------------------------+
                                                 |
                                   +-------------+-------------+
                                   |                           |
                       [ Score >= 75: High Viability ]   [ Score < 75: Archive/Park ]
                                   |                           |
                                   v                           v
             +------------------------------------+   +------------------------------------+
             | Stage 3: 48-Hour Rapid Spike       |   | Cold Storage Incubator Archive     |
             | - Build minimal Python / n8n POC   |   | - Preserved for future reference   |
             | - Validate API / user interest     |   +------------------------------------+
             +------------------------------------+
                                   |
                                   v
                     +-------------------------------------------------------+
                     |         Stage 4: Milestone Graduation & Promotion     |
                     |  - Promoted to Canonical Domain (01 to 09)            |
                     |  - Full Golden Master Playbook Authored               |
                     +-------------------------------------------------------+
```

---

# Source Lineage & Merge Rationale

### Exact Source Files Synthesized
1. `Raw_copies/moc_template.md` (742 B) — Standard Obsidian Map of Content (MOC) taxonomy template.
2. `Raw_copies/content_template.md` (1.1 KB) — Standard research note schema and metadata structure.
3. `Raw_copies/Untitled document.pdf` (108 KB) & `Raw_copies/4QsExsft5X.pdf` (21.8 KB) & `Raw_copies/D155472913 (1).pdf` (1.0 MB) — Uncurated external whitepapers and experimental notes.
4. `Raw_copies/24feb2026.txt` (3.7 KB) — Raw idea scratchpad capturing local AI setup concepts and next-step experiments.

### Concrete Merge Rationale
The raw assets contained disparate note templates, scratchpad brainstorming notes, and unclassified PDF documents. Merging these documents produces a formal R&D incubation framework with an objective scoring scorecard, ensuring that speculative ideas are systematically evaluated and promoted.

### Superiority Justification
- **Objective Mathematical Scoring**: Replaces subjective enthusiasm with a quantifiable 4-factor scoring rubric.
- **Strict 48-Hour Timeboxing**: Enforces that initial POCs must be built within 48 hours or discarded to prevent project sprawl.
- **Seamless Second Brain Indexing**: Uses standard Obsidian MOC link schemas to maintain visual relationships across all research nodes.

---

# Core Implementations & Code Artifacts

### 1. Idea Scorecard & Incubation Evaluator (`idea_evaluator.py`)

```python
"""
idea_evaluator.py - Automated R&D Incubator Idea Scorecard & Graduation Sieve
Evaluates speculative projects across feasibility, MVP velocity, monetization, and synergy.
"""

from typing import Dict, Any, List

class IdeaIncubator:
    def __init__(self):
        pass

    def evaluate_idea(
        self,
        name: str,
        technical_feasibility: int,  # 1 - 10
        speed_to_mvp_hours: int,     # Hours required to build basic POC
        monetization_potential: int, # 1 - 10
        strategic_synergy: int       # 1 - 10
    ) -> Dict[str, Any]:
        # Scoring Weights:
        # Feasibility: 30%, MVP Speed: 30%, Monetization: 25%, Synergy: 15%
        
        # Velocity score: <24h = 10, <48h = 8, <100h = 5, >100h = 2
        if speed_to_mvp_hours <= 24:
            velocity_score = 10
        elif speed_to_mvp_hours <= 48:
            velocity_score = 8
        elif speed_to_mvp_hours <= 100:
            velocity_score = 5
        else:
            velocity_score = 2

        composite_score = (
            (technical_feasibility * 10 * 0.30) +
            (velocity_score * 10 * 0.30) +
            (monetization_potential * 10 * 0.25) +
            (strategic_synergy * 10 * 0.15)
        )

        composite_score = round(composite_score, 1)

        if composite_score >= 80.0:
            status = "GRADUATE_TO_ACTIVE_DEV"
            action = "Build 48-hour prototype immediately and scaffold into active domain."
        elif composite_score >= 65.0:
            status = "INCUBATE_AND_SPIKE"
            action = "Conduct focused technical research to resolve feasibility questions."
        else:
            status = "PARK_IN_BACKLOG"
            action = "Archive idea in Cold Storage until prerequisite tools mature."

        return {
            "idea_name": name,
            "composite_score": composite_score,
            "status": status,
            "recommended_action": action,
            "metrics": {
                "technical_feasibility": technical_feasibility,
                "speed_to_mvp_hours": speed_to_mvp_hours,
                "monetization_potential": monetization_potential,
                "strategic_synergy": strategic_synergy
            }
        }

if __name__ == "__main__":
    incubator = IdeaIncubator()
    sample_eval = incubator.evaluate_idea(
        name="Automated YouTube Comment Lead Harvester",
        technical_feasibility=9,
        speed_to_mvp_hours=16,
        monetization_potential=8,
        strategic_synergy=9
    )
    print("Incubation Evaluation:\n", sample_eval)
```

---

# Parameterized Prompt Decks & Templates

### Rapid 48-Hour Prototype Spike Planner
```markdown
ROLE: Principal Research Engineer & Rapid Prototyper.

RAW EXPERIMENT IDEA: {{IDEA_NAME}}
CORE HYPOTHESIS: {{CORE_HYPOTHESIS}}
TARGET PREREQUISITES / APIs: {{APIS_AND_TOOLS}}

PLANNING INSTRUCTIONS:
Create a lean, 48-Hour Technical Spike Blueprint:
1. **Core Assumption to Validate**: What single technical assumption must be proven true for this project to succeed?
2. **Minimal Viable Script Architecture**: A single Python file or 3-node n8n workflow that validates this assumption.
3. **Pass / Fail Threshold**: Explicit numeric criteria to declare the prototype a success or failure.
4. **48-Hour Milestone Schedule**:
   - Hour 0–12: Environment setup & API key verification.
   - Hour 12–36: Core script implementation.
   - Hour 36–48: Test runs & decision gate.
```

---

# Deployment SOP & Operational Guide

1. **Log New Idea**: Capture the idea in Obsidian using `moc_template.md`.
2. **Run Scorecard**: Evaluate the idea with `idea_evaluator.py`.
3. **Timebox Spike**: If score >= 80, allocate a 48-hour sprint to build the minimal POC.
4. **Graduate or Archive**: Promote successful POCs to their target domain or move them to `04_Archive_Cold_Storage/`.

---

# Failure Modes, Edge Cases & Troubleshooting

| Incubator Anti-Pattern | Manifestation | Remedy |
|---|---|---|
| **Endless Architecture Planning** | Writing 20 pages of specs without running code. | Hard rule: no spec can exceed 2 pages before a working Python script is executed. |
| **Sunk Cost Trap on Failed Spikes** | Refusing to abandon an idea after the 48h spike fails. | Strict adherence to the Pass/Fail threshold: if the API or library fails during the spike, archive immediately. |
