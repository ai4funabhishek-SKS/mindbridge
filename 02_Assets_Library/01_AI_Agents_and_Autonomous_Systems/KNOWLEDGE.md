# KNOWLEDGE.md — Knowledge Base Operating Manual
# ZeroClaw APEX | How to Mine Your 1,500-Project Goldmine

---

## THE KNOWLEDGE BASE PHILOSOPHY

You own 1,500 GitHub projects, hundreds of prompts, dozens of n8n JSONs, training videos from the world's best AI creators, official docs, PDFs, and community resources. This is a multi-year head start worth tens of thousands of dollars.

**Rule #1: Never build from scratch if you own something that does it.**
**Rule #2: Check the KB before writing a single line of code or a single word of copy.**
**Rule #3: Every output you create goes back into the KB to help future projects.**

---

## KB ARCHITECTURE — FOUR LAYERS

### Layer 1: Google Drive — Raw Asset Store
**Location:** Google Drive → /EMPIRE-KB/
**What lives here:** Every file, organized by type

```
/EMPIRE-KB/
├── /github-repos/
│   ├── /video-automation/      ← FFmpeg scripts, YouTube bots, video tools
│   ├── /web-builders/          ← Site generators, templates, full-stack starters
│   ├── /ai-agents/             ← Agent frameworks, AutoGPT forks, crew configs
│   ├── /n8n-tools/             ← Custom nodes, workflow utilities
│   ├── /voice-tts/             ← Kokoro, Coqui, voice cloning tools
│   ├── /image-gen/             ← ComfyUI workflows, SD configs
│   ├── /scraping-data/         ← Lead gen, Antigravity configs, scrapers
│   ├── /marketing/             ← SEO tools, social bots, email scripts
│   ├── /ebooks-docs/           ← Document generators, PDF tools
│   └── /mvps/                  ← Your ready-made MVP collection
├── /n8n-workflows/             ← All JSON workflow files, tagged by category
├── /prompt-libraries/          ← All prompt collections, organized by task
├── /training-videos/           ← URLs + timestamps + key learnings
├── /pdfs-docs/                 ← Official docs, community resources, guides
├── /images-assets/             ← Brand assets, stock images, templates
├── /agent-outputs/             ← Where agents save completed work
└── /obsidian-vault/            ← Live sync with Obsidian app
```

### Layer 2: ChromaDB — Semantic Search Engine
**Location:** VPS at http://localhost:8000
**What it does:** Converts all your documents into searchable vectors

When you ask "find me everything about YouTube video automation," ChromaDB searches across all 1,500 repos, all PDFs, all prompts simultaneously and returns ranked results in 2 seconds.

**How to query ChromaDB (Librarian Agent does this for you):**
```python
import chromadb
client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_collection("empire_kb")
results = collection.query(
    query_texts=["YouTube video automation pipeline FFmpeg"],
    n_results=10
)
# Returns: top 10 most relevant documents with metadata
```

### Layer 3: NotebookLM — Deep Topic Intelligence
**Location:** notebooklm.google.com (your Google account)
**What it does:** Deep Q&A and synthesis across curated source documents

**Your 6 Active Notebooks:**
| Notebook | Sources Loaded | Best For |
|----------|----------------|----------|
| YouTube Automation | Training videos, FFmpeg docs, channel strategy guides | Video pipeline decisions |
| Web & App Building | Bolt.DIY docs, OpenCode guides, your web MVPs | Tech stack decisions |
| Ebook Factory | Writing guides, formatting templates, cover design | Ebook production |
| AI Voice Agents | VAPI docs, conversation design, deployment guides | Voice agent builds |
| Marketing & SEO | Copywriting prompts, SEO guides, social playbooks | Marketing decisions |
| DevOps & Infrastructure | VPS guides, Docker docs, n8n workflow library | System decisions |

**Librarian queries NotebookLM like this:**
"Based on the sources in this notebook, what is the fastest way to assemble a kids educational video using FFmpeg with Kokoro TTS voiceover and Pexels stock footage?"

NotebookLM returns: specific steps, relevant source quotes with timestamps, and warnings about edge cases — drawn from your actual training videos and docs.

### Layer 4: Obsidian — Living Memory
**Location:** ~/obsidian-vault/ (synced to Google Drive)
**What it does:** Agent decisions, learnings, templates, and proven configurations

```
/obsidian-vault/
├── /System/
│   ├── API-Keys.md             ← API key reference (encrypted)
│   ├── Agent-Prompts/          ← All proven agent system prompts
│   ├── Approved-Workflows/     ← n8n workflows that have been tested and work
│   └── Performance-Log.md      ← Weekly agent performance scores
├── /Projects/
│   ├── /Active/                ← Current project blueprints
│   ├── /Completed/             ← Archive with results
│   └── /Ideas/                 ← Validated ideas waiting for capacity
├── /Knowledge/
│   ├── /Proven-Prompts/        ← Prompts that produced excellent outputs
│   ├── /Reusable-Components/   ← Code snippets, configs, templates that worked
│   ├── /Niche-Research/        ← Market research by niche
│   └── /Competitor-Intel/      ← Competitor analysis by niche
├── /Revenue/
│   ├── Revenue-Tracker.md      ← Daily/weekly revenue log
│   ├── Products-Live.md        ← All live products with links and revenue
│   └── Clients-Active.md       ← Active client list
└── /Agents/
    ├── /Performance/           ← Per-agent success rate logs
    └── /Improvements/          ← Self-improvement agent weekly reports
```

