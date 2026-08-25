"""
mindbridge Web UI - FastAPI Backend
Web UI Wizard for configuring mindbridge Second Brain
"""

import os
import sys
import json
import yaml
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import uvicorn

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from llm_providers import LLMManager, LLMConfig, create_default_config

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / "mindbridge_config.yaml"
AUTO_RULES_PATH = PROJECT_ROOT / "auto_rules.yaml"
WEB_UI_DIR = Path(__file__).parent

# Global state
app_state = {
    "config": None,
    "auto_rules": None,
    "llm_manager": None,
}

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class LLMProviderConfig(BaseModel):
    name: str
    enabled: bool = True
    priority: int = 1
    provider_type: str
    model: str
    api_key_env: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60
    max_tokens: int = 4096
    temperature: float = 0.2
    fallback_models: List[str] = []

class EmbeddingConfig(BaseModel):
    provider: str = "ollama"
    model: str = "nomic-embed-text"
    base_url: str = "http://localhost:11434"
    dimensions: int = 768
    batch_size: int = 32

class AskModeConfig(BaseModel):
    default_provider: str = "auto"
    max_passages: int = 12
    max_passage_chars: int = 700
    context_window: int = 4096
    temperature: float = 0.2
    fallback_context_windows: List[int] = [4096, 2048, 1024]
    citation_format: str = "[S{num}]"
    save_briefings: bool = True
    briefings_dir: str = "Briefings"

class WatchFolderConfig(BaseModel):
    path: str
    recursive: bool = True
    include_patterns: List[str] = ["*"]
    exclude_patterns: List[str] = []

class ClassificationRuleConfig(BaseModel):
    name: str
    priority: int
    patterns: List[str]
    action: str
    description: str = ""

class AutoRulesConfig(BaseModel):
    watch_folders: List[WatchFolderConfig] = []
    classification_rules: List[ClassificationRuleConfig] = []

class MindbridgeConfig(BaseModel):
    llm_providers: Dict[str, Any] = {}
    fallback_chain: List[str] = ["opencode", "groq", "ollama"]
    embeddings: Dict[str, Any] = {}
    ask_mode: Dict[str, Any] = {}
    auto_ingestion: Dict[str, Any] = {}
    web_ui: Dict[str, Any] = {}
    search: Dict[str, Any] = {}
    database: Dict[str, Any] = {}
    dashboards: Dict[str, Any] = {}
    security: Dict[str, Any] = {}
    testing: Dict[str, Any] = {}
    logging: Dict[str, Any] = {}
    advanced: Dict[str, Any] = {}

class TestConnectionRequest(BaseModel):
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str

class SaveConfigRequest(BaseModel):
    config: Dict[str, Any]

class TestFoldersRequest(BaseModel):
    watch_folders: List[Dict[str, Any]]

class RunTestsRequest(BaseModel):
    pass

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_yaml(path: Path) -> Dict:
    """Load YAML file safely."""
    if not path.exists():
        return {}
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}

