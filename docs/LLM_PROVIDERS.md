# 🤖 mindbridge LLM Provider Guide

Complete guide to configuring and using different LLM backends with mindbridge.

---

## 🎯 Supported Providers

| Provider | Type | Cost | Speed | Best For |
|----------|------|------|-------|----------|
| **OpenCode Zen** | Cloud (Free) | Free | Medium | Quick start, no setup |
| **Groq** | Cloud (Free Tier) | Free* | ⚡ Fastest | Production, speed |
| **Ollama** | Local | Free | Variable | Privacy, offline |
| **OpenAI Compatible** | Cloud/Local | Varies | Variable | Custom endpoints |

*Groq free tier: 1K req/day (120B), 14.4K req/day (8B)

---

## 🚀 Quick Provider Comparison

| Feature | OpenCode Zen | Groq | Ollama | OpenAI Compatible |
|---------|--------------|------|--------|-------------------|
| **Setup Time** | 0 min | 2 min | 10 min | 5 min |
| **API Key** | ❌ None | ✅ Required | ❌ None | ✅ Required |
| **Privacy** | Cloud | Cloud | **Local** | Depends |
| **Models** | freemodel | gpt-oss-120b, llama-3.1-8b | Any GGUF | Any OpenAI-compatible |
| **Speed** | Medium | ⚡ Fastest | Variable | Variable |
| **Offline** | ❌ | ❌ | ✅ | Depends |
| **Rate Limits** | Generous | 1K/day (120B) | None | Varies |
| **Best For** | Quick start | Production speed | Privacy/Offline | Custom endpoints |

---

## 🔧 Provider Setup Guides

### 1. OpenCode Zen (Easiest - No Setup!)

```yaml
# llm_config.yaml
llm_providers:
  opencode:
    enabled: true
    priority: 1
    provider_type: "opencode"
    model: "freemodel"
    # No API key needed!
```

**Pros:** Zero setup, free, works immediately  
**Cons:** Slower, limited model choice

---

### 2. Groq (Recommended for Speed)

