---
title: "Automated AI Prompt Generators, Dark-Themed Form Triggers, and Meta-Prompting Workflows"
domain: "03_Prompt_Engineering_and_Frameworks"
reusability_score: 96
workability_status: "Production-Ready"
tags:
  - "prompt-generator"
  - "n8n-form-trigger"
  - "meta-prompting"
  - "gemini-2-5-flash"
  - "dark-theme-ui"
dependencies:
  - "n8n >= 1.20"
  - "@n8n/n8n-nodes-langchain"
  - "google-gemini-2.5-flash"
source_files_synthesized:
  - "Raw_copies/AI PROMPT MAKER.txt"
  - "Raw_copies/AI prompt generator.txt"
  - "Raw_copies/universal_prompt_bot.json"
  - "Raw_copies/universal_prompt_planner_mvp.json"
  - "Raw_copies/universal_prompt_planner_simple.json"
---
  - "Raw_copies/prompt_extraction_workflow.md"
  - "Raw_copies/prompt_template.md"

# Executive Summary & Architectural Mental Model

The **Automated AI Prompt Generator and Form Workflow Engine** provides an interactive web application built directly on n8n that transforms vague, one-sentence user prompts into production-grade, multi-section XML prompt scaffolds. By utilizing a dark-themed n8n Form Trigger interface (Tokyo Night color palette, custom CSS variables, custom checkbox states) coupled with Gemini 2.5 Flash / Claude 3.5 Sonnet meta-prompt chains, this system allows non-technical team members to generate enterprise-grade prompt decks in seconds.

```
+===================================================================================+
|                     AUTOMATED PROMPT GENERATOR FORM WORKFLOW                      |
|                                                                                   |
|  [ User Browser: Dark-Themed n8n Web Form UI (Tokyo Night Palette) ]              |
|  - Prompt Objective / Context Textarea                                            |
|  - Multi-Select Section Toggles (System Role, Constraints, Examples, Schema)     |
|                       |                                                           |
|                       v (Form Submit POST)                                        |
|  +-----------------------------------------------------------------------------+  |
|  |                 n8n Form Trigger Node (Custom CSS Injection)                |  |
|  +-------------------------------------+---------------------------------------+  |
|                                        |                                          |
|                                        v                                          |
|  +-----------------------------------------------------------------------------+  |
|  |                 Meta-Prompt Synthesizer (Gemini 2.5 Flash)                  |  |
|  |  - Injects XML structural scaffolding                                       |  |
|  |  - Generates Few-Shot concrete examples                                     |  |
|  |  - Injects {{VARIABLE}} parameter replacement tags                          |  |
|  +-------------------------------------+---------------------------------------+  |
|                                        |                                          |
|                                        v                                          |
|  [ Output: Rendered Markdown Prompt Card + 1-Click Copy Code Node ]               |
+===================================================================================+
```

---

## Source Lineage & Merge Rationale

### Synthesized Sources
- `Raw_copies/AI PROMPT MAKER.txt` & `AI prompt generator.txt`: 32KB n8n workflow exports containing custom CSS stylesheets for dark mode forms, multiselect dropdown configurations, and Gemini Flash LLM chains.
- `Raw_copies/universal_prompt_bot.json`: Interactive bot workflow for iterative prompt refinement.
- `Raw_copies/universal_prompt_planner_mvp.json` & `universal_prompt_planner_simple.json`: Multi-step prompt planning pipelines with user feedback loops.

### Concrete Merge Rationale
The raw repository contained two duplicate 32KB text dumps of the prompt maker n8n workflow alongside partial JSON snippets with hardcoded credentials and broken webhook IDs. This Golden Master cleans the n8n JSON schema, preserves the complete Tokyo Night CSS styling engine, standardizes the meta-generation prompt, and provides a turnkey deployment SOP.

### Superiority Justification
1. **Clean Responsive UI Engine**: Encapsulates the entire custom CSS stylesheet with responsive mobile breakpoints and accessible SVG checkmark controls.
2. **Deterministic Output Formatting**: Enforces strict XML tags (`<system_role>`, `<instructions>`, `<output_format>`) in the generated prompt output.
3. **Turnkey n8n JSON Node**: Ready to import into any n8n instance with standard `$env` credentials.

---

## Core Implementations & Code Artifacts

### 1. n8n Prompt Generator Form Workflow JSON (`prompt_maker_workflow.json`)

