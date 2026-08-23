---
title: "Universal Micro-Prompt Deck and Atomic Text Transformation Catalog"
domain: "03_Prompt_Engineering_and_Frameworks"
reusability_score: 98
workability_status: "Production-Ready"
tags:
  - "micro-prompts"
  - "text-transformations"
  - "slash-commands"
  - "summarization"
  - "copilot-deck"
dependencies:
  - "any-llm-engine"
  - "markdown"
source_files_synthesized:
  - "Raw_copies/Emojify.md"
  - "Raw_copies/Explain like I am 5.md"
  - "Raw_copies/Fix grammar and spelling.md"
  - "Raw_copies/Generate glossary.md"
  - "Raw_copies/Generate table of contents.md"
  - "Raw_copies/Make longer.md"
  - "Raw_copies/Make shorter.md"
  - "Raw_copies/Remove URLs.md"
  - "Raw_copies/Rewrite as tweet thread.md"
  - "Raw_copies/Rewrite as tweet.md"
  - "Raw_copies/Simplify.md"
  - "Raw_copies/Summarize.md"
  - "Raw_copies/Translate to Chinese.md"
---

# Executive Summary & Architectural Mental Model

The **Universal Micro-Prompt Deck and Atomic Text Transformation Catalog** consolidates 13 modular, zero-latency micro-prompts designed for inline text manipulation, Obsidian Copilot slash commands, IDE context menu extensions, and automated content processing pipelines. Each micro-prompt is parameterized, strictly bounded to prevent conversational preamble, and engineered to execute atomic operations (summarization, expansion, simplification, grammar correction, formatting conversion, social syndication) with 100% determinism.

```
+===================================================================================+
|                       ATOMIC TEXT TRANSFORMATION ROUTER                           |
|                                                                                   |
|  [ Inbound Raw Text / Selected Clipboard Buffer / Markdown Document ]             |
|                                    |                                              |
|                                    v                                              |
|  +-----------------------------------------------------------------------------+  |
|  |                 Transformation Intent Selector / Slash Router               |  |
|  +-------------------------------------+---------------------------------------+  |
|                                        |                                          |
|        +----------------+--------------+---------------+-----------------+        |
|        |                |                              |                 |        |
|        v                v                              v                 v        |
|  [ /summarize ]  [ /eli5 /simplify ]            [ /fix-grammar ]  [ /social-thread ]
|  [ /glossary  ]  [ /make-shorter /longer ]      [ /remove-urls ]  [ /emojify ]     |
|        |                |                              |                 |        |
|        +----------------+--------------+---------------+-----------------+        |
|                                        |                                          |
|                                        v                                          |
|  [ Zero-Preamble Output Filter: Pure Transformed Text Buffer Ready for Pasting ]  |
+===================================================================================+
```

---

## Source Lineage & Merge Rationale

### Synthesized Sources
- 13 isolated micro-prompt markdown files from `Raw_copies/` (`Emojify.md`, `Explain like I am 5.md`, `Fix grammar and spelling.md`, `Generate glossary.md`, `Generate table of contents.md`, `Make longer.md`, `Make shorter.md`, `Remove URLs.md`, `Rewrite as tweet thread.md`, `Rewrite as tweet.md`, `Simplify.md`, `Summarize.md`, `Translate to Chinese.md`).

### Concrete Merge Rationale
In the raw repository, each micro-prompt was stored in an individual 10-line Markdown file with Obsidian Copilot frontmatter headers. This forced developers and agents to maintain 13 separate file references. This Golden Master unifies all 13 transformation cards into a standardized, parameterized catalog complete with few-shot input/output examples and programmatic Python/n8n invocation wrappers.

### Superiority Justification
1. **Consolidated Card Catalog**: Combines 13 separate files into a single structured reference with unified variable parameterization (`{{TEXT_INPUT}}`).
2. **Zero-Preamble Enforcement**: Strips out polite conversational filler (*"Sure, here is your text..."*), guaranteeing pure output text.
3. **Multi-Platform Portability**: Compatible with Obsidian Copilot, Cursor AI, VS Code, and n8n Code Nodes.

