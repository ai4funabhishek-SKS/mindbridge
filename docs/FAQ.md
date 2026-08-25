# ❓ mindbridge FAQ

Frequently asked questions about mindbridge Second Brain.

---

## 🚀 Getting Started

### Q: What is mindbridge?
**A:** mindbridge is a local-first, privacy-first Second Brain that transforms your scattered files (PDFs, docs, code, notes) into a searchable, intelligent knowledge base with cited answers. It runs entirely on your machine — your data never leaves your computer unless you choose to use a cloud LLM.

### Q: How is this different from Obsidian/Notion/Roam?
| Feature | mindbridge | Obsidian | Notion | Roam |
|---------|------------|----------|--------|------|
| **Local-first** | ✅ | ✅ | ❌ | ❌ |
| **AI Search** | ✅ (5 modes) | Via plugins | ✅ (cloud) | Via plugins |
| **Cited Answers** | ✅ Native | Via plugins | ✅ | Via plugins |
| **Auto-ingestion** | ✅ Native | Manual | Manual | Manual |
| **Cost** | Free | Free/Paid | Paid | Paid |
| **Self-hosted** | ✅ | ✅ | ❌ | ❌ |

### Q: Do I need to know how to code?
**No!** The Web UI Wizard guides you through 5 simple steps. No coding required. The system is designed for non-technical users.

### Q: What are the system requirements?
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows 10/11 | Windows 10/11 |
| RAM | 8 GB | 16 GB |
| CPU | 2 cores | 4+ cores |
| Disk | 5 GB free | 20 GB free |
| Docker | Required for Ollama | Required for Ollama |
| Python | 3.10+ | 3.11+ |

---

## 🔐 Privacy & Security

### Q: Is my data really private?
**Yes!** 
- Your files **never leave your machine** unless you use a cloud LLM
- API keys stored in `.env` (gitignored)
- Vault files in `01_Vault_Private/` (gitignored)
- Embeddings run locally via Ollama
- Only Ask mode excerpts go to cloud LLM (if you use Groq/OpenCode)

### Q: Can I use this completely offline?
**Yes!** Use Ollama for both embeddings and LLM. No internet required after initial model downloads.

### Q: Where are my API keys stored?
In a `.env` file in the project root (gitignored). Never committed to git. The Web UI shows masked keys (`***`).

### Q: Can I use this for sensitive business data?
**Yes!** The vault system keeps sensitive files (keys, PII, financials) completely separate from the searchable index. They're stored in `01_Vault_Private/` and never enter the search index.

---

## 🤖 LLM Providers

### Q: Which LLM provider should I use?
| Use Case | Recommendation |
|----------|----------------|
| **Quick start, no setup** | OpenCode Zen (default) |
| **Fastest, free tier** | Groq (`gpt-oss-120b`) |
| **Maximum privacy, offline** | Ollama (llama3.2/phi3) |
| **Custom endpoint** | OpenAI-compatible |

### Q: Do I need an API key for OpenCode Zen?
**No!** OpenCode Zen works out of the box with `freemodel`. No API key, no signup.

