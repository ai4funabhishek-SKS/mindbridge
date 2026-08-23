# ZEROCLAW SOUL FILES — Installation Guide
# Digital Empire AI CEO System | Version 1.0

---

## WHAT THESE FILES ARE

This folder contains the "soul" of your ZeroClaw AI CEO (codename: APEX).

These are configuration and instruction files that define who APEX is, what it knows, how it thinks, what tools it has, and exactly how to run every workflow in your empire.

Drop these files into ZeroClaw and it knows everything about your business, your tools, your goals, and how to execute every project type you've defined.

---

## THE FILES IN THIS FOLDER

| File | Purpose | Priority |
|------|----------|----------|
| `SOUL.md` | Identity, personality, decision framework, communication style | LOAD FIRST |
| `TOOLS.md` | Complete tool stack + LLM chain routing table | LOAD SECOND |
| `KNOWLEDGE.md` | How to use the knowledge base, KB architecture, query protocols | LOAD THIRD |
| `AGENTS.md` | Complete agent directory, endpoints, input/output specs | LOAD FOURTH |
| `PROTOCOLS.md` | Exact step-by-step workflows for every project type | LOAD FIFTH |
| `BRUTAL_REVIEW.md` | Honest critical analysis — keep for reference, don't load into ZeroClaw | REFERENCE ONLY |

---

## HOW TO INSTALL INTO ZEROCLAW

### Option 1: Direct File Loading (Recommended)
Place all files in: `~/.0claw/soul/`

```bash
# On your laptop (PowerShell):
mkdir -p ~/.0claw/soul
# Copy all .md files from this folder into ~/.0claw/soul/
```

Then in your `~/.0claw/config.toml`, add:
```toml
[agent]
soul_directory = "~/.0claw/soul/"
load_order = ["SOUL.md", "TOOLS.md", "KNOWLEDGE.md", "AGENTS.md", "PROTOCOLS.md"]
name = "APEX"
```

### Option 2: System Prompt Injection
If ZeroClaw doesn't support file loading yet, concatenate all files and use as system prompt:

```bash
# PowerShell:
cat SOUL.md TOOLS.md KNOWLEDGE.md AGENTS.md PROTOCOLS.md > APEX_SYSTEM_PROMPT.md
```

Then configure ZeroClaw to use APEX_SYSTEM_PROMPT.md as its system context.

### Option 3: Per-Session Loading
At the start of each ZeroClaw session, reference these files:

```
zeroclaw --system-file ~/.0claw/soul/SOUL.md \
         --context-file ~/.0claw/soul/TOOLS.md \
         --context-file ~/.0claw/soul/PROTOCOLS.md
```

---

## WHAT TO CONFIGURE BEFORE FIRST USE

### 1. Update API Keys in TOOLS.md
Replace placeholder text with your actual endpoints:
- Your VPS IP address
- Your Telegram bot token
- Your n8n webhook base URL (your Cloudflare Tunnel URL)
- Confirm all API keys are in `~/.0claw/config.toml` and `~/.9router/config.json`

### 2. Personalize SOUL.md
- Line 5: Replace `[YOUR NAME]` with your actual name
- Line 210: Update Chairman's timezone for digest scheduling
- Review the Revenue Targets section — adjust if you want to start with fewer streams

### 3. Update Agent Endpoints in AGENTS.md
Replace `http://VPS:5678` with your actual VPS IP or Cloudflare Tunnel URL.
Example: `https://yourdomain.cfargotunnel.com/webhook/script-creator`

### 4. Confirm Tool Availability
Run through TOOLS.md and mark any tools you don't yet have set up.
APEX will not hallucinate tools it doesn't have — but it needs to know which are active.

Add to TOOLS.md at the top:
```
## ACTIVE TOOLS (confirmed working as of [date])
[list tools you've verified are working]

## PENDING SETUP (not yet active)
[list tools still being configured]
```

---

## FIRST CONVERSATION TO HAVE WITH APEX

After installing the soul files, start your first session with:

```
"APEX, you've just been initialized. Please confirm:
1. What is your primary mission?
2. What tools do you currently have access to?  
3. What is the first thing I should do to get this empire running?
4. What are the 3 biggest risks you see in my current setup?
5. What pipeline should we build first and why?"
```

Apex should respond with a clear, decisive brief that references SOUL.md for mission, TOOLS.md for available tools, and PROTOCOLS.md for recommended first pipeline.

If the response is generic and doesn't reference your specific setup — the soul files haven't loaded correctly. Troubleshoot the loading method.

---

## ONGOING MAINTENANCE

### Weekly (APEX does this automatically via Self-Improvement Protocol):
- Updates agent prompts in Obsidian based on performance data
- Reviews failed workflows and proposes fixes
- Sends you a Sunday summary: "What I improved this week"

### Monthly (you do this manually):
- Review BRUTAL_REVIEW.md — check which concerns have been addressed, which are still relevant
- Update TOOLS.md with any new tools you've added or removed
- Add new Protocols to PROTOCOLS.md for any new project types you've launched
- Archive old agent configs that are no longer in use

### When You Add a New Tool:
1. Add it to TOOLS.md in the appropriate section
2. Specify which LLM chain it supports
3. Add the webhook endpoint to AGENTS.md if it's a new agent
4. Test it manually once before APEX uses it in production

---

## TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| APEX gives generic responses | Soul files not loaded. Check config.toml load_order. |
| APEX hallucinates tools | Update TOOLS.md "Active Tools" section. Be explicit. |
| APEX asks too many questions | Remind it: "Check SOUL.md — you're allowed to make decisions." |
| APEX doesn't check KB first | Remind it: "KNOWLEDGE.md says: check KB before building anything." |
| Protocols don't match your setup | Edit PROTOCOLS.md to match your actual n8n webhook URLs. |

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | February 2026 | Initial release — complete soul system |

---

*These files are your empire's constitution. They define the law of the land.*
*APEX governs by these rules. Update them when your business evolves.*