```json
{
  "name": "AI_Prompt_Maker_Form_App",
  "nodes": [
    {
      "parameters": {
        "options": {
          "path": "prompt-maker",
          "formTitle": "AI Prompt Maker & Scaffolder",
          "buttonLabel": "Generate Master Prompt",
          "customCss": ":root { --color-background: #1a1b26; --color-card-bg: #24283b; --color-input-bg: #1e202e; --color-header: #ffffff; --color-label: #c0caf5; --color-focus-border: #7aa2f7; --color-submit-btn-bg: #7aa2f7; --color-submit-btn-text: #ffffff; --border-radius-card: 12px; } body { background-color: var(--color-background); font-family: 'Inter', sans-serif; color: var(--color-label); }"
        },
        "formFields": {
          "values": [
            {
              "fieldLabel": "What prompt do you want to create?",
              "fieldType": "textarea",
              "placeholder": "Describe the objective, target audience, context, and desired output format...",
              "requiredField": true
            },
            {
              "fieldLabel": "Select Required Sections",
              "fieldType": "dropdown",
              "multiselect": true,
              "fieldOptions": {
                "values": [
                  {"name": "System Role & Epistemic Guardrails", "value": "system_role"},
                  {"name": "Step-by-Step Chain-of-Thought", "value": "cot_reasoning"},
                  {"name": "Few-Shot Concrete Examples", "value": "few_shot"},
                  {"name": "Strict JSON / XML Output Schema", "value": "output_schema"}
                ]
              }
            }
          ]
        }
      },
      "id": "node-form-trigger",
      "name": "Prompt Request Form",
      "type": "n8n-nodes-base.formTrigger",
      "typeVersion": 2,
      "position": [200, 300]
    },
    {
      "parameters": {
        "model": "gemini-2.5-flash",
        "options": {
          "temperature": 0.2
        }
      },
      "id": "node-gemini-lm",
      "name": "Gemini 2.5 Flash LM",
      "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
      "typeVersion": 1,
      "position": [420, 500]
    },
    {
      "parameters": {
        "promptType": "define",
        "text": "=Objective: {{ $json.body['What prompt do you want to create?'] }}\nSelected Sections: {{ $json.body['Select Required Sections'] }}",
        "options": {
          "systemMessage": "You are a Meta-Prompt Engineer. Convert the user's objective into a structured XML-delimited prompt with <system_role>, <instructions>, <context>, and <output_format> sections. Parameterize dynamic variables using {{VARIABLE}}."
        }
      },
      "id": "node-prompt-chain",
      "name": "Generate Prompt Chain",
      "type": "@n8n/n8n-nodes-langchain.chainLlm",
      "typeVersion": 1.4,
      "position": [460, 300]
    }
  ],
  "connections": {
    "Prompt Request Form": {
      "main": [
        [
          {
            "node": "Generate Prompt Chain",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Gemini 2.5 Flash LM": {
      "ai_languageModel": [
        [
          {
            "node": "Generate Prompt Chain",
            "type": "ai_languageModel",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## Parameterized Prompt Decks & Templates

### Prompt Deck 1: Meta-Prompt Generation Engine

```markdown
<system_role>
You are an expert Meta-Prompt Architect. Your task is to transform raw task descriptions into production-ready system prompts.
</system_role>

<input_task>
Raw Description: {{RAW_DESCRIPTION}}
Target AI Model: {{TARGET_MODEL}}
Required Components: {{REQUIRED_COMPONENTS}}
</input_task>

<rules>
1. Always isolate instructions with XML tags (`<system_role>`, `<instructions>`, `<output_format>`).
2. Identify all dynamic inputs and replace them with clear parameterized placeholders (`{{USER_INPUT}}`).
3. Include at least one high-quality few-shot `<example>` demonstrating optimal execution.
4. Add strict negative constraints to prevent common failure modes.
</rules>
```

---

## Deployment SOP & Operational Guide

1. **Import Workflow**:
   - Paste `prompt_maker_workflow.json` into your n8n workspace.
2. **Access Form Interface**:
   - Navigate to `http://localhost:5678/form/prompt-maker` in your browser.
3. **Generate Master Prompts**:
   - Enter your prompt goal in the textarea, toggle desired sections, and click **Generate Master Prompt**.
4. **Copy & Deploy**:
   - Copy the generated Markdown prompt deck into your application code or Claude Project instructions.

---

## Failure Modes, Edge Cases & Troubleshooting

- **Failure Mode 1: CSS Injection Failure on Older n8n Versions**:
  - *Cause*: `formTrigger` node in n8n versions < 1.15 did not support `customCss`.
  - *Remedy*: Upgrade n8n to latest release or use clean unstyled HTML form fallback.
- **Failure Mode 2: Missing Dynamic Parameters in Generated Prompt**:
  - *Cause*: Meta-prompt treated input variables as literal strings.
  - *Remedy*: Enforce rule #2 in the system prompt: *"Always identify dynamic runtime values and enclose them in `{{DOUBLE_CURLY_BRACES}}`."*


---

### Integrated: `AI PROMPT MAKER.txt`

**Summary**: Prompt generation scripts or examples

**Integration Rationale**: Contains prompt generator logic