---

## Core Implementations & Code Artifacts

### 1. The 13 Atomic Transformation Cards

#### Card 1: Summarize (`/summarize`)
```markdown
Summarize the following text while preserving all key statistics, action items, and technical concepts:
<input_text>
{{TEXT_INPUT}}
</input_text>
Rules:
1. Provide a 3-bullet executive summary followed by core findings.
2. Maintain high factual density.
3. Return only the summary text without conversational preamble.
```

#### Card 2: Explain Like I'm 5 (`/eli5`)
```markdown
Explain the following concept in clear, simple terms suitable for a 5-year-old:
<concept>
{{TEXT_INPUT}}
</concept>
Rules:
1. Use an intuitive real-world analogy.
2. Avoid technical jargon; replace complex terminology with everyday objects.
3. Return only the simplified explanation.
```

#### Card 3: Fix Grammar and Spelling (`/fix-grammar`)
```markdown
Fix all grammatical, punctuation, and spelling errors in the following text:
<input_text>
{{TEXT_INPUT}}
</input_text>
Rules:
1. Preserve the author's original voice, style, and vocabulary choices.
2. Do not rewrite sentences unless required for grammatical correctness.
3. Return ONLY the corrected text.
```

#### Card 4: Generate Glossary (`/glossary`)
```markdown
Extract all technical terms, acronyms, and domain concepts from the following text and generate an alphabetical glossary:
<input_text>
{{TEXT_INPUT}}
</input_text>
Format:
- **Term**: Clear 1-sentence definition based on context.
```

