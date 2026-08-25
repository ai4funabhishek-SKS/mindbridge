# ⚙️ mindbridge Configuration Guide

Complete reference for all configuration options in `mindbridge_config.yaml`.

---

## 📁 Configuration Files

| File | Purpose | Auto-reload |
|------|---------|-------------|
| `mindbridge_config.yaml` | Main configuration | No (restart required) |
| `llm_config.yaml` | LLM provider settings | No (restart required) |
| `auto_rules.yaml` | Auto-ingestion rules | **Yes** (hot-reload) |
| `.env` | Environment variables | No (restart required) |

---

## 🔑 LLM Provider Configuration

### Provider Types

| Provider | Type | Cost | Best For |
|----------|------|------|----------|
| `opencode` | Cloud (free) | Free | Quick start, no setup |
| `groq` | Cloud (free tier) | Free* | Speed, quality |
| `ollama` | Local | Free | Privacy, offline |
| `openai_compatible` | Cloud/Local | Varies | Custom endpoints |

*Groq free tier: 1K req/day for 120B model, 14.4K req/day for 8B model

### Provider Configuration Schema

```yaml
llm_providers:
  provider_name:
    enabled: true           # Enable/disable provider
    priority: 1             # Lower = higher priority
    provider_type: "groq"   # opencode, groq, ollama, openai_compatible
    model: "model-name"     # Model identifier
    api_key_env: "ENV_VAR"  # Environment variable name
    api_key: "sk-..."       # Direct key (not recommended)
    base_url: "https://..." # Custom endpoint
    timeout: 60             # Request timeout (seconds)
    max_tokens: 4096        # Max output tokens
    temperature: 0.2        # Creativity (0-1)
    fallback_models: []     # Fallback models (Ollama only)
```

### Fallback Chain

```yaml
fallback_chain: ["opencode", "groq", "ollama"]
```

Providers are tried in order until one succeeds. Set `default_provider: "auto"` in ask_mode to use this chain.

---

## 🧠 Embeddings Configuration

```yaml
embeddings:
  provider: "ollama"           # Always local for privacy
  model: "nomic-embed-text"    # 768-dim embeddings
  base_url: "http://localhost:11434"
  dimensions: 768
  batch_size: 32
```

> **Note**: Embeddings are always local for privacy. Requires Ollama with `nomic-embed-text` pulled.

---

## 🤖 Ask Mode Configuration

```yaml
ask_mode:
  default_provider: "auto"           # "auto" = use fallback_chain
  max_passages: 12                   # Max source passages
  max_passage_chars: 700             # Max chars per passage
  context_window: 4096               # Context window size
  temperature: 0.2                   # Low = factual, high = creative
  fallback_context_windows: [4096, 2048, 1024]  # Shrink on OOM
  citation_format: "[S{num}]"        # Citation format
  save_briefings: true               # Save answers to Briefings/
  briefings_dir: "Briefings"         # Output directory
```

---

## 📂 Auto-Ingestion Configuration

### Watch Folders

```yaml
auto_ingestion:
  enabled: true
  schedule: "weekly"          # weekly, daily, manual
  schedule_time: "02:00"      # 2 AM
  timezone: "local"
  
  watch_folders:
    - path: "~/Desktop"
      recursive: true
      include_patterns: ["*"]
      exclude_patterns: ["*.tmp", "*.log", "~$*"]
  
    - path: "~/Downloads"
      recursive: true
      include_patterns: ["*"]
      exclude_patterns: ["*.tmp", "*.crdownload"]
  
    - path: "Raw_copies/incoming"
      recursive: true
      include_patterns: ["*"]
```

### Classification Rules

Rules evaluated in priority order (lower = higher priority):

```yaml
classification_rules:
  - name: "secrets_and_keys"
    priority: 10
    patterns:
      - "*key*.txt"
      - "*.env"
      - "*secret*"
    action: "vault"
    
  - name: "personal_pii"
    priority: 20
    patterns:
      - "*cv*"
      - "*statement*"
    action: "vault"
```

### Actions

