# 🧠 mindbridge Quick Start Guide

> **Transform your scattered files into a searchable, intelligent Second Brain in 5 minutes.**

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Windows 10/11 (8GB+ RAM recommended)
- Python 3.10+
- Git
- Docker Desktop (for Ollama local models)

### 1. Clone & Enter
```bash
git clone https://github.com/ai4funabhishek-SKS/mindbridge.git
cd mindbridge
```

### 2. Verify Installation
```bash
python -m pytest tests/ -q
# ✅ 181 passed, 0 failed
```

### 3. Configure Your LLM (Choose One)

**Option A: Groq (Free Cloud - Recommended)**
```bash
# Get free key at https://console.groq.com/keys
echo "GROQ_API_KEY=gsk_your_key_here" > .env
```

**Option B: Ollama (Local - Private)**
```bash
# Requires Docker Desktop + 3GB RAM for WSL
wsl ollama pull nomic-embed-text
wsl ollama pull llama3.2
```

**Option C: OpenCode Zen (Free, No Key)**
```bash
# Works out of the box! No setup needed.
```

### 4. Launch Web UI
```bash
.\launch_ui.ps1
# Opens http://127.0.0.1:7860 in browser
```

### 5. Complete Wizard (5 Steps)
1. **Welcome** → Overview
2. **Provider** → Choose LLM (Groq/Ollama/OpenCode)
3. **Keys** → Paste API keys, test connections
4. **Folders** → Add watch folders (Desktop, Downloads, etc.)
5. **Test** → Run tests, launch!

---

## 🎯 What You Get

| Feature | Description |
|---------|-------------|
| **5 Search Modes** | Linear (BM25), Semantic, Hybrid (RRF), Knowledge Graph, Ask (cited answers) |
| **49 Playbooks** | Pre-built across 10 domains (AI, n8n, Finance, Content, etc.) |
| **Auto-Ingestion** | Weekly auto-scan of Desktop/Downloads/Inbox |
| **Cited Answers** | Ask questions → get answers with [S1], [S2] source citations |
| **Zero Cloud for Secrets** | Your API keys & files never leave your machine |
| **Auto-Resume** | Restart? Run `.\resume_mindbridge.ps1` to see status instantly |

---

## 🎮 Common Commands

```bash
# Search your knowledge base
python search_engine.py "crypto trading strategies" --mode ask --save

# Different search modes
python search_engine.py "n8n workflow" --mode hybrid
python search_engine.py "Groq API" --mode semantic
python search_engine.py "langchain" --mode graph

# Force specific LLM
python search_engine.py "question" --mode ask --model groq
python search_engine.py "question" --mode ask --model ollama

# Run tests
python -m pytest tests/ -q

# Rebuild indexes
python build_doc_anchors.py --force
python build_folder_indexes.py
python deep_inspect_and_build_dashboard.py
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `mindbridge_config.yaml` | Main configuration |
| `auto_rules.yaml` | Auto-ingestion rules |
| `llm_config.yaml` | LLM provider settings |
| `START_HERE.md` | This file |
| `PROJECT_STATE.md` | Project diary |
| `GK_242_FILE_REVIEW.csv` | File audit log |
| `web_ui/` | Web UI wizard |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Permission denied" on CSV | Close Excel, retry |
| "No module named fastapi" | `pip install -r requirements.txt` |
| Ollama not found | Start Docker Desktop, run `wsl ollama serve` |
| Groq 403 error | Regenerate API key at console.groq.com |
| Tests fail | Run `python -m pytest tests/ -v --tb=short` |

---

## 🔐 Security Notes

- **API keys** stored in `.env` (gitignored)
- **Vault files** in `01_Vault_Private/` (gitignored)
- **Database** in `Processed_Assets/` (gitignored)
- **Never commit secrets** - use `.env` or environment variables

---

## 🚀 Next Steps

1. **Add your files** to `Raw_copies/incoming/` or watch folders
2. **Run ingestion**: `python weekly_school.py`
3. **Ask questions**: `python search_engine.py "your question" --mode ask`
4. **Automate**: Run `.\setup_scheduler.ps1` (Admin) for weekly auto-ingestion

---

**Need help?** Check `docs/FAQ.md` or open an issue on GitHub.

**Happy bridging!** 🧠🌉