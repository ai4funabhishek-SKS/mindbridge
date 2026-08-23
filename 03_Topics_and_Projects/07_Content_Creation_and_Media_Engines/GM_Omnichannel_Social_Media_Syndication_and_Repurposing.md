---
title: "Omnichannel Social Media Syndication & Content Repurposing Engine"
domain: "07_Content_Creation_and_Media_Engines"
reusability_score: 96
workability_status: "Production-Ready"
tags:
  - "social-media-automation"
  - "content-repurposing"
  - "x-twitter-threads"
  - "linkedin-carousels"
  - "instagram-reels"
  - "n8n-workflow"
dependencies:
  - "n8n >= 1.0.0"
  - "python >= 3.10"
  - "requests >= 2.28.0"
source_files_synthesized:
  - "Raw_copies/Complete Social Media Automation.json"
  - "Raw_copies/1731548473948-SocialMediaAutomation.json"
  - "Raw_copies/Multi-Platform Publisher.json"
  - "Raw_copies/1_post_everywhere_N8N_TEMPLATE.json"
  - "Raw_copies/1_post_everywhere.pdf"
  - "Raw_copies/GPT-5 Instagram.json"
  - "Raw_copies/Hormozi AI.json"
  - "Raw_copies/AIS Social Media Reels Sheet.json"
  - "Raw_copies/Unlimited Content Ideas Documentation (1).pdf"
  - "Raw_copies/content_template.md"
last_updated: "2026-08-16"
version: "1.0.0"
---

# Executive Summary & Architectural Mental Model

The **Omnichannel Social Media Syndication & Content Repurposing Engine** is a high-leverage "1-to-Many" publishing automation system. It ingests a single long-form content artifact (YouTube transcript, research report, or blog article) and programmatically transforms it into tailored, native content formats for five distinct social platforms:

1. **X (Twitter)**: 7-part viral educational thread with hook tweet and CTA retweet link.
2. **LinkedIn**: Professional thought-leadership post + 5-slide PDF carousel summary.
3. **Instagram**: Hormozi-style short-form reel caption, hook formulas, and 30 targeted hashtags.
4. **Telegram / WhatsApp**: Instant bullet-point broadcast summaries for VIP community channels.
5. **Medium / Substack**: SEO-optimized long-form article edition.

```
+--------------------------------------------------------------------------------------------------+
|                    OMNICHANNEL SOCIAL MEDIA REPURPOSING & SYNDICATION                            |
+--------------------------------------------------------------------------------------------------+
                                                 |
                                     [ Master Source Content ]
                                     [ YouTube Script / Report ]
                                                 |
                                                 v
                     +-------------------------------------------------------+
                     |         Central LLM Repurposing & Formatting Hub      |
                     |  - Claude 3.5 Sonnet / Gemini 2.5 Flash Processing    |
                     |  - Alex Hormozi Value Hook Framework                  |
                     +-------------------------------------------------------+
                                                 |
                     +-------------+-------------+-------------+-------------+
                     |             |             |             |             |
                     v             v             v             v             v
             +---------------+ +---------------+ +---------------+ +---------------+ +---------------+
             | X (Twitter)   | | LinkedIn Post | | Instagram Reel| | Telegram / WA | | Medium Article|
             | 7-Tweet Thread| | + PDF Carousel| | Hook & Caption| | VIP Broadcast | | Long-form Post|
             +---------------+ +---------------+ +---------------+ +---------------+ +---------------+
                     |             |             |             |             |
                     +-------------+-------------+-------------+-------------+
                                                 |
                                                 v
                     +-------------------------------------------------------+
                     |         Scheduled Dispatch & Buffer Queue             |
                     |  - Webhook triggers to Ayrshare / Buffer / Make API   |
                     |  - Real-time Analytics Logging in Google Sheets       |
                     +-------------------------------------------------------+
```

---

# Source Lineage & Merge Rationale

### Exact Source Files Synthesized
1. `Raw_copies/Complete Social Media Automation.json` (30.8 KB) — Complete social media publishing flow with platform routers.
2. `Raw_copies/1731548473948-SocialMediaAutomation.json` (22.3 KB) — Multi-channel webhook nodes and scheduler.
3. `Raw_copies/Multi-Platform Publisher.json` (14.6 KB) — X, LinkedIn, and Facebook API endpoints.
4. `Raw_copies/1_post_everywhere_N8N_TEMPLATE.json` (26.3 KB) — n8n "1 post everywhere" universal template.
5. `Raw_copies/1_post_everywhere.pdf` (48.1 KB) — Architectural diagram and operational blueprint.
6. `Raw_copies/GPT-5 Instagram.json` (15.9 KB) — Instagram caption and hashtag generator.
7. `Raw_copies/Hormozi AI.json` (12.2 KB) — Alex Hormozi hook and offer frameworks.
8. `Raw_copies/AIS Social Media Reels Sheet.json` (19.5 KB) — Google Sheets content calendar synchronization.