| Action | Description |
|--------|-------------|
| `vault` | Move to `01_Vault_Private/` (never indexed) |
| `cold_storage` | Move to `04_Archive_Cold_Storage/` (archived) |
| `domain_name` | Route to domain folder (e.g., `06_Quantitative_Finance_and_Trading`) |
| `review` | Flag for manual review |
| `skip` | Ignore file |

### Enrichment Options

```yaml
enrichment:
  extract_entities: true      # Named entities (people, orgs, locations)
  generate_summary: true      # AI summary
  suggest_tags: true          # Auto-tag
  find_related: true          # Find related docs
  extract_actions: true       # Extract action items
  detect_language: true       # Detect language
  generate_embeddings: true   # For semantic search
```

---

## 🌐 Web UI Configuration

```yaml
web_ui:
  enabled: true
  host: "127.0.0.1"        # Bind address
  port: 7860               # Port (default 7860)
  auto_open_browser: true  # Auto-open browser
  
  auth:
    enabled: false         # Set true for LAN access
    # password: "your-password"  # Uncomment to enable
  
  wizard:
    enabled: true
    steps:
      - "welcome"
      - "provider"
      - "keys"
      - "folders"
      - "test"
```

---

## 🔍 Search Configuration

```yaml
search:
  default_mode: "ask"          # linear, graph, semantic, hybrid, ask
  default_limit: 10
  max_limit: 50
  
  bm25:
    k1: 1.2
    b: 0.75
  
  semantic:
    top_k: 50
    rerank: true
  
  hybrid:
    rrf_k: 60
    bm25_weight: 0.5
    semantic_weight: 0.5
  
  diversity:
    max_per_doc: 2
```

---

## 🗄️ Database Configuration

```yaml
database:
  path: "Processed_Assets/my_rag_data.db"
  backup_dir: "04_Archive_Cold_Storage/db_backups"
  auto_backup: true
  backup_before_mutations: true
  vacuum_after_mutations: true
```

---

## 🔐 Security Configuration

```yaml
security:
  vault_path: "01_Vault_Private"
  never_index_patterns:
    - "*key*.txt"
    - "*.env"
    - "*secret*"
    - "*credential*"
    - "*.key"
  redact_keys_in_logs: true
  never_log_keys: true
```

---

## 🧪 Testing Configuration

```yaml
testing:
  run_after_ingest: true
  run_after_config_change: true
  pytest_args: ["-q", "--tb=line"]
  coverage: false
```

---

## 📝 Logging Configuration

```yaml
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/mindbridge.log"
  max_size_mb: 10
  backup_count: 5
  console: true
```

---

## ⚙️ Advanced Settings

```yaml
advanced:
  max_concurrent_ingest: 4
  chunk_size: 512
  chunk_overlap: 50
  max_file_size_mb: 100
  supported_extensions:
    - ".md"
    - ".txt"
    - ".pdf"
    - ".docx"
    - ".xlsx"
    - ".csv"
    - ".json"
    - ".py"
    - ".js"
    - ".ts"
    - ".html"
    - ".css"
    - ".md"
    - ".rst"
```

---

## 🔄 Configuration Priority

1. **Environment variables** (highest)
2. **mindbridge_config.yaml**
2. **llm_config.yaml** (for LLM providers)
3. **auto_rules.yaml** (auto-reload)
4. **Defaults** (lowest)

---

## 🔧 Environment Variables

```bash
# Required for Groq
export GROQ_API_KEY="gsk_..."

# Optional
export OPENAI_API_KEY="sk-..."
export EMAIL_USERNAME="your@gmail.com"
export EMAIL_APP_PASSWORD="your-app-password"
export GROQ_API_KEY="gsk_..."
```

---

## ✅ Validation

Validate your config:
```bash
python -c "
import yaml
with open('mindbridge_config.yaml') as f:
    config = yaml.safe_load(f)
print('✅ Config valid')
print(f'Providers: {list(config[\"llm_providers\"].keys())}')
print(f'Fallback chain: {config[\"fallback_chain\"]}')
"
```

---

## 🔄 Hot Reload

Only `auto_rules.yaml` supports hot-reload. Other configs require restart:
```bash
# Restart Web UI
./launch_ui.ps1

# Or restart Python process
python -m pytest tests/ -q
```