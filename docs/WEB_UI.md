# 🌐 mindbridge Web UI Guide

Complete guide to the Web UI Wizard and administration interface.

---

## 🚀 Quick Start

```bash
# Launch the Web UI
.\launch_ui.ps1

# Or manually
python -m uvicorn web_ui.main:app --host 127.0.0.1 --port 7860 --reload
```

Opens automatically at: **http://127.0.0.1:7860**

---

## 🧙 Wizard Walkthrough (5 Steps)

### Step 1: Welcome
- Overview of mindbridge capabilities
- Click "Let's Get Started" to begin

### Step 2: LLM Provider
- Choose primary provider (Groq/Ollama/OpenCode)
- Configure fallback chain order
- Set model preferences

### Step 3: API Keys
- Enter API keys for cloud providers
- Test connections before proceeding
- Keys stored in `.env` (never committed)

### Step 4: Watch Folders
- Add folders to monitor (Desktop, Downloads, etc.)
- Configure include/exclude patterns
- Test folder accessibility

### Step 5: Test & Launch
- Test all LLM connections
- Run full test suite (181 tests)
- Run manual ingestion
- Launch Web UI

---

## 🎛️ Web UI Features

### Dashboard (Coming Soon)
- System health overview
- Document statistics
- Recent activity
- Quick search

### Configuration Management
- Visual config editor
- Real-time validation
- Hot-reload for auto_rules.yaml

### LLM Management
- Test provider connections
- Switch providers on-the-fly
- Configure fallback chains
- Monitor rate limits

### Folder Management
- Add/remove watch folders
- Configure include/exclude patterns
- Test folder accessibility
- Preview file counts

### Test & Monitoring
- Run full test suite (181 tests)
- Manual ingestion trigger
- View test results
- System health status

---

## 🔧 Configuration via Web UI

All settings in `mindbridge_config.yaml` editable via UI:

| Section | Editable via UI |
|---------|-----------------|
| LLM Providers | ✅ Yes |
| Fallback Chain | ✅ Yes (drag-drop) |
| API Keys | ✅ Yes (masked input) |
| Watch Folders | ✅ Yes (add/remove/test) |
| Classification Rules | ✅ Yes |
| Search Settings | ✅ Yes |
| Web UI Settings | ✅ Yes |

**Note:** Changes to `mindbridge_config.yaml` require restart. `auto_rules.yaml` hot-reloads.

---

## 🔐 Authentication

### Options

| Mode | Use Case |
|------|----------|
| **None** (default) | Local development, trusted network |
| **Password** | LAN access, shared team |

### Enable Password Auth

```yaml
# mindbridge_config.yaml
web_ui:
  auth:
    enabled: true
    password: "your-secure-password"
```

Or via Web UI → Settings → Authentication.

---

## 🔌 API Reference

### Base URL
```
http://127.0.0.1:7860
```

### Endpoints

#### Configuration
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/config` | Get current config (keys masked) |
| POST | `/api/config` | Save configuration |
| GET | `/api/auto-rules` | Get auto-ingestion rules |
| POST | `/api/auto-rules` | Save auto-ingestion rules |

#### LLM Testing
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/test/llm` | Test LLM connection |
| POST | `/api/test/folders` | Test folder accessibility |
| POST | `/api/test/run` | Run full test suite |
| POST | `/api/ingest/run` | Trigger manual ingestion |

#### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | System health |
| GET | `/health` | Health check |

### Example: Test LLM Connection

```bash
curl -X POST http://127.0.0.1:7860/api/test/llm \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "groq",
    "model": "openai/gpt-oss-120b",
    "api_key": "gsk_...",
    "base_url": "https://api.groq.com/openai/v1"
  }'
```

Response:
```json
{
  "success": true,
  "response": "OK. I'm ready to help!",
  "provider": "groq",
  "model": "openai/gpt-oss-120b"
}
```

---

## 🎨 Customization

### Theming
Edit `web_ui/static/styles.css`:
```css
:root {
  --primary-color: #3b82f6;
  --secondary-color: #8b5cf6;
  --success-color: #10b981;
  --error-color: #ef4444;
}
```

### Custom Templates
Edit templates in `web_ui/templates/`:
- `base.html` - Base layout
- `wizard_*.html` - Wizard steps

---

## 🔧 Development

### Run in Development
```bash
cd web_ui
python -m uvicorn main:app --host 127.0.0.1 --port 7860 --reload
```

### Run Tests
```bash
cd web_ui
python -m pytest ../tests/ -q
```

### Build for Production
```bash
# No build step needed! Alpine.js loads from CDN
# Just copy web_ui/ to production server
```

---

## 🐳 Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 7860
CMD ["uvicorn", "web_ui.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

```bash
docker build -t mindbridge .
docker run -p 7860:7860 -v $(pwd)/data:/app/Processed_Assets mindbridge
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 7860 in use | Change port in `launch_ui.ps1` or `mindbridge_config.yaml` |
| Module not found | `pip install -r requirements.txt` |
| CORS errors | Check `host` in config, use `127.0.0.1` not `localhost` |
| WebSocket errors | Disable browser extensions, try incognito |
| Config not saving | Check file permissions, run as admin |

---

## 🔗 Useful Links

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Alpine.js Docs**: https://alpinejs.dev
- **Tailwind CSS**: https://tailwindcss.com
- **Uvicorn**: https://www.uvicorn.org

---

## 📝 API Examples

### Python Client
```python
import requests

BASE = "http://127.0.0.1:7860"

# Get config
config = requests.get(f"{BASE}/api/config").json()

# Test LLM
result = requests.post(f"{BASE}/api/test/llm", json={
    "provider": "groq",
    "model": "openai/gpt-oss-120b",
    "api_key": "gsk_...",
    "base_url": "https://api.groq.com/openai/v1"
}).json()

# Run tests
result = requests.post(f"{BASE}/api/test/run").json()

# Run ingestion
result = requests.post(f"{BASE}/api/ingest/run").json()
```

### JavaScript/TypeScript
```typescript
const API = 'http://127.0.0.1:7860';

async function testLLM(provider: string, model: string, apiKey: string) {
  const res = await fetch(`${API}/api/test/llm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider, model, api_key: apiKey })
  });
  return res.json();
}
```

---

## 📚 Related Docs

- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup
- [CONFIGURATION.md](CONFIGURATION.md) - All config options
- [LLM_PROVIDERS.md](LLM_PROVIDERS.md) - Provider details
- [FAQ.md](FAQ.md) - Common questions