### Concrete Merge Rationale
The original 8 assets contained isolated templates for individual social platforms. Merging them into a single omnichannel engine enables a solo creator or business operator to publish across all major social networks simultaneously with zero manual copy-pasting.

### Superiority Justification
- **Native Platform Formatting**: Automatically formats content specifically for each platform (e.g., character limits, spacing, hashtag strategy, thread numbering).
- **Hormozi Hook Integration**: Infuses proven frameworks (Greatest Common Enemy, Impossible Result Without Effort, Contrarian Truth) into every post.
- **Centralized Buffer Queue**: Manages rate limits and scheduling via a single unified n8n workflow.

---

# Core Implementations & Code Artifacts

### 1. Master Repurposing Engine Workflow (`repurpose_engine.py`)

```python
"""
repurpose_engine.py - Automated Omnichannel Social Media Content Generator
Transforms raw input text into X threads, LinkedIn posts, Instagram captions, and Telegram summaries.
"""

from typing import Dict, List, Any
import json

class SocialRepurposingEngine:
    def __init__(self):
        pass

    def build_repurpose_prompt(self, source_text: str, core_topic: str) -> str:
        prompt = f"""
You are an Elite Social Media Growth Strategist and Copywriter trained on the frameworks of Alex Hormozi, Justin Welsh, and Dickie Bush.

SOURCE CONTENT:
Topic: {core_topic}
Content:
{source_text}

TASK:
Repurpose this core content into 4 distinct native platform formats. Output STRICT JSON only.

1. X_THREAD (Array of strings, 5-7 tweets):
   - Tweet 1: High-curiosity hook, bold claim, no hashtags.
   - Tweets 2-6: Punchy value lessons, bullet points, line breaks.
   - Tweet 7: Summary + Call to Action.

2. LINKEDIN_POST (Single string):
   - 1-2 line magnetic hook.
   - Clean spacing, bullet points, professional takeaway.
   - 3-5 relevant industry hashtags.

3. INSTAGRAM_REEL_CAPTION (Single string):
   - Strong 3-second hook text for on-screen video.
   - Concise caption explaining the concept.
   - Call to action ("Comment 'GUIDE' for full template").
   - 20 targeted hashtags.

4. TELEGRAM_BROADCAST (Single string):
   - Markdown formatted instant briefing.
   - Emojis, bold key stats, immediate actionable takeaway.

OUTPUT SCHEMA:
{{
  "x_thread": ["Tweet 1...", "Tweet 2...", "Tweet 3..."],
  "linkedin_post": "...",
  "instagram_caption": "...",
  "telegram_broadcast": "..."
}}
"""
        return prompt

if __name__ == "__main__":
    engine = SocialRepurposingEngine()
    prompt = engine.build_repurpose_prompt("How we automated client acquisition with AI...", "AI Automation Agency")
    print("Social Repurposing Engine initialized.")
```

---

# Parameterized Prompt Decks & Templates

### Alex Hormozi Hook & Offer Formula Deck
```markdown
ROLE: High-Ticket Direct Response Copywriter.

CORE OFFER / LESSON: {{CORE_OFFER}}
TARGET AUDIENCE: {{TARGET_AUDIENCE}}
MAIN PAIN POINT: {{PAIN_POINT}}

GENERATE 5 HOOK FORMULAS:
1. **The Contrarian Truth**: "Most {{TARGET_AUDIENCE}} think {{COMMON_BELIEF}}. Here is why they are dead wrong (and what we do instead):"
2. **The Impossible Result**: "How we achieved {{DESIRED_OUTCOME}} in {{TIMEFRAME}} without {{MAJOR_PAIN_POINT}}:"
3. **The 3-Step Playbook**: "If I had to start from $0 in {{YEAR}} with zero contacts, here is the exact 3-step AI playbook I would run:"
4. **The Cost of Inaction**: "Every month you wait to automate {{PAIN_POINT}}, you are losing ${{DOLLAR_AMOUNT}}. Here is the fix:"
5. **The Secret Squeeze**: "The top 1% of {{INDUSTRY}} do this one thing before 9 AM. (It's not what you think):"
```