def save_yaml(path: Path, data: Dict) -> None:
    """Save YAML file with nice formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)

def load_config() -> Dict:
    """Load main config."""
    if CONFIG_PATH.exists():
        return load_yaml(CONFIG_PATH)
    return {}

def load_auto_rules() -> Dict:
    """Load auto rules."""
    if AUTO_RULES_PATH.exists():
        return load_yaml(AUTO_RULES_PATH)
    return {}

def save_config(config: Dict) -> None:
    """Save main config."""
    save_yaml(CONFIG_PATH, config)

def save_auto_rules(rules: Dict) -> None:
    """Save auto rules."""
    save_yaml(AUTO_RULES_PATH, rules)

def get_llm_manager():
    """Get or create LLM manager."""
    from llm_providers import LLMManager
    return LLMManager(str(PROJECT_ROOT / "llm_config.yaml"))

# ============================================================================
# FASTAPI APP
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app_state["config"] = load_config()
    app_state["auto_rules"] = load_auto_rules()
    try:
        from llm_providers import LLMManager
        app_state["llm_manager"] = LLMManager(str(PROJECT_ROOT / "llm_config.yaml"))
    except Exception as e:
        print(f"LLM Manager init failed: {e}")
        app_state["llm_manager"] = None
    yield
    # Shutdown

app = FastAPI(
    title="mindbridge Web UI",
    description="Configuration wizard for mindbridge Second Brain",
    version="1.0.0",
    lifespan=lifespan,
)

# Static files and templates
app.mount("/static", StaticFiles(directory=str(WEB_UI_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(WEB_UI_DIR / "templates"))

# ============================================================================
# WIZARD ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def wizard_welcome(request: Request):
    """Step 1: Welcome"""
    return templates.TemplateResponse("wizard_welcome.html", {"request": request})

@app.get("/provider", response_class=HTMLResponse)
async def wizard_provider(request: Request):
    """Step 2: Choose LLM Provider"""
    config = load_config()
    providers = config.get("llm_providers", {})
    return templates.TemplateResponse("wizard_provider.html", {
        "request": request,
        "providers": providers,
        "fallback_chain": config.get("fallback_chain", ["opencode", "groq", "ollama"])
    })

@app.get("/keys", response_class=HTMLResponse)
async def wizard_keys(request: Request):
    """Step 3: API Keys"""
    config = load_config()
    providers = config.get("llm_providers", {})
    return templates.TemplateResponse("wizard_keys.html", {
        "request": request,
        "providers": providers,
    })

@app.get("/folders", response_class=HTMLResponse)
async def wizard_folders(request: Request):
    """Step 4: Watch Folders"""
    auto_rules = load_auto_rules()
    watch_folders = auto_rules.get("watch_folders", [])
    return templates.TemplateResponse("wizard_folders.html", {
        "request": request,
        "watch_folders": watch_folders,
    })

@app.get("/test", response_class=HTMLResponse)
async def wizard_test(request: Request):
    """Step 5: Test & Launch"""
    config = load_config()
    return templates.TemplateResponse("wizard_test.html", {
        "request": request,
        "config": config,
    })

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/api/config")
async def get_config():
    """Get current configuration."""
    config = load_config()
    # Remove sensitive data
    safe_config = json.loads(json.dumps(config))
    # Mask API keys
    for provider_name, provider in safe_config.get("llm_providers", {}).items():
        if "api_key" in provider:
            provider["api_key"] = "***" if provider.get("api_key") else ""
    return safe_config

@app.post("/api/config")
async def save_config(request: SaveConfigRequest):
    """Save configuration."""
    try:
        save_yaml(CONFIG_PATH, request.config)
        return {"success": True, "message": "Configuration saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test/llm")
async def test_llm_connection(request: TestConnectionRequest):
    """Test LLM connection."""
    try:
        from llm_providers import LLMConfig, LLMProviderFactory
        
        config = LLMConfig(
            name=request.provider,
            provider_type=request.provider,
            model=request.model,
            api_key=request.api_key,
            base_url=request.base_url,
        )
        
        provider = LLMProviderFactory.create(config)
        
        if not provider.is_available():
            return {"success": False, "error": f"Provider {request.provider} not available"}
        
        # Test with a simple message
        test_messages = [{"role": "user", "content": "Say 'OK' if you can hear me."}]
        response = provider.chat(test_messages, max_tokens=10, temperature=0)
        
        return {
            "success": True,
            "response": response,
            "provider": request.provider,
            "model": request.model
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/test/folders")
async def test_folders(request: TestFoldersRequest):
    """Test watch folders accessibility."""
    results = []
    for folder in request.watch_folders:
        path = Path(folder["path"]).expanduser()
        exists = path.exists()
        readable = False
        file_count = 0
        
        if exists:
            try:
                # Count files (sample)
                for _ in path.rglob("*"):
                    file_count += 1
                    if file_count > 1000:
                        break
                readable = True
            except Exception as e:
                readable = False
        
        results.append({
            "path": str(path),
            "exists": exists,
            "readable": readable,
            "file_count_estimate": file_count
        })
    
    return {"folders": results}

@app.post("/api/test/run")
async def run_tests():
    """Run full test suite."""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/", "-q", "--tb=line"
        ], capture_output=True, text=True, timeout=300, cwd=PROJECT_ROOT)
        
        return {
            "passed": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout[-3000:] if result.stdout else "",
            "stderr": result.stderr[-3000:] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "error": "Test timeout (5 min)"}
    except Exception as e:
        return {"passed": False, "error": str(e)}

@app.post("/api/ingest/run")
async def run_ingestion():
    """Trigger manual ingestion."""
    try:
        result = subprocess.run([
            sys.executable, "weekly_school.py"
        ], capture_output=True, text=True, timeout=600, cwd=PROJECT_ROOT)
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout[-3000:] if result.stdout else "",
            "stderr": result.stderr[-3000:] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Ingestion timeout (10 min)"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/status")
async def get_status():
    """Get system status."""
    # Check database
    db_status = {}
    try:
        import sqlite3
        conn = sqlite3.connect(PROJECT_ROOT / "Processed_Assets" / "my_rag_data.db")
        for table in ["documents", "chunks", "chunks_fts", "doc_anchors", "kg_nodes", "kg_edges"]:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            db_status[table] = count
        conn.close()
    except Exception:
        db_status = {"error": "Database not accessible"}
    
    # Check Ollama
    ollama_status = {"available": False, "models": []}
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            ollama_status["available"] = True
            ollama_status["models"] = [m["name"] for m in data.get("models", [])]
    except Exception:
        pass
    
    # Check Groq
    groq_status = {"available": False}
    if os.environ.get("GROQ_API_KEY"):
        groq_status["available"] = True
    
    return {
        "database": db_status,
        "ollama": ollama_status,
        "groq": groq_status,
        "config_loaded": CONFIG_PATH.exists(),
        "auto_rules_loaded": AUTO_RULES_PATH.exists(),
    }

@app.post("/api/auto-rules")
async def save_auto_rules(rules: Dict):
    """Save auto-ingestion rules."""
    try:
        save_yaml(AUTO_RULES_PATH, rules)
        return {"success": True, "message": "Auto-rules saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auto-rules")
async def get_auto_rules():
    """Get auto-ingestion rules."""
    return load_auto_rules()

# ============================================================================
# STATIC FILES & ROOT
# ============================================================================

app.mount("/static", StaticFiles(directory=str(WEB_UI_DIR / "static")), name="static")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=7860,
        reload=True,
        log_level="info"
    )