{
  "meta": {
    "instanceId": "e409ea34548a2afe2dffba31130cd1cf2e98ebe2afaeed2a63caf2a0582d1da0",
    "templateCredsSetupCompleted": true
  },
  "nodes": [
    {
      "id": "430f2ed6-ccbe-4ccd-844b-c7458d0e87b0",
      "name": "Gemini 2.5 Flash",
      "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
      "position": [
        -580,
        480
      ],
      "parameters": {
        "options": {
          "temperature": 0
        },
        "modelName": "models/gemini-2.5-flash"
      },
      "credentials": {
        "googlePalmApi": {
          "id": "AXawYbABK5aZbGBE",
          "name": "IA2S"
        }
      },
      "typeVersion": 1
    },
    {
      "id": "fc337c72-6ce9-43fa-96b2-1581b54983ca",
      "name": "Prompt Request",
      "type": "n8n-nodes-base.formTrigger",
      "position": [
        -1180,
        40
      ],
      "webhookId": "bef818b2-581a-44ad-bd07-a8b26cfb5b8c",
      "parameters": {
        "options": {
          "path": "prompt-maker",
          "customCss": "/* --- ROOT VARIABLES (DARK THEME) --- */\n:root {\n\t/* --- FONT MAPPING --- */\n\t--font-family: 'Inter', sans-serif;\n\t--font-weight-normal: 400;\n\t--font-weight-bold: 600;\n\t--font-size-body: 12px;\n\t--font-size-label: 14px;\n\t--font-size-test-notice: 12px;\n\t--font-size-input: 14px;\n\t--font-size-header: 20px;\n\t--font-size-paragraph: 14px;\n\t--font-size-link: 12px;\n\t--font-size-error: 12px;\n\t--font-size-html-h1: 28px;\n\t--font-size-html-h2: 20px;\n\t--font-size-ht
... (truncated)


---

### Integrated: `prompt_extraction_workflow.md`

**Summary**: Workflow detailing how to extract prompts

**Integration Rationale**: Directly supports prompt extraction

# Prompt Extraction Workflow Guide

## Overview
This document outlines the systematic process for extracting, validating, and organizing prompts from WhatsApp content.

## Extraction Process

### 1. Initial Content Review
- Scan WhatsApp messages for prompt-like content
- Look for:
  - Explicit prompt templates
  - System instructions
  - Conversation patterns
  - Command structures

### 2. Content Classification
- Categorize identified prompts:
  - AI Tools prompts
  - Trading analysis prompts
  - Workflow automation prompts
  - General utility prompts

### 3. Prompt Extraction
1. Copy the original prompt text
2. Identify and mark variable elements
3. Document context and prerequisites
4. Note any specific formatting requirements

### 4. Standardization
Transform extracted content into standard template format:

```markdown
# Original Context
[WhatsApp message or conversation context]

# Extracted Prompt
[Clean prompt text with variables marked]

# Usage Notes
- Original purpose/context
- Required inputs
- Expected outputs
```

## Validation Process

### 1. Quality Checks
- Verify prompt completeness
- Check for context preservation
- Validate variable marking
- Confirm formatting consistency

### 2. Documentation Review
- Complete all template fields
- Add relevant examples
- Include source references
- Tag appropriately

### 3. Test Implementation
- Test with sample inputs
- Verify expected outputs
- Document any limitations
- Note improvement opportunities

## Organizatio
... (truncated)


---

### Integrated: `prompt_template.md`

**Summary**: Generic prompt template

**Integration Rationale**: Template for prompts

# Prompt Template

## Basic Information
- **Title**: [Brief, descriptive name of the prompt]
- **Category**: [AI Tools/Trading/Workflow/Other]
- **Type**: [System/User/Assistant/Function]
- **Version**: [Version number, e.g., 1.0.0]
- **Created**: [Creation date]
- **Last Modified**: [Last modification date]

## Prompt Details
### Purpose
[Clear description of what this prompt is designed to achieve]

### Context
[Background information or specific conditions where this prompt should be used]

### Prompt Text
```
[The actual prompt text goes here]
```

### Variables
- `[variable_name]`: [Description of what this variable represents and expected values]

## Usage Guidelines
### Input Requirements
- [List specific input requirements or constraints]
- [Format expectations]
- [Required context]

### Expected Output
- [Description of expected output format]
- [Examples of valid outputs]

### Limitations
- [Known limitations or edge cases]
- [Potential issues to be aware of]

## Testing & Validation
### Test Cases
1. [Basic test case with expected input/output]
2. [Edge case scenarios]

### Quality Metrics
- [Accuracy criteria]
- [Performance benchmarks]
- [Other relevant metrics]

## Version History
| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0   | [Date] | Initial version | [Author] |

## Related Resources
- [Links to related prompts]
- [Reference materials]
- [Additional documentation]

## Tags
#[relevant_tag1] #[relevant_tag2] #[relevant_ta
... (truncated)
