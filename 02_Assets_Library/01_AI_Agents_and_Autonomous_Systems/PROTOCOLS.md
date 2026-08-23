# PROTOCOLS.md — Exact Workflow Protocols
# ZeroClaw APEX | Step-by-Step for Every Scenario

---

## PROTOCOL 0: RECEIVING ANY COMMAND

This runs FIRST for every single Telegram message from Chairman.

```
Step 1: Parse intent
  → What type of project? (YouTube / Web / Ebook / Voice Agent / Research / System)
  → What is the specific deliverable?
  → What constraints? (deadline, budget, style, audience)
  → Is anything unclear? If yes → ask ONE question before proceeding

Step 2: Trigger Librarian Agent
  → Build query payload from parsed intent
  → Receive Resource Pack (max 90 seconds)
  → If high-value existing assets found → report to Chairman: "Found existing [X] that covers 80% of this. Starting from there."

Step 3: Log project start to Obsidian
  → Project name, date, Chairman brief, resource pack summary

Step 4: Route to correct protocol below
```

---

## PROTOCOL 1: NEW YOUTUBE CHANNEL

### Trigger: "create channel" / "new YouTube" / "start channel for [niche]"

**Phase A — Research & Validation (runs in parallel, ~15 min)**
```
A1. Market Research Agent → niche viability, search volume, CPM rates
A2. Trend Scout Agent → current trending topics in niche
A3. Competitor Analyst → top 10 channels, gap analysis
A4. Librarian Agent → existing scripts, workflows, templates
A5. Legal & Compliance Agent → platform policy check for content type
All A-tasks run simultaneously via n8n parallel branches
```

**Phase B — Strategy (after A completes, ~10 min)**
```
B1. Idea Validity Agent → scores all research on 10-point framework
    If score < 6 → report to Chairman with better alternatives
    If score >= 6 → proceed
B2. Monetization Strategist → revenue model, timeline, upsell map
B3. Prompt Engineer → crafts master brief for Planner using Chain 4 (STRATEGY)
B4. Strategic Planner → full channel blueprint:
    - Channel name, description, brand colors, intro/outro style
    - 3 content series with episode titles
    - Upload schedule (days/times optimized for niche audience)
    - 90-day content calendar
    - Monetization roadmap
```

**Phase C — Approval Gate 1 (Chairman reviews strategy)**
```
Send to Telegram:
"✋ APPROVAL REQUIRED: [Channel Name] Strategy

📋 Niche: [niche]
📊 Market score: [X/10] — [summary]
📅 Upload plan: [X videos/week, days]
💰 Revenue timeline: [estimate]
🎯 3 content series: [names]
⚠️  Any risks: [flagged items]

[✅ APPROVE STRATEGY] [✏️ EDIT] [❌ REJECT]"
```

**Phase D — Production (after strategy approved, ~60-90 min per video)**
```
D1. Script Creator Agent → Episode 1 script (Chain 1: CREATIVE_WRITING)
    Uses: channel style guide + content calendar + proven script templates from KB
D2. Visual Director → scene plan, B-roll list, image prompts
D3. Voice Synthesis Agent → Kokoro TTS render (local, free, immediate)
D4. AV Creator Agent → FFmpeg pipeline: audio + stock footage + captions → MP4
D5. Thumbnail Architect → 3 thumbnail options
D6. Video SEO Agent → title variants, description, 30 tags, timestamps
D7. QA Agent → age-appropriateness, audio quality, captions, compliance
D8. Evaluator Agent → quality score. If < 8 → back to D1 with notes
```

**Phase E — Approval Gate 2 (Chairman reviews first video)**
```
Send preview link + title options + thumbnail options
[✅ APPROVE & UPLOAD] [✏️ EDIT] [❌ REJECT]
```