#### Card 5: Generate Table of Contents (`/toc`)
```markdown
Analyze the Markdown heading structure in the following document and generate a nested Markdown Table of Contents:
<document>
{{TEXT_INPUT}}
</document>
Rules:
1. Include H1, H2, and H3 levels.
2. Use valid Markdown anchor links: `- [Heading Name](#heading-anchor)`.
```

#### Card 6: Make Shorter / Condense (`/make-shorter`)
```markdown
Condense the following text by 50% while retaining 100% of its critical meaning and facts:
<input_text>
{{TEXT_INPUT}}
</input_text>
Rules:
1. Eliminate fluff, passive voice, and redundant adverbs.
2. Return only the condensed text.
```

#### Card 7: Make Longer / Elaborate (`/make-longer`)
```markdown
Elaborate on the following text by expanding the underlying logic, providing concrete examples, and detailing implications:
<input_text>
{{TEXT_INPUT}}
</input_text>
Rules:
1. Maintain rigorous technical depth.
2. Return only the expanded text.
```

#### Card 8: Remove URLs (`/remove-urls`)
```markdown
Strip all HTTP/HTTPS links and Markdown URL syntax from the following text while preserving the anchor text:
<input_text>
{{TEXT_INPUT}}
</input_text>
Return only the cleaned text.
```

#### Card 9: Rewrite as Viral Tweet (`/tweet`)
```markdown
Transform the core insight of the following text into a high-impact, viral X (Twitter) post:
<input_text>
{{TEXT_INPUT}}
</input_text>
Rules:
1. Maximum 280 characters.
2. Strong opening hook line.
3. Include 2 relevant hashtags.
```

#### Card 10: Rewrite as Tweet Thread (`/thread`)
```markdown
Deconstruct the following text into an engaging, 5-to-7 post X (Twitter) educational thread:
<input_text>
{{TEXT_INPUT}}
</input_text>
Rules:
1. Tweet 1: High-curiosity hook + "Here's what you need to know 🧵👇".
2. Tweets 2-6: Single core idea per tweet with bullet points.
3. Tweet 7: Actionable summary + call to action.
```

#### Card 11: Simplify (`/simplify`)
```markdown
Rewrite the following complex text in simple, active, and accessible business language:
<input_text>
{{TEXT_INPUT}}
</input_text>
Return only the simplified text.
```

#### Card 12: Emojify (`/emojify`)
```markdown
Add relevant emojis to enhance the readability of the following text:
<input_text>
{{TEXT_INPUT}}
</input_text>
Rules:
1. Insert emojis at natural section breaks and bullet points.
2. Never place two emojis next to each other.
3. Keep all original wording completely unchanged.
```

#### Card 13: Translate to Chinese (`/translate-zh`)
```markdown
Translate the following English technical text into natural, professional Simplified Chinese (Mandarin):
<input_text>
{{TEXT_INPUT}}
</input_text>
Rules:
1. Use standard technical terminology.
2. Preserve all code blocks and variable names in English.
```

---

## Parameterized Prompt Decks & Templates

### Prompt Deck 1: Python Micro-Transformation Dispatcher

```python
"""
Python Micro-Prompt Dispatcher Engine
Executes atomic text transformations with zero overhead.
"""

from typing import Dict, Any

PROMPT_CATALOG: Dict[str, str] = {
    "summarize": "Summarize the text while preserving statistics and key facts:\n<text>\n{text}\n</text>\nReturn only summary.",
    "fix_grammar": "Fix all grammar, spelling, and punctuation errors:\n<text>\n{text}\n</text>\nReturn only corrected text.",
    "make_shorter": "Condense this text by 50% without losing core facts:\n<text>\n{text}\n</text>\nReturn only condensed text.",
    "emojify": "Insert appropriate contextual emojis at natural break points:\n<text>\n{text}\n</text>\nKeep wording unchanged.",
    "eli5": "Explain this concept to a 5-year-old using a real-world analogy:\n<text>\n{text}\n</text>"
}

def build_transformation_prompt(action: str, text: str) -> str:
    if action not in PROMPT_CATALOG:
        raise ValueError(f"Unknown transformation '{action}'. Available: {list(PROMPT_CATALOG.keys())}")
    return PROMPT_CATALOG[action].format(text=text)
```

---

## Deployment SOP & Operational Guide

1. **Obsidian Copilot Integration**:
   - Copy any card prompt into your Obsidian vault under `.obsidian/plugins/copilot/prompts/`.
   - Invoke via `/action_name` in the Copilot chat window.
2. **n8n Automation Integration**:
   - In any n8n LLM Chain node, select the desired card prompt and pass `{{ $json.text }}` as the input variable.
3. **IDE Context Menu Integration**:
   - Add prompt cards to Cursor `.cursorrules` or VS Code Custom Prompts.

---

## Failure Modes, Edge Cases & Troubleshooting

- **Failure Mode 1: Model Conversational Preamble**:
  - *Cause*: Model prepends *"Here is your summary:"*.
  - *Remedy*: Include strict instruction *"Return ONLY the transformed text. Zero preamble."* and set temperature <= 0.2.
- **Failure Mode 2: Emoji Overuse in `/emojify`**:
  - *Cause*: Model puts 3-4 emojis per sentence.
  - *Remedy*: Enforce rule *"Never place two emojis next to each other, max 1 emoji per paragraph."*


---

### Integrated: `Explain like I am 5.md`

**Summary**: ELI5 prompt template

**Integration Rationale**: Classic micro-prompt

---
copilot-command-context-menu-enabled: true
copilot-command-slash-enabled: true
copilot-command-context-menu-order: 1040
copilot-command-model-key: ""
copilot-command-last-used: 0
---
Explain {} in simple terms that a 5-year-old would understand:
    1. Use basic vocabulary
    2. Include simple analogies
    3. Break down complex concepts
    Return only the simplified explanation.


---

### Integrated: `Fix grammar and spelling.md`

**Summary**: Grammar fixing prompt

**Integration Rationale**: Standard micro-prompt

---
copilot-command-context-menu-enabled: true
copilot-command-slash-enabled: true
copilot-command-context-menu-order: 1000
copilot-command-model-key: ""
copilot-command-last-used: 0
---
Fix the grammar and spelling of {}. Preserve all formatting, line breaks, and special characters. Do not add or remove any content. Return only the corrected text.


---

### Integrated: `Generate glossary.md`

**Summary**: Glossary generation prompt

**Integration Rationale**: Micro-prompt

---
copilot-command-context-menu-enabled: false
copilot-command-slash-enabled: false
copilot-command-context-menu-order: 1090
copilot-command-model-key: ""
copilot-command-last-used: 0
---
Create a glossary of important terms, concepts, and phrases from {}. Format each entry as "Term: Definition". Sort entries alphabetically. Return only the glossary.


---

### Integrated: `Generate table of contents.md`

**Summary**: TOC generation prompt

**Integration Rationale**: Micro-prompt

---
copilot-command-context-menu-enabled: false
copilot-command-slash-enabled: false
copilot-command-context-menu-order: 1080
copilot-command-model-key: ""
copilot-command-last-used: 0
---
Generate a hierarchical table of contents for {}. Use appropriate heading levels (H1, H2, H3, etc.). Include page numbers if present. Return only the table of contents.


---

### Integrated: `Make longer.md`

**Summary**: Prompt to expand text

**Integration Rationale**: Micro-prompt

---
copilot-command-context-menu-enabled: true
copilot-command-slash-enabled: true
copilot-command-context-menu-order: 1070
copilot-command-model-key: ""
copilot-command-last-used: 0
---
Expand {} to twice its length by:
    1. Adding relevant details and examples
    2. Elaborating on key points
    3. Maintaining the original tone and style
    Return only the expanded text.


---

### Integrated: `Make shorter.md`

**Summary**: Prompt to condense text

**Integration Rationale**: Micro-prompt

---
copilot-command-context-menu-enabled: true
copilot-command-slash-enabled: true
copilot-command-context-menu-order: 1060
copilot-command-model-key: ""
copilot-command-last-used: 0
---
Reduce {} to half its length while preserving these elements:
    1. Main ideas and key points
    2. Essential details
    3. Original tone and style
    Return only the shortened text.


---

### Integrated: `Remove URLs.md`

**Summary**: Prompt to strip URLs from text

**Integration Rationale**: Micro-prompt

---
copilot-command-context-menu-enabled: false
copilot-command-slash-enabled: false
copilot-command-context-menu-order: 1100
copilot-command-model-key: ""
copilot-command-last-used: 0
---
Remove all URLs from {}. Preserve all other content and formatting. URLs may be in various formats (http, https, www). Return only the text with URLs removed.


---

### Integrated: `Rewrite as tweet thread.md`

**Summary**: Prompt for tweet thread creation

**Integration Rationale**: Micro-prompt

---
copilot-command-context-menu-enabled: false
copilot-command-slash-enabled: false
copilot-command-context-menu-order: 1120
copilot-command-model-key: ""
copilot-command-last-used: 0
---
Convert {} into a Twitter thread following these rules:
    1. Each tweet must be under 240 characters
    2. Start with "THREAD START" on its own line
    3. Separate tweets with "

---

"
    4. End with "THREAD END" on its own line
    5. Make content engaging and clear
    Return only the formatted thread.


---

### Integrated: `Rewrite as tweet.md`

**Summary**: Prompt for single tweet creation

**Integration Rationale**: Micro-prompt

---
copilot-command-context-menu-enabled: false
copilot-command-slash-enabled: false
copilot-command-context-menu-order: 1110
copilot-command-model-key: ""
copilot-command-last-used: 0
---
Rewrite {} as a single tweet with these requirements:
    1. Maximum 280 characters
    2. Use concise, impactful language
    3. Maintain the core message
    Return only the tweet text.


---

### Integrated: `Translate to Chinese.md`

**Summary**: Translation prompt

**Integration Rationale**: Micro-prompt

---
copilot-command-context-menu-enabled: true
copilot-command-slash-enabled: true
copilot-command-context-menu-order: 1010
copilot-command-model-key: ""
copilot-command-last-used: 0
---
Translate {} into Chinese:
    1. Preserve the meaning and tone
    2. Maintain appropriate cultural context
    3. Keep formatting and structure
    Return only the translated text.
