# TOOLS.md — Complete Tool Stack & LLM Chain Routing
# ZeroClaw APEX Configuration | Digital Empire OS

---

## LLM ARSENAL & ROUTING STRATEGY

9Router is configured as your primary API gateway at `http://localhost:20128`.
All LLM calls route through 9Router. Never call APIs directly.

### Free LLM Inventory

| Model | Provider | Strengths | Free Tier Limit |
|-------|----------|-----------|-----------------|
| Gemini 2.0 Flash | Google AI Studio | Speed, vision, long context, web search | 1,500 req/day |
| Gemini 1.5 Pro | Google AI Studio | 1M context, document analysis | 50 req/day |
| Claude 3.5 Sonnet | Anthropic (via OpenRouter free) | Creative writing, reasoning, code | Limited |
| GPT-4o | OpenAI (via OpenRouter) | Structure, marketing, coding | Limited |
| Grok | xAI | Real-time X/Twitter data, trends | Limited |
| Groq/Llama 3.1 | Groq | Ultra-fast inference (500+ tok/sec) | 14,400 req/day |
| DeepSeek Chat | DeepSeek | Deep reasoning, analysis | Generous free |
| DeepSeek Coder | DeepSeek | Code generation | Generous free |
| Qwen2.5-72B | Via OpenRouter | Long documents, multilingual | Limited |
| Qwen Code | Alibaba Cloud | Code completion | Limited |
| GitHub Copilot | GitHub | IDE-integrated code | Subscription (existing) |
| Kiro AI | Amazon | Intelligent code completion | Existing access |
| Llama 3.1 8B | Ollama (local) | Private, unlimited, fast | Unlimited (local) |
| Mistral 7B | Ollama (local) | Efficient reasoning | Unlimited (local) |
| Qwen2.5 7B | Ollama (local) | Multilingual tasks | Unlimited (local) |
| DeepSeek Coder 6.7B | Ollama (local) | Code, no API dependency | Unlimited (local) |

---

## LLM CHAIN ROUTING TABLE

9Router reads the `task_type` tag on every request and routes accordingly.

### Chain 1: CREATIVE_WRITING (scripts, ebooks, stories)
```
Primary:   Claude 3.5 Sonnet  → creative depth, nuance, voice
Secondary: GPT-4o             → structure, pacing, engagement hooks  
Tertiary:  Gemini 2.0 Flash   → speed iteration, SEO integration
Fallback:  Llama 3.1 8B local → offline, unlimited
```

### Chain 2: RESEARCH_ANALYSIS (market research, trend analysis)
```
Primary:   Grok              → real-time web + X/Twitter data
Secondary: Gemini 2.0 Flash  → synthesis, broad knowledge
Tertiary:  DeepSeek Chat     → deep competitive analysis
Fallback:  Groq/Llama        → fast summarization
```

### Chain 3: CODE_GENERATION (websites, scripts, automation)
```
Primary:   GitHub Copilot    → IDE-native, context-aware
Secondary: Kiro AI           → intelligent completion
Tertiary:  DeepSeek Coder    → complex logic, algorithms
Quaternary:Qwen Code         → alternative perspective
Fallback:  DeepSeek Coder 6.7B local → offline
```

### Chain 4: STRATEGY_PLANNING (architecture, project planning)
```
Primary:   Claude 3.5 Sonnet → deep multi-step reasoning
Secondary: GPT-4o            → structured output, frameworks
Tertiary:  Gemini 1.5 Pro    → long document context
Fallback:  DeepSeek Chat     → analytical reasoning
```

### Chain 5: MARKETING_COPY (sales pages, ads, social posts)
```
Primary:   GPT-4o            → conversion-optimized copy
Secondary: Claude 3.5 Sonnet → nuance, storytelling
Tertiary:  Gemini 2.0 Flash  → volume, speed
Fallback:  Llama 3.1 8B local → bulk generation
```

### Chain 6: DATA_STRUCTURED (JSON, APIs, parsing)
```
Primary:   DeepSeek Coder    → precise structured output
Secondary: Qwen2.5-72B       → complex data transformation
Tertiary:  Mistral 7B local  → fast, reliable, offline
Fallback:  Llama 3.1 8B local
```

### Chain 7: DOCUMENT_ANALYSIS (PDFs, long docs, KB queries)
```
Primary:   Gemini 1.5 Pro    → 1M token context window
Secondary: Claude 3.5 Sonnet → nuanced comprehension
Tertiary:  Qwen2.5-72B       → multilingual documents
Fallback:  Ollama local      → private documents
```

### Chain 8: REAL_TIME_INFO (news, trends, current events)
```
Primary:   Grok              → X/Twitter real-time
Secondary: Gemini 2.0 Flash  → Google search grounding
Tertiary:  Groq/Llama        → fast synthesis
```

### Chain 9: BULK_PROCESSING (high volume, batch tasks)
```
Primary:   Groq/Llama 3.1    → 500+ tokens/sec, high volume
Secondary: Gemini 2.0 Flash  → large daily quota
Tertiary:  Llama 3.1 8B local → zero cost, unlimited
```

### Chain 10: VISION_ANALYSIS (image understanding, thumbnails)
```
Primary:   GPT-4o Vision     → strongest multi-modal
Secondary: Gemini 2.0 Flash  → fast image analysis
Tertiary:  Qwen2.5-VL local  → offline vision
```

---

## TOOL STACK DIRECTORY

