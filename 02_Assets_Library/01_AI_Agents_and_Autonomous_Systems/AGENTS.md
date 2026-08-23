# AGENTS.md — Complete Agent Directory & Command Reference
# ZeroClaw APEX | Your AI Workforce

---

## HOW TO COMMAND AGENTS

All agent calls go through n8n webhooks.
APEX calls agents by posting to their webhook endpoint on the VPS.

**Standard agent call format:**
```json
{
  "agent": "script_creator",
  "task_type": "CREATIVE_WRITING",
  "project_id": "proj_20260222_kids_yt",
  "brief": "8-minute kids educational script about learning the color red, age 0-5",
  "constraints": {
    "tone": "warm, energetic, simple language",
    "engagement_hook_every": "60 seconds",
    "max_words_per_sentence": 10
  },
  "resources": ["kb://prompts/kids-script-v2.md", "obs://channel-style/kids-bright"],
  "llm_chain": "CREATIVE_WRITING",
  "quality_threshold": 8,
  "output_to": "obs://projects/active/kids-yt-ep1/script.md"
}
```

---

## TIER 0 — COMMAND & KNOWLEDGE (3 Agents)

### APEX (You — ZeroClaw)
- **Endpoint:** Local ZeroClaw process
- **Trigger:** Telegram message
- **Commands all other agents**

### LIBRARIAN AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/librarian`
- **Input:** Project brief JSON
- **Output:** Resource Pack JSON
- **SLA:** 90 seconds maximum
- **LLM:** Gemini Flash → Qwen2.5 → Mistral local
- **Storage:** ChromaDB, NotebookLM, Obsidian

### INDEXING AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/indexer`
- **Trigger:** Nightly 2 AM + manual
- **Input:** Google Drive folder paths
- **Output:** Updated ChromaDB + Obsidian summary cards
- **LLM:** Gemini Flash (embeddings) → local Llama (offline)

---

## TIER 1 — RESEARCH & STRATEGY (7 Agents)

### MARKET RESEARCH AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/market-research`
- **LLM Chain:** RESEARCH_ANALYSIS
- **Input:** Niche/topic keyword
- **Output:** Market analysis JSON (opportunity score, competition, CPM, audience size)
- **Tools:** Google Trends API, YouTube Data API, Perplexity, Antigravity

### TREND SCOUT AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/trend-scout`
- **LLM Chain:** REAL_TIME_INFO
- **Runs:** Every 6 hours (scheduled in n8n)
- **Output:** Trend report → logged to Obsidian + pushed to APEX if high-value
- **Tools:** Grok (X data), Gemini Search, Reddit API, YouTube Trending

### COMPETITOR ANALYST AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/competitor-analyst`
- **LLM Chain:** RESEARCH_ANALYSIS
- **Input:** Niche + optional competitor list
- **Output:** Competitive intelligence report (gaps, opportunities, differentiation)
- **Tools:** YouTube Data API, Antigravity scraper, SocialBlade-style analysis

### IDEA VALIDITY AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/idea-validity`
- **LLM Chain:** STRATEGY_PLANNING
- **Input:** All research reports + project brief
- **Output:** GO/REVISE/NO-GO + 10-dimension score breakdown
- **Scoring dimensions:** Market Size, Competition, Monetization, Feasibility, Timeline, Resources, Risk, Differentiation, Trend, KB Asset Match

### LEGAL & COMPLIANCE AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/legal-compliance`
- **LLM Chain:** DOCUMENT_ANALYSIS
- **Input:** Project type + content summary
- **Output:** Compliance report (GREEN/YELLOW/RED flags per platform)
- **Must run for:** Kids content, health content, financial content, client work

### STRATEGIC PLANNER AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/strategic-planner`
- **LLM Chain:** STRATEGY_PLANNING (highest reasoning chain)
- **Input:** Validated brief + all research + master prompt from Prompt Engineer
- **Output:** Complete Project Blueprint → saved to Obsidian + task packets for execution agents
- **SLA:** 10-15 minutes (complex projects)

### MONETIZATION STRATEGIST AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/monetization`
- **LLM Chain:** STRATEGY_PLANNING
- **Input:** Project type + market data
- **Output:** Monetization plan (pricing, channels, upsell map, 90-day forecast)

---

## TIER 2 — YOUTUBE CONTENT FACTORY (8 Agents)