---

## THE LIBRARIAN AGENT PROTOCOL

Before ANY project begins, you (APEX) trigger the Librarian with this exact payload:

```json
{
  "project_type": "youtube_channel",
  "topic": "kids learning colors ages 0-5",
  "deliverables": ["5 videos", "channel setup", "upload schedule"],
  "search_priority": ["n8n_workflows", "scripts", "ffmpeg", "voice_tts"],
  "return_format": "resource_pack"
}
```

Librarian returns a **Resource Pack**:

```json
{
  "existing_workflows": [
    {
      "name": "youtube-auto-upload-v3.json",
      "location": "/EMPIRE-KB/n8n-workflows/",
      "relevance_score": 0.94,
      "covers": "script to upload pipeline, missing voice synthesis step",
      "time_saved": "4 hours"
    }
  ],
  "relevant_repos": [
    {
      "name": "ffmpeg-kids-video-generator",
      "location": "/EMPIRE-KB/github-repos/video-automation/",
      "stars": 1240,
      "relevance": "exactly matches use case",
      "note": "Uses Python + FFmpeg, needs Kokoro TTS integration"
    }
  ],
  "relevant_prompts": [
    {
      "name": "kids-educational-script-v2.md",
      "location": "/EMPIRE-KB/prompt-libraries/youtube/",
      "proven": true,
      "last_used": "2026-01-15",
      "output_quality": "9/10"
    }
  ],
  "notebooklm_notebook": "YouTube Automation",
  "recommended_query": "What is the fastest pipeline for children's educational YouTube using FFmpeg + Kokoro TTS?",
  "obsidian_prior_decisions": [
    "Kids content: always use warm female voice (Bella profile in Kokoro)",
    "Optimal video length for 0-5 audience: 6-9 minutes",
    "Best upload time: Saturday/Sunday 8-9 AM local time"
  ],
  "estimated_time_saved": "6-8 hours",
  "reuse_recommendation": "Use existing workflow as 80% base, add voice synthesis node"
}
```

---

## KNOWLEDGE BASE QUERY EXAMPLES

### When building a new n8n workflow:
```
Query: "n8n workflow video production pipeline voice synthesis upload"
Expect: 3-5 matching JSON files ranked by relevance
Action: Import highest-scored file, adapt to current project
```

### When writing a YouTube script:
```
Query: "script template educational children colors shapes engaging"
Expect: Existing templates with quality ratings and success history
Action: Use as starting point, customize for this episode
```

### When researching a niche:
```
Query: "market research [niche name] YouTube monetization competition"
Expect: Prior research docs, competitor analysis, relevant training video timestamps
Action: Build on existing research, add fresh data from Grok/Gemini
```

### When building a website:
```
Query: "web template [industry] modern responsive Bolt.DIY"
Expect: Existing MVPs, GitHub repos, template files
Action: Clone closest match, customize with Web Builder Agent
```

---

## INDEXING PROTOCOL — KEEPING KB CURRENT

The Indexing Agent runs every night at 2 AM VPS time.

**What it does:**
1. Scans Google Drive for files added or modified in last 24 hours
2. Chunks each document into 512-token segments
3. Generates embeddings using Gemini text-embedding-004 (free)
4. Stores in ChromaDB with metadata: file_type, category, date_added, quality_score
5. Updates Obsidian with new summary cards for significant additions
6. Notifies APEX of high-value new additions (repos with 1000+ stars, new workflow JSONs)

**Manual indexing trigger (when you add many files at once):**
```
[In n8n] → Trigger "Force Full KB Reindex" webhook
[Via Telegram] → Send "kb reindex" to bot
```

---

## COMPOUND LEARNING PROTOCOL

Every time an agent completes a task:

```
1. APEX evaluates: Was this output good? (QA Agent score)
2. If quality >= 8/10:
   → Extract reusable prompt → save to /obsidian/Knowledge/Proven-Prompts/
   → Extract reusable components → save to /Reusable-Components/
   → Tag and index in ChromaDB
3. If quality < 8/10:
   → Log what went wrong → save to /Agents/Performance/[agent-name]/failures/
   → Flag for Self-Improvement Agent review
4. Always log: which tools used, which LLM chain, time taken, cost
```

**Result:** Every week the KB gets smarter. By Month 3, your system is running on a library of 100+ proven prompts and 50+ proven workflows — none of which need to be rebuilt ever again.

---

## YOUR HIGHEST VALUE EXISTING ASSETS — PRIORITY INDEXING LIST

Index these first because they have the highest immediate impact:

1. **All n8n workflow JSONs** — immediately deployable pipelines
2. **YouTube automation GitHub repos** — video pipeline foundation
3. **Your MVP collection** — proven products ready to clone and resell
4. **Prompt libraries** — immediately usable by all agents
5. **Official API documentation** — accurate tool knowledge for agents
6. **Training video timestamps** — your creator community's knowledge

---

*SOUL.md tells you who you are. This file tells you how to use what you have.*
*Always mine the knowledge base first. Always feed it back after.*