### Command & Orchestration
```
ZeroClaw          → You. CEO layer. Telegram interface. On laptop.
9Router           → localhost:20128. LLM routing and fallback.
OpenClaw (VPS)    → Multi-agent orchestrator. Commands agent teams.
Agent Zero (VPS)  → Autonomous task executor. Does actual work.
n8n (VPS:5678)    → Workflow automation. All pipelines live here.
Telegram Bot      → Chairman command interface.
```

### Knowledge & Memory
```
ChromaDB (VPS:8000)     → Vector database. Semantic search across all KB.
Obsidian Vault          → Agent memory, decisions, templates, outputs.
NotebookLM              → Topic workspaces for deep document Q&A.
Google Drive (2TB)      → Raw asset storage. Organized by category.
Google One              → Extended storage for large files.
```

### AI & Compute
```
Ollama (VPS:11434)      → Local LLMs. Zero cost. Unlimited.
Google AI Studio        → Gemini API. 1,500 free req/day.
OpenRouter              → Multi-model gateway. Accesses Claude, GPT, etc.
Groq                    → Ultra-fast Llama inference.
GCP (existing account)  → Cloud compute for burst workloads.
AWS (credentials)       → S3 storage, Lambda for serverless.
```

### Content Production
```
Kokoro TTS (VPS)        → Local voice synthesis. Unlimited. Free.
ElevenLabs (free)       → Premium voice cloning. 10,000 chars/month.
FFmpeg (VPS)            → Video/audio processing. All formats.
ComfyUI (VPS)           → Stable Diffusion image generation. Local.
Pexels API              → Stock footage and images. Free tier.
Pixabay API             → Additional stock assets. Free.
```

### Development & Building
```
Bolt.DIY                → Rapid full-stack app generation.
Open Loveable           → AI-first web app builder.
OpenCode                → Terminal-based AI coding. Installed.
Cursor                  → AI code editor. Installed.
Kiro AI                 → Amazon's AI IDE. Installed.
Trae AI                 → AI coding assistant. Installed.
Kilo Code               → Additional coding AI. Installed.
VSCode                  → Full IDE. Installed.
GitHub Copilot          → Inline code completion. Active subscription.
Docker Desktop          → Container management on laptop.
Docker (VPS)            → Production containers on VPS.
```

### Automation & Integration
```
n8n (self-hosted)       → Primary workflow automation. 500+ integrations.
CrewAI                  → Multi-agent framework for complex tasks.
Lutra AI                → Browser automation workflows.
Antigravity             → AI-powered browser agent. Scraping, interaction.
I Flow AI               → Additional automation layer.
Ngrok / Cloudflare Tunnel → Expose local services securely.
```

### Revenue & Stores
```
Gumroad                 → Digital product sales. Free to list.
LemonSqueezy            → Stripe-powered digital store.
Etsy                    → Digital download marketplace.
YouTube (3+ channels)   → Ad revenue + affiliate integration.
```

### Analytics & Monitoring
```
Uptime Kuma (VPS:3001)  → Service health monitoring.
Google Analytics        → Web traffic analysis.
YouTube Studio API      → Channel performance data.
Google Search Console   → SEO and search ranking data.
```

### Tunneling & Networking
```
Cloudflare Tunnel       → Permanent, secure VPS exposure. FREE.
Cloudflare R2           → 10GB object storage. FREE.
Cloudflare Pages        → Frontend hosting. FREE.
Vercel                  → Next.js hosting. FREE tier.
Netlify                 → Static site hosting. FREE tier.
Railway                 → Backend app hosting. FREE tier.
```

---

## TOOL SELECTION DECISION TREE

When choosing how to build something, follow this order:

```
1. Does an n8n JSON in the knowledge base already do this?
   YES → Import and configure it. Done.
   NO  → Continue...

2. Does a GitHub repo in the KB do 80%+ of what's needed?
   YES → Clone, configure, integrate via n8n.
   NO  → Continue...

3. Can Bolt.DIY or Open Loveable generate it?
   YES → Generate, then refine with Cursor/OpenCode.
   NO  → Continue...

4. Build custom with OpenCode + GitHub Copilot + Kiro AI
   → Use DeepSeek Coder chain for complex logic
   → Reference existing MVPs from KB for patterns
```

---

## API KEY LOCATIONS

All API keys are stored in: `~/.0claw/config.toml`
Backup location: Obsidian vault → `/System/API-Keys.md` (encrypted)

9Router config: `~/.9router/config.json`
- Primary: Google AI Studio (Gemini)
- Secondary: OpenRouter (Claude, GPT, Qwen)  
- Tertiary: Groq (Llama ultra-fast)
- Quaternary: DeepSeek direct
- Local fallback: Ollama http://VPS-IP:11434

---

## RESOURCE LIMITS TRACKER

Monitor these weekly. 9Router tracks usage automatically.

| Provider | Daily Limit | Alert Threshold | Action at Limit |
|----------|-------------|-----------------|-----------------|
| Gemini 2.0 Flash | 1,500 req | 1,200 | Route to Groq |
| Groq | 14,400 req | 12,000 | Route to Gemini |
| Grok | Varies | 80% | Route to Gemini search |
| DeepSeek | Generous | 80% | Route to local Ollama |
| Local Ollama | Unlimited | N/A | Always available |

---

*See AGENTS.md for who uses these tools. See PROTOCOLS.md for how workflows are assembled.*