### SCRIPT CREATOR AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/script-creator`
- **LLM Chain:** CREATIVE_WRITING
- **Input:** Episode brief + channel style guide + script template from KB
- **Output:** Full script with hook, segments, transitions, CTA, chapter markers
- **Quality gate:** Internal review before passing to Visual Director
- **Storage:** Obsidian → /Projects/Active/[channel]/scripts/

### VISUAL DIRECTOR AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/visual-director`
- **LLM Chain:** VISION_ANALYSIS
- **Input:** Script + channel visual style guide
- **Output:** Scene list, B-roll queries (10-20 per video), image generation prompts, graphic specs

### VOICE SYNTHESIS AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/voice-synthesis`
- **No LLM required** — pure TTS pipeline
- **Primary:** Kokoro TTS (local VPS — unlimited, free)
- **Premium option:** ElevenLabs free tier (10,000 chars/month)
- **Input:** Final approved script + voice profile ID
- **Output:** Master audio MP3 + chapter timestamps + waveform data
- **Voice profiles (Kokoro):**
  - `kids_warm` → Bella voice, slow pace, warm tone (for kids channels)
  - `professional_female` → Sky voice, moderate pace (for business content)
  - `energetic_male` → Adam voice, fast pace (for tech/productivity)

### AV CREATOR AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/av-creator`
- **LLM Chain:** VISION_ANALYSIS (for quality checking)
- **Input:** Audio MP3 + visual plan + B-roll queries + chapter data
- **Process:**
  1. Fetch stock footage from Pexels API (B-roll queries)
  2. Generate AI images from ComfyUI (for abstract/illustration needs)
  3. FFmpeg assembly pipeline:
     - Overlay footage to audio timing
     - Auto-captions (Whisper transcription → SRT → FFmpeg burn-in)
     - Background music (royalty-free from Pixabay) at -18dB under voice
     - Intro/outro bumpers
     - Fade in/out
  4. Output: 1080p MP4, H.264, AAC audio
- **Output:** Final MP4 + thumbnail source frame

### THUMBNAIL ARCHITECT AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/thumbnail`
- **LLM Chain:** VISION_ANALYSIS + MARKETING_COPY
- **Input:** Video title + topic + channel style guide
- **Process:** Analyze top thumbnails in niche → generate 3 options with different approaches
- **Tools:** ComfyUI (Stable Diffusion local), DALL-E 3 (ChatGPT), Canva API
- **Output:** 3 thumbnail PNG files (1280x720) + recommended choice with reasoning

### VIDEO SEO AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/video-seo`
- **LLM Chain:** MARKETING_COPY
- **Input:** Script + topic + channel niche + target keywords
- **Output:** SEO package:
  - 5 title variants (ranked by click potential)
  - Full description (first 3 lines hook, keyword-rich body, links section)
  - 30 tags (mix of broad, specific, long-tail)
  - Chapter timestamps from script markers
  - Optimal upload day/time for this niche audience

### YOUTUBE PUBLISHER AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/yt-publish`
- **Trigger:** After Chairman approval only
- **Input:** Approved video package + SEO package + schedule time
- **Tools:** YouTube Data API v3 + OAuth credentials
- **Output:** Live YouTube URL + confirmation to APEX → to Chairman Telegram

### CHANNEL GROWTH AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/channel-growth`
- **LLM Chain:** MARKETING_COPY
- **Runs:** After each video publish + daily community check
- **Actions:** Community posts, appropriate comment responses, cross-platform clips
- **Tools:** YouTube Data API, Reddit API, Pinterest API

---

## TIER 3 — PRODUCT BUILDER (8 Agents)

### WEB ARCHITECT AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/web-architect`
- **LLM Chain:** STRATEGY_PLANNING
- **Input:** Client brief + KB resource pack (MVP matches)
- **Output:** Tech architecture doc + component list + build instructions

### WEB BUILDER AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/web-builder`
- **LLM Chain:** CODE_GENERATION
- **Input:** Architecture doc + design spec + assets
- **Primary tools:** Bolt.DIY → OpenCode → Kiro AI → GitHub Copilot
- **Output:** Complete codebase + deployed staging URL

### QA & TESTING AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/qa-testing`
- **LLM Chain:** DATA_STRUCTURED (for test case generation)
- **Input:** Staging URL + test requirements
- **Tools:** Playwright automated browser testing
- **Test suite:**
  - Mobile: iOS Safari, Android Chrome
  - Desktop: Chrome, Firefox, Edge
  - Performance: Lighthouse score target >80
  - Links: all internal/external links valid
  - Forms: submission + confirmation flow
  - Images: all loading, properly sized