**Phase F — Deployment (after Chairman approves)**
```
F1. YouTube Publisher → upload with full metadata, scheduled time
F2. Social Media Agent → announcement post on Pinterest, Reddit
F3. Analytics Agent → set up tracking, baseline metrics
F4. Send confirmation: live URL + scheduled publish time
F5. Log all outputs, prompts, configs to Obsidian
F6. Queue Episodes 2-5 for production (pipeline continues automatically)
```

---

## PROTOCOL 2: NEW WEBSITE OR WEB APP

### Trigger: "build website" / "create app" / "website for [client/product]"

**Phase A — Requirements Capture**
```
A1. Extract from Chairman message:
    - Client name / product name
    - Industry / niche
    - Key pages needed
    - Style preference (modern/classic/bold/minimal)
    - Budget / delivery deadline
    - Target audience
If any critical info missing → ONE question to Chairman
```

**Phase B — Resource Check & Architecture**
```
B1. Librarian → find closest existing MVP or template in KB
B2. Web Architect Agent → tech stack decision:
    Simple site (5 pages) → Bolt.DIY + Cloudflare Pages
    Web app (with backend) → Bolt.DIY + Railway + PostgreSQL
    E-commerce → Bolt.DIY + LemonSqueezy integration
    Complex SaaS → OpenCode + Vercel + Supabase
B3. Visual Director → color palette, font, layout mood board description
B4. Copywriter Agent → key messages, headlines, CTAs (Chain 5: MARKETING_COPY)
```

**Phase C — Build**
```
C1. Web Builder Agent:
    → If template found: clone, customize, connect to client brand
    → If no template: Bolt.DIY generation from architecture doc
    → Kiro AI / OpenCode for custom components
    → GitHub Copilot for any complex logic
C2. Deployment Agent → push to staging URL (Vercel preview)
```

**Phase D — QA**
```
D1. QA & Testing Agent → Playwright automated tests:
    ✓ Mobile responsiveness (iOS + Android)
    ✓ All links work
    ✓ Forms submit correctly
    ✓ Loading speed < 3 seconds
    ✓ Images optimized
    ✓ Contact info correct
D2. If fails → specific fix list back to Web Builder → retest
D3. If passes → Evaluator scores → minimum 8/10 to proceed
```

**Phase E — Approval Gate**
```
"✋ APPROVAL REQUIRED: [Client] Website

🔗 Preview: [staging URL]
📋 Pages built: [list]
✅ QA: All tests passed
💰 Invoice: $[amount] ready to send
⏱️  Build time: [X hours]

[✅ APPROVE & DELIVER] [✏️ REQUEST CHANGES] [❌ REJECT]"
```

**Phase F — Delivery**
```
F1. Move to production domain / final hosting
F2. Client Services Agent → send delivery email with login details
F3. Invoicing Agent → send invoice
F4. Portfolio Builder Agent → add to portfolio website
F5. Testimonial Agent → schedule follow-up in 7 days
F6. Log entire project to Obsidian, extract reusable components to KB
```

---

## PROTOCOL 3: EBOOK CREATION & LISTING

### Trigger: "create ebook" / "write ebook" / "make a guide on [topic]"

**Phase A — Research & Outline**
```
A1. Librarian → existing ebook templates, topic research in KB
A2. Market Research Agent → is this topic searched? What competing ebooks exist?
A3. Monetization Strategist → optimal pricing, upsell opportunities
A4. Prompt Engineer → crafts ebook outline prompt
A5. Ebook Factory Agent (Chain 1: CREATIVE_WRITING):
    → Generates detailed chapter outline
    → Sends outline to APEX for internal review
    → If outline quality < 8/10 → regenerate with adjusted prompt
```

**Phase B — Production**
```
B1. Ebook Factory Agent → write all chapters (full Claude 3.5 chain)
    → Each chapter: intro hook, 3-5 sections, actionable takeaway, segue
    → Target: 40-80 pages depending on brief
B2. Visual Director → cover art brief
B3. Image Generation → ComfyUI or DALL-E 3 for cover (3 options)
B4. Formatting Agent → Pandoc: Markdown → PDF + EPUB
    → Professional typography, page numbers, TOC, chapter headers
B5. QA Agent → proofread, fact-check, formatting check
```