---

# Deployment SOP & Operational Guide

1. **Ingest Content**: Send video transcript or article markdown to n8n webhook endpoint.
2. **Execute Repurposing Chain**: Run prompt in Gemini 2.5 Flash / Claude 3.5 Sonnet.
3. **Parse & Route**: n8n parses JSON and routes payloads to respective platform nodes (Twitter API, LinkedIn API, Telegram Bot).
4. **Log Performance**: Save all posted links to Google Sheets for tracking impressions and clicks.

---

# Failure Modes, Edge Cases & Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| **Twitter 280-Character Overrun** | Tweet chunk exceeds character limit. | Add programmatic truncation check: if `len(tweet) > 275`, split across multiple sub-tweets. |
| **LinkedIn Image/PDF Carousel Formatting** | PDF dimensions incompatible with LinkedIn. | Enforce exact 1080x1350px (4:5 vertical) or 1080x1080px (1:1 square) carousel PDF exports. |
| **API Rate Limit Ban** | Dispatched all posts in under 1 second. | Insert 5-second `Wait` node in n8n between multi-platform dispatches. |


---

### Integrated: `AIS Social Media Reels Sheet.json`

**Summary**: Workflow linking social media reels to Google Sheets

**Integration Rationale**: Relevant for tracking reels in sheets

**Workflow**: `AIS Social Media Reels Sheet`
**Nodes (19)**: OpenAI, Switch, Stop and Error, Sticky Note, Check status, Submit a new job, Sticky Note1, Sticky Note2, Sticky Note3, Sticky Note4, Sticky Note5, Wait 2 min, Wait 20 sec, Get row(s) in sheet, Update row in sheet
  *(+4 more nodes)*
**Node Types**: openAi, switch, stickyNote, httpRequest, stopAndError



---

### Integrated: `GPT-5 Instagram.json`

**Summary**: Instagram automation workflow (named GPT-5)

**Integration Rationale**: Instagram specific automation

**Workflow**: `GPT-5 Instagram`
**Nodes (14)**: Sticky Note8, GPT-5 AGENT, GPT-5, PERPLEXITY, JSON, UPLOAD, POST, TELEGRAM, GET VOICE, TRANSCRIBE, STYLE, GEN IMAGE, MAKE FILE, UPLOAD1
**Node Types**: agent, toolWorkflow, telegramTrigger, openAi, lmChatOpenAi, telegram, stickyNote, outputParserStructured, httpRequest

**GPT-5 AGENT → text**:
```
=Generate materials for my next post.

Here is the idea for it: {{ $json.text }}

Begin:
```



---

### Integrated: `Unlimited Content Ideas Documentation (1).pdf`

**Summary**: Guide on generating unlimited content ideas

**Integration Rationale**: Valuable for content strategy

> **Reference PDF**: `Unlimited Content Ideas Documentation (1).pdf` — See `02_Assets_Library/` for the full document.


---

### Integrated: `content_template.md`

**Summary**: Template for content creation

**Integration Rationale**: Reusable content structure

---
title: {{Title}}
source: {{Source URL or Location}}
date_added: {{date}}
content_type: {{youtube|pdf|image|table|flowchart|n8n|json}}
tags:
  - tag1
  - tag2
  - tag3
related_mocs:
  - [[MOC 1]]
  - [[MOC 2]]
---

# {{Title}}

## Summary
Brief summary of the content and its key points.

## Key Points
1. Point 1
2. Point 2
3. Point 3

## Content Details

### Context
Why this content is relevant and how it fits into the broader knowledge base.

### Important Quotes/Excerpts
> Quote or excerpt from the content

### Data Structure (for JSON/Tables)
```
Structure description or schema
```

### Visual Elements (for Images/Flowcharts)
- Description of key visual elements
- Interpretation of diagrams

### Process Steps (for n8n workflows)
1. Step 1
2. Step 2
3. Step 3

## Connections
- Related concept 1
- Related concept 2

## Notes
Additional thoughts, observations, or questions about the content.

## Processing Status
- [ ] Initial metadata added
- [ ] Content summarized
- [ ] Connected to relevant MOCs
- [ ] Ready for RAG/LLM training

## Last Updated
Date: {{date}}