### Q: How do I get a Groq API key?
1. Go to [console.groq.com/keys](https://console.groq.com/keys)
2. Sign in with GitHub/Google
3. Create API Key (starts with `gsk_`)
4. Add to `.env`: `GROQ_API_KEY=gsk_your_key`

### Q: Can I use multiple providers at once?
**Yes!** Configure fallback chain: `["groq", "ollama", "opencode"]`. System tries each until one succeeds.

### Q: How do I switch providers?
```bash
# CLI
python search_engine.py "question" --mode ask --model groq
python search_engine.py "question" --mode ask --model ollama

# Web UI: Step 2 → Choose provider → Step 5 → Test
```

### Q: What models does Groq support?
| Model | Speed | Quality | Free Tier |
|-------|-------|---------|-----------|
| `openai/gpt-oss-120b` | Medium | Highest | 1K req/day |
| `llama-3.1-8b-instant` | ⚡ Fast | High | 14.4K req/day |
| `qwen/qwen3-32b` | Fast | High | 1K req/day |

### Q: How do I use Ollama locally?
```bash
# Install Docker Desktop
# In WSL/PowerShell:
wsl ollama pull nomic-embed-text  # Required for embeddings
wsl ollama pull llama3.2          # Main model
wsl ollama pull phi3:mini         # Fallback (smaller)
```

### Q: Can I use OpenAI/GPT-4?
Yes, via OpenAI-compatible endpoint:
```yaml
openai_compatible:
  enabled: true
  model: "gpt-4"
  api_key_env: "OPENAI_API_KEY"
  base_url: "https://api.openai.com/v1"
```

---

## 🔍 Search & Ask

### Q: What are the 5 search modes?
| Mode | Best For |
|--------|----------|
| **linear** | Exact keyword matches (BM25) |
| **semantic** | Meaning-based similarity |
| **hybrid** | Best of both (RRF fusion) |
| **graph** | Entity relationships |
| **ask** | Cited answers from your docs |

### Q: How does Ask mode work?
1. **Retrieves** relevant passages (BM25 + semantic + anchors)
2. **Filters** by topic/gem filters
3. **Synthesizes** answer via LLM with citations `[S1]`, `[S2]`
4. **Saves** to `Briefings/` if `--save` flag used

### Q: Why are my search results poor?
- **Run ingestion**: `python weekly_school.py` or `python process_gms.py`
- **Rebuild anchors**: `python build_doc_anchors.py --force`
- **Check topic filters**: Use `--topic` or `--gems` flags
- **Rebuild indexes**: `python build_folder_indexes.py`

### Q: How do I search for specific topics?
```bash
# Topic filter
python search_engine.py "trading" --topic "Quantitative Finance" --mode hybrid

# Gems only (reusability ≥8)
python search_engine.py "prompt" --gems --mode hybrid

# List all topics
python search_engine.py --topics
```

### Q: Can I save Ask answers?
```bash
# Save to Briefings/
python search_engine.py "question" --mode ask --save
```

---

## 📁 File Management

### Q: Where do I put my files?
Drop files in any **watch folder**:
- `~/Desktop`
- `~/Downloads`
- `~/Documents/Inbox`
- `Raw_copies/incoming/`

Or run manual ingestion:
```bash
python weekly_school.py
```

### Q: What file types are supported?
| Type | Extensions |
|------|------------|
| Documents | `.pdf`, `.docx`, `.txt`, `.md`, `.rst` |
| Data | `.csv`, `.xlsx`, `.json`, `.csv` |
| Code | `.py`, `.js`, `.ts`, `.html`, `.css` |
| Config | `.yaml`, `.yml`, `.toml`, `.ini` |

### Q: How does auto-ingestion work?
1. **Monitor** watches folders for new files
2. **Classify** using rules (vault/cold_storage/domain)
3. **Enrich** with LLM (entities, summary, tags)
4. **Index** into SQLite FTS5 + Knowledge Graph
5. **Regenerate** dashboards & indexes
6. **Email report** sent

### Q: How do I add custom watch folders?
Edit `auto_rules.yaml`:
```yaml
watch_folders:
  - path: "~/MyFolder"
    recursive: true
    include_patterns: ["*.pdf", "*.md"]
    exclude_patterns: ["*.tmp", "*.log"]
```
Or use Web UI → Step 4 → Add Folder.

### Q: What happens to duplicate files?
Duplicates (`dup_*`, `Copy of *`, `(1)`, `(2)`) are automatically detected and sent to cold storage. Originals stay in Raw_copies.

---

## 🛠️ Technical

### Q: How do I update mindbridge?
```bash
git pull
python -m pytest tests/ -q
# If tests pass:
python build_doc_anchors.py --force
python build_folder_indexes.py
python deep_inspect_and_build_dashboard.py
```

### Q: How do I backup my knowledge base?
```bash
# Database backup
cp Processed_Assets/my_rag_data.db backups/

# Full backup (includes Raw_copies)
tar -czf mindbridge-backup-$(date +%Y%m%d).tar.gz \
  --exclude=__pycache__ --exclude=.git \
  --exclude=04_Archive_Cold_Storage/db_backups \
  .
```

### Q: How do I move to another computer?
1. Copy entire `mindbridge` folder
2. On new machine: `.\launch_ui.ps1` (auto-installs deps)
3. Or copy to L1 laptop and use `_handoff/L1_second_brain_refinement/SKILL.md`

### Q: How do I reset everything?
```bash
# Reset database (keeps Raw_copies)
rm Processed_Assets/my_rag_data.db
python init_rag_and_knowledge_graph.py
python build_doc_anchors.py --force
python build_folder_indexes.py
python deep_inspect_and_build_dashboard.py
```

### Q: Python version issues?
```bash
# Check version
python --version  # Need 3.10+

# Use pyenv (recommended)
pyenv install 3.11.0
pyenv local 3.11.0
```

---

## 🐛 Troubleshooting

### "Permission denied" on CSV
**Close Excel** and retry. Excel locks CSV files.

### "Module not found" errors
```bash
pip install -r requirements.txt
# Or in venv:
python -m pip install -r requirements.txt
```

### Ollama not found
```bash
# Start Docker Desktop
# In WSL:
wsl ollama serve
```

### Groq 403 Forbidden
- Regenerate key at console.groq.com
- Check model name (e.g., `openai/gpt-oss-120b`)
- Verify `.env` has `GROQ_API_KEY=gsk_...`

### Tests failing
```bash
# Run with details
python -m pytest tests/ -v --tb=short

# Specific test
python -m pytest tests/test_ask_mode.py -v
```

### Out of Memory (OOM)
- Reduce `context_window` in ask_mode config
- Use smaller model (`phi3:mini` instead of `llama3.2`)
- Increase WSL memory in `.wslconfig`: `memory=6GB`

### Web UI won't start
```bash
# Check port
netstat -an | findstr 7860

# Kill existing
taskkill /F /IM python.exe

# Restart
.\launch_ui.ps1
```

### Tests failing after cleanup
```bash
# Re-run after DB rebuild
python -m pytest tests/ -q
# Should be 181 passed
```

---

## 💡 Tips & Tricks

### Better Search Results
1. Use `--topic` to narrow domain
2. Use `--gems` for high-quality content only
2. Try `--mode hybrid` for best results
4. Rebuild anchors after adding files: `python build_doc_anchors.py --force`

### Faster Ingestion
- Use `--limit` on search to reduce context
- Enable `auto_ingestion.rebuild_on_ingest: false` for speed
- Run weekly via scheduler instead of manual

### Organize Your Knowledge
- Use `--topic` filters consistently
- Tag business ideas with `#business-idea` in filename
- Use `Quick Prompts` domain for reusable prompts
- Tag templates with `template` in filename

---

## 📞 Getting Help

| Resource | Link |
|----------|------|
| **GitHub Issues** | [github.com/ai4funabhishek-SKS/mindbridge/issues](https://github.com/ai4funabhishek-SKS/mindbridge/issues) |
| **Discussions** | [github.com/ai4funabhishek-SKS/mindbridge/discussions](https://github.com/ai4funabhishek-SKS/mindbridge/discussions) |
| **Email** | Aiadoptionconsultant@gmail.com |

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

Apache 2.0 - See [LICENSE](LICENSE) for details.

---

*Last updated: 2026-08-25 | mindbridge v1.0*