**Phase C — Approval Gate**
```
"✋ APPROVAL REQUIRED: [Title] Ebook

📖 [X] pages, [X] chapters
🎨 Cover: [3 options attached]
💰 Recommended price: $[X]
📊 Market: [X monthly searches, Y competing ebooks]

[✅ APPROVE & LIST] [✏️ EDIT] [❌ REJECT]"
```

**Phase D — Monetization**
```
D1. Copywriter Agent → sales page copy, product description (Chain 5)
D2. Product Packager Agent → create Gumroad listing:
    - Title, description, cover image, file upload
    - Price set, delivery automation configured
    - Tags and categories for discovery
D3. Social Media Agent → launch announcement posts
D4. Email Marketing Agent → send to list (if applicable)
D5. YouTube SEO Agent → create YouTube video about ebook topic (cross-sell)
D6. Confirm to Chairman: live Gumroad link + first 24-hour revenue check
```

---

## PROTOCOL 4: AI VOICE AGENT BUILD

### Trigger: "build voice agent" / "AI receptionist for [business]" / "voice bot"

**Phase A — Discovery**
```
A1. Client Intake Agent → capture:
    Business name, industry, use case (receptionist/FAQ/booking/support)
    Business hours, escalation rules, top 20 FAQs
    Voice preference (warm/professional/energetic)
    Key information to know (services, prices, locations)
A2. Librarian → existing voice agent configs in KB
A3. Monetization Strategist → pricing recommendation
```

**Phase B — Design**
```
B1. Voice Agent Builder (Claude 3.5 chain):
    → Full conversation flow design
    → Welcome message, main menu, FAQ responses
    → Escalation logic (when to transfer to human)
    → Edge case handling
B2. Copywriter Agent → all scripts in brand voice
B3. Voice selection → ElevenLabs or Kokoro TTS test renders (3 voice options)
```

**Phase C — Build & Test**
```
C1. Voice Agent Builder → configure VAPI or Bland.ai:
    → Load all conversation flows
    → Connect to business phone/web widget
    → Set operating hours, fallback messages
C2. Internal testing → 20 simulated conversation scenarios
C3. QA Agent → score each scenario outcome
C4. Evaluator → minimum 9/10 for client demo (higher bar — this represents Chairman)
```

**Phase D — Demo & Approval**
```
"✋ APPROVAL REQUIRED: [Business] Voice Agent

📞 Test number: [number or web widget link]
✅ [X/20] test scenarios passed perfectly
🎙️ Voice: [voice name] — [sample clip]
💰 Monthly retainer: $[97-197]/month
📋 Conversation flows designed: [list key ones]

[✅ APPROVE FOR CLIENT DEMO] [✏️ ADJUST] [❌ REJECT]"
```

**Phase E — Delivery**
```
E1. Send demo to client with onboarding guide
E2. After client approval → activate on live number
E3. Invoicing Agent → first month invoice sent
E4. Project Manager → 7-day check-in scheduled
E5. Log complete config to KB for future similar clients
```

---

## PROTOCOL 5: RESEARCH & MARKET ANALYSIS

### Trigger: "research [topic]" / "is [idea] good?" / "analyze [niche]"

```
Step 1. Market Research Agent (Chain 2: RESEARCH_ANALYSIS)
    → Google Trends data
    → YouTube search volume estimate
    → Top competing channels/products
    → CPM rates for this niche (if YouTube)
    → Audience demographics

Step 2. Competitor Analyst
    → Top 5 competitors detailed breakdown
    → What they do well, gaps in their content
    → Their monetization strategies

Step 3. Trend Scout
    → Current momentum (growing/stable/declining)
    → Seasonal patterns
    → Emerging sub-niches

Step 4. Synthesize → Idea Validity Score (1-10 across 7 dimensions)

Step 5. Report to Chairman:
"🔍 RESEARCH COMPLETE: [Topic]

📊 Market Score: [X/10]
👥 Audience: [size estimate]
💰 Revenue Potential: [$X-Y/month at scale]
📈 Trend: [Growing/Stable/Declining]
🏆 Competition: [Low/Medium/High]
⭐ Recommendation: [GO / REVISE / NO-GO]
📋 Full report saved to Obsidian: /Projects/Ideas/[name]"
```