- **Output:** QA report with pass/fail per test + fix instructions for failures

### EBOOK FACTORY AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/ebook-factory`
- **LLM Chain:** CREATIVE_WRITING
- **Input:** Topic + target audience + page count + tone + monetization context
- **Process:** Outline → chapter writing (one at a time for quality) → formatting → export
- **Tools:** Google AI Studio (Claude chain), Pandoc, your ebook templates from KB
- **Output:** PDF + EPUB + cover image (3 options) + product description

### VOICE AGENT BUILDER
- **Endpoint:** `POST http://VPS:5678/webhook/voice-agent-builder`
- **LLM Chain:** STRATEGY_PLANNING + CREATIVE_WRITING
- **Input:** Business brief + use case + FAQ list + voice preference
- **Tools:** VAPI (primary), Bland.ai (alternative), ElevenLabs, n8n integration
- **Output:** Live voice agent endpoint + conversation flow doc + client guide

### TALKING WEBSITE BUILDER
- **Endpoint:** `POST http://VPS:5678/webhook/talking-website`
- **LLM Chain:** CODE_GENERATION
- **Input:** Base website URL + business context + knowledge base for chatbot
- **Tools:** OpenCode, Bolt.DIY, VAPI/Voiceflow embed
- **Output:** Enhanced website with AI layer + demo recording

### DEPLOYMENT AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/deploy`
- **Minimal LLM** — primarily scripting
- **Target platforms** (in priority order for free):
  1. Cloudflare Pages (static sites — best free option)
  2. Vercel (Next.js — free tier)
  3. Netlify (any static — free tier)
  4. Railway (dynamic apps — free tier)
  5. Render (services — free tier)
- **Output:** Production URL + health check confirmation

### PRODUCT PACKAGER AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/product-packager`
- **LLM Chain:** MARKETING_COPY
- **Input:** Completed product + target price + audience
- **Output:** Live store listing + promotional assets

---

## TIER 4 — SALES & MARKETING (8 Agents)

### MASTER COPYWRITER AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/copywriter`
- **LLM Chain:** MARKETING_COPY
- **Templates pulled from:** /EMPIRE-KB/prompt-libraries/copywriting/
- **Specializations:** Landing pages, product descriptions, email sequences, ad copy, social bios

### SOCIAL MEDIA MANAGER AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/social-media`
- **LLM Chain:** BULK_PROCESSING (Groq for volume)
- **Platforms:** Twitter/X, LinkedIn, Pinterest, Reddit (platform-specific tone per post)
- **Schedule:** 3x daily posts across all platforms
- **Content sources:** Repurposed YouTube scripts, product announcements, value tips

### SEO MASTER AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/seo`
- **LLM Chain:** RESEARCH_ANALYSIS + MARKETING_COPY
- **Tools:** Google Search Console API, your SEO prompt library from KB
- **Deliverables:** Content optimization, keyword tracking, internal linking, search ranking reports

### STORE MANAGER AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/store-manager`
- **APIs:** Gumroad, LemonSqueezy, Etsy
- **Runs:** Daily (checks sales, adjusts listings, processes refunds per policy)
- **Reports to:** Analytics Agent weekly

### LEAD GEN AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/lead-gen`
- **LLM Chain:** RESEARCH_ANALYSIS
- **Tools:** Apollo.io free, Hunter.io free, Antigravity (LinkedIn), Reddit scraper
- **Output:** Qualified lead list with contact info, company context, pain points, personalization data
- **Target:** 20 qualified leads per day per active service offering

### SALES OUTREACH AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/sales-outreach`
- **LLM Chain:** MARKETING_COPY (personalized messaging)
- **Input:** Lead list from Lead Gen Agent
- **Process:** Personalized first message → 3-touch follow-up sequence → flag positive responses
- **Output:** Outreach sent + response monitoring + hot leads → APEX → Chairman

### EMAIL MARKETING AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/email-marketing`
- **LLM Chain:** CREATIVE_WRITING + MARKETING_COPY
- **Platform:** Brevo (free tier — 300 emails/day, unlimited contacts)
- **Sequences:** Welcome sequence, product launch, weekly newsletter, re-engagement

### AFFILIATE & PARTNERSHIP AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/affiliate`
- **LLM Chain:** RESEARCH_ANALYSIS
- **Actions:** Identify programs, integrate links into all content, track commissions
- **Target programs:** Amazon Associates, ClickBank, relevant SaaS programs