**Get API Key:**
1. Go to [console.groq.com/keys](https://console.groq.com/keys)
2. Sign in with GitHub/Google
3. Create API Key (starts with `gsk_`)

```bash
# Add to .env
echo "GROQ_API_KEY=gsk_your_key_here" >> .env
```

```yaml
# llm_config.yaml
llm_providers:
  groq:
    enabled: true
    priority: 2
    provider_type: "groq"
    model: "openai/gpt-oss-120b"  # or llama-3.1-8b-instant
    api_key_env: "GROQ_API_KEY"
    base_url: "https://api.groq.com/openai/v1"
    timeout: 60
    max_tokens: 4096
    temperature: 0.2
```

**Model Options:**
| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `openai/gpt-oss-120b` | Medium | Highest | Complex reasoning |
| `llama-3.1-8b-instant` | ⚡ Fastest | High | Quick answers |
| `qwen/qwen3-32b` | Fast | High | Coding, multilingual |
| `gemma2-9b-it` | Fast | Good | General chat |

**Rate Limits (Free Tier):**
| Model | RPM | RPD | TPM |
|-------|-----|-----|-----|
| gpt-oss-120b | 30 | 1,000 | 12K |
| llama-3.1-8b-instant | 30 | 14,400 | 6K |

---

### 3. Ollama (Local - Maximum Privacy)

**Prerequisites:**
- Docker Desktop installed
- 8GB+ RAM (4GB for WSL + 4GB for model)

**Setup:**
```bash
# Start Docker Desktop
# In WSL/PowerShell:
wsl ollama pull nomic-embed-text  # Required for embeddings
wsl ollama pull llama3.2          # Main model
wsl ollama pull phi3:mini         # Fallback (smaller)
wsl ollama pull qwen2.5:7b-instruct  # Alternative
```

```yaml
llm_providers:
  ollama:
    enabled: true
    priority: 3
    provider_type: "ollama"
    model: "llama3.2"
    base_url: "http://localhost:11434"
    timeout: 120
    max_tokens: 4096
    temperature: 0.2
    fallback_models:
      - "phi3:mini"
      - "qwen2.5:7b-instruct"
```

**Verify:**
```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Test model
curl -X POST http://localhost:11434/api/chat \
  -d '{"model": "llama3.2", "messages": [{"role": "user", "content": "Hello"}], "stream": false}'
```

**Model Recommendations for 8GB RAM:**
| Model | Size | RAM | Quality |
|-------|------|-----|---------|
| `phi3:mini` | 2.2GB | ~3GB | Good |
| `llama3.2` | 2GB | ~3GB | Good |
| `qwen2.5:7b` | 4.7GB | ~6GB | High |
| `gemma2:9b` | 5.4GB | ~7GB | High |

---

### 4. OpenAI-Compatible Endpoints

Works with: OpenAI, Azure OpenAI, LocalAI, vLLM, Text Generation Inference, etc.

```yaml
openai_compatible:
  enabled: true
  priority: 4
  provider_type: "openai_compatible"
  model: "gpt-3.5-turbo"
  api_key_env: "OPENAI_API_KEY"
  base_url: "https://api.openai.com/v1"  # or your endpoint
  timeout: 60
  max_tokens: 4096
  temperature: 0.2
```

**Common Endpoints:**
| Provider | Base URL | API Key Env |
|----------|----------|-------------|
| OpenAI | `https://api.openai.com/v1` | `OPENAI_API_KEY` |
| Azure OpenAI | `https://{resource}.openai.azure.com` | `AZURE_OPENAI_KEY` |
| LocalAI | `http://localhost:8080/v1` | (none) |
| vLLM | `http://localhost:8000/v1` | (none) |
| TGI | `http://localhost:8080/v1` | (none) |

---

## 🔄 Fallback Chain Configuration

```yaml
fallback_chain: ["opencode", "groq", "ollama"]
```

**How it works:**
1. Try `opencode` (free, no key) → if fails/timeout
2. Try `groq` (fast cloud) → if fails/rate limited
3. Try `ollama` (local) → if fails
4. Return error

**Customize priority:**
```yaml
llm_providers:
  groq:
    priority: 1  # Try first
  opencode:
    priority: 2  # Try second
  ollama:
    priority: 3  # Try last
```

---

## 🎯 Ask Mode Provider Selection

### Via CLI
```bash
# Use specific provider
python search_engine.py "question" --mode ask --model groq
python search_engine.py "question" --mode ask --model ollama
python search_engine.py "question" --mode ask --model opencode

# Auto (uses fallback chain)
python search_engine.py "question" --mode ask --model auto
```

### Via Web UI
1. Go to **Step 2: Provider** → Select primary
2. Go to **Step 3: Keys** → Add API keys
3. Go to **Step 5: Test** → Click "Test Connection"
4. Drag providers in fallback chain to reorder

### Per-Query Override
```bash
# Override for single query
python search_engine.py "question" --mode ask --model groq:llama-3.1-8b-instant
```

---

## 🔧 Troubleshooting

### Groq 403 Forbidden
- **Cause:** Invalid/expired key, or model not available
- **Fix:** Regenerate key at console.groq.com, check model name

### Ollama Connection Refused
- **Cause:** Ollama not running
- **Fix:** `wsl ollama serve` or start Docker Desktop

### Ollama Model Not Found
- **Cause:** Model not pulled
- **Fix:** `wsl ollama pull model-name`

### Groq Rate Limited (429)
- **Cause:** Exceeded free tier limits
- **Fix:** Wait for reset, or add `groq` fallback to `ollama`

### OpenCode Zen Slow/Timeout
- **Cause:** Free tier congestion
- **Fix:** Move `groq` to priority 1 in fallback chain

### Out of Memory (OOM)
- **Cause:** Context window too large
- **Fix:** Reduce `context_window` in ask_mode config, or use smaller model

---

## 🔧 Advanced: Custom Provider

Add custom OpenAI-compatible provider:

```yaml
llm_providers:
  my_custom:
    enabled: true
    priority: 1
    provider_type: "openai_compatible"
    model: "my-model"
    api_key_env: "MY_API_KEY"
    base_url: "http://my-server:8000/v1"
    timeout: 60
```

Then use: `--model my_custom`

---

## 📊 Monitoring Provider Health

```bash
# Check all providers
python -c "
from llm_providers import LLMManager
m = LLMManager()
for name, p in m.providers.items():
    print(f'{name}: available={p.is_available()}, model={p.get_model()}')
"
```

### Health Check Endpoint (Web UI)
```
GET /api/status
```
Returns:
```json
{
  "ollama": {"available": true, "models": ["llama3.2", "phi3:mini"]},
  "groq": {"available": true},
  "database": {"documents": 338, "chunks": 10075}
}
```

---

## 💡 Pro Tips

1. **Use Groq as primary** - fastest free option
2. **Keep Ollama as fallback** - works offline
3. **Set `GROQ_API_KEY` in `.env`** - never commit keys
4. **Test each provider** in Web UI Step 3 before finishing
5. **Monitor rate limits** - Groq free tier has daily limits

---

## 🔮 Future Providers (Planned)

- [ ] Anthropic (Claude)
- [ ] Cohere
- [ ] Together AI
- [ ] Replicate
- [ ] HuggingFace Inference API
- [ ] Custom vLLM/TGI endpoints

---

**Need help?** Check [Troubleshooting](#troubleshooting) or open an issue!