---

## PROTOCOL 6: EMERGENCY SITUATIONS

### VPS Unreachable
```
1. Guardian Agent attempts Docker restart (automated)
2. If unreachable: alert Chairman → "⚠️ VPS unreachable. Attempting restart."
3. Log into Oracle Cloud Console → Instance → Reboot
4. Services auto-restart (all containers have restart:always policy)
5. Health check confirms all services up → "✅ VPS restored. All services running."
```

### YouTube Channel Strike
```
1. IMMEDIATELY pause all production for that channel
2. Retrieve the flagged video details
3. Legal & Compliance Agent → analyze what triggered the strike
4. Report to Chairman: specific video, specific violation, recommended fix
5. Remove or edit the flagged video as Chairman directs
6. Update Script Agent and QA Agent prompts to prevent recurrence
7. Resume production only after Chairman approval
```

### API Quota Exhausted (all providers)
```
1. Route ALL tasks to local Ollama models (always available)
2. Queue any tasks that REQUIRE specific external models
3. Alert Chairman: "⚠️ API quota exhausted. Running on local models. [X tasks queued]"
4. Next day: quotas reset. Process queue automatically.
5. Review usage to prevent future exhaustion
```

### Agent Producing Consistently Bad Output
```
1. Disable agent immediately
2. Route its tasks to next-best alternative
3. Self-Improvement Agent → diagnose: prompt issue? Tool issue? LLM issue?
4. Draft fix → test on 3 sample tasks
5. If fixed → re-enable with updated prompt
6. If not fixed → flag to APEX for manual review → report to Chairman
```

---

## PROTOCOL 7: WEEKLY OPERATING RHYTHM

### Automated (No Chairman involvement)

**Every Day:**
- 6:00 AM: Trend Scout report generated and logged
- 8:00 AM: Daily digest sent to Chairman Telegram
- 2:00 AM: Indexing Agent runs (new KB content)
- Continuous: All active pipelines producing content

**Every Monday:**
- YouTube videos scheduled for the week (auto-upload Tuesday, Wednesday, Friday)
- Social media content calendar generated
- Weekly revenue summary logged to Obsidian

**Every Thursday:**
- Evaluator Agent runs full performance review
- Self-Improvement Agent drafts prompt improvements
- Analytics Agent compiles KPI report

**Every Sunday:**
- Self-Improvement Agent implements approved changes
- Indexing Agent full KB rescan
- Infrastructure Guardian → VPS backup
- Next week's content calendar generated

### Chairman's Daily 30 Minutes
```
Morning (10 min): Review Telegram — check approvals queue, dismiss or act
Afternoon (10 min): Review any flagged items, send new project ideas if any
Evening (10 min): Check daily revenue summary, note anything to chase
```

---

## PROTOCOL 8: NEW PROJECT INTAKE CHECKLIST

Before ANY new project starts, APEX confirms:

```
□ Intent clearly understood (or one question asked and answered)
□ Librarian queried — Resource Pack received
□ Existing assets identified and flagged for reuse
□ Idea Validity score >= 6 (or Chairman has overridden with explicit instruction)
□ LLM chain selected for primary task type
□ n8n workflow exists or will be created for this pipeline
□ Output logging to Obsidian configured
□ Approval gate configured in Telegram bot
□ Quality threshold set (minimum QA score before Chairman sees it)
□ Revenue pathway identified (how will this make money?)
```

If any box is unchecked → resolve before starting.

---

*This is the operational manual. SOUL.md is who you are. TOOLS.md is what you have.*
*KNOWLEDGE.md is how to use your resources. AGENTS.md is who you command.*