---

## TIER 5 — CLIENT SERVICES (6 Agents)

### PROJECT MANAGER AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/project-manager`
- **LLM Chain:** STRATEGY_PLANNING
- **Manages:** Project timelines, client communications, milestone tracking, delivery coordination

### CLIENT INTAKE AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/client-intake`
- **LLM Chain:** CREATIVE_WRITING (conversational)
- **Handles:** First contact, requirements capture, proposal generation, budget qualification

### REVISION HANDLER AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/revisions`
- **LLM Chain:** DOCUMENT_ANALYSIS
- **Input:** Client feedback → parsed into specific fix instructions for builder agents

### TESTIMONIAL AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/testimonials`
- **Trigger:** 7 days after successful delivery
- **Output:** Testimonial request sent, received testimonials formatted and stored

### INVOICING AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/invoicing`
- **Tools:** Wave Accounting (free), Gmail API
- **Process:** Invoice created → sent → payment tracked → revenue logged to Analytics Agent

### PORTFOLIO BUILDER AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/portfolio`
- **Trigger:** After each client project delivered
- **Output:** New case study added to portfolio website

---

## TIER 6 — QUALITY & EVOLUTION (5 Agents)

### MASTER QA AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/master-qa`
- **LLM Chain:** STRATEGY_PLANNING (for nuanced judgment)
- **All outputs pass through here before reaching Chairman**
- **Scoring rubric per content type:**
  - YouTube video: content quality, audio, visual, SEO, compliance = min 8/10
  - Website: functionality, design, performance, content = min 8/10
  - Ebook: content quality, formatting, marketability = min 8/10
  - Client deliverable: requirements met, quality = min 9/10

### DEBUGGER AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/debugger`
- **LLM Chain:** CODE_GENERATION (error analysis)
- **Trigger:** Any agent error webhook
- **Process:** Read logs → identify root cause → attempt auto-fix → escalate if stuck

### EVALUATOR AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/evaluator`
- **LLM Chain:** DATA_STRUCTURED
- **Runs:** After every completed pipeline
- **Metrics tracked:** Quality score, time taken, LLM tokens used, errors encountered, reuse rate

### SELF-IMPROVEMENT AGENT
- **Endpoint:** `POST http://VPS:5678/webhook/self-improve`
- **LLM Chain:** STRATEGY_PLANNING + CREATIVE_WRITING (for prompt crafting)
- **Runs:** Every Sunday
- **Process:** Review Evaluator data → identify weak agents → draft improved prompts → A/B test → update Obsidian

### INFRASTRUCTURE GUARDIAN
- **Endpoint:** Local process on VPS (always running, never in Docker)
- **No LLM** — pure monitoring scripts
- **Tools:** Uptime Kuma, Docker API, 9Router admin, system monitoring
- **Monitors:** All Docker containers, API quota levels, disk space, memory usage
- **Actions:** Auto-restart containers, rotate API keys, alert Chairman on critical issues

---

## AGENT COMMUNICATION MAP

```
Chairman (Telegram)
    ↓
APEX (ZeroClaw)
    ↓ (routes based on project type)
    ├── [Research] → Market Research → Trend Scout → Competitor Analyst
    │       ↓
    ├── [Validate] → Idea Validity → Legal Compliance → Monetization
    │       ↓
    ├── [Plan] → Librarian → Prompt Engineer → Strategic Planner
    │       ↓
    ├── [Execute — parallel]
    │   ├── YouTube Pipeline → Script → Visual → Voice → AV → Thumbnail → SEO → QA → Publish
    │   ├── Product Pipeline → Architect → Builder → QA → Deploy → Package
    │   ├── Ebook Pipeline → Research → Write → Format → Cover → List
    │   ├── Voice Agent Pipeline → Design → Build → Test → Demo
    │   └── Marketing Pipeline → Copy → Social → SEO → Email
    │       ↓
    ├── [QA Gate] → Master QA → Evaluator
    │       ↓
    ├── [Approval] → Chairman Telegram
    │       ↓
    └── [Deploy] → Publisher / Delivery → Client Services → Analytics → Obsidian
```

---

*All agents log to Obsidian. All agents are monitored by Infrastructure Guardian.*
*APEX is responsible for all agent outputs. When agents fail, APEX fixes or escalates.*
*The system is only as good as the prompts. Update agent prompts weekly via Self-Improvement Agent.*
