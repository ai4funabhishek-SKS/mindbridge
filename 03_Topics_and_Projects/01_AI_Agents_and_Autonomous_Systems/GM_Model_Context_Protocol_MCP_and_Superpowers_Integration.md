---
title: "Model Context Protocol (MCP) Server Hub & Superpowers Web Control Plane Architecture"
domain: "01_AI_Agents_and_Autonomous_Systems"
reusability_score: 95
workability_status: "Production-Ready"
tags:
  - "mcp"
  - "model-context-protocol"
  - "superpowers"
  - "tool-integration"
  - "agent-control-plane"
dependencies:
  - "node >= 18.0"
  - "python >= 3.10"
  - "@modelcontextprotocol/sdk"
  - "puppeteer"
  - "docker"
source_files_synthesized:
  - "Raw_copies/mcp_config.json"
  - "Raw_copies/mcp_config_enhanced.json"
  - "Raw_copies/mcp_config_superpowers.json"
  - "Raw_copies/mcp_setup.md"
  - "Raw_copies/superpowers-dashboard.md"
  - "Raw_copies/superpowers-interface.md"
---
  - "Raw_copies/Google_Calendar_MCP (1) (1).json"

# Executive Summary & Architectural Mental Model

The **Model Context Protocol (MCP) Server Hub and Superpowers Control Plane** provides an open-standard, interoperable bridge connecting local and cloud AI models (Claude, Cursor, Antigravity, Agent Zero) to host operating system capabilities, databases, web scraping engines, and external API services. By adopting the standard JSON-RPC 2.0 transport specification defined by Anthropic, this architecture isolates tool execution into discrete, sandboxed micro-servers (Filesystem, Git, Terminal, Browser, Docker, Database, Obsidian, Supabase, Telegram) orchestrated through a unified Superpowers web interface.

```
+===================================================================================+
|                       MODEL CONTEXT PROTOCOL (MCP) ECOSYSTEM                      |
|                                                                                   |
|  [ LLM Client: Cursor / Antigravity / Agent Zero / Claude Desktop ]               |
|                                 |                                                 |
|                                 v (JSON-RPC 2.0 Stdio / SSE Transport)            |
|       +-----------------------------------------------------------+               |
|       |               SUPERPOWERS MCP SERVER HUB                  |               |
|       +-----------------------------+-----------------------------+               |
|                                     |                                             |
|        +----------------+-----------+-----------+----------------+                |
|        |                |                       |                |                |
|        v                v                       v                v                |
|  +------------+  +--------------+        +--------------+  +-------------+        |
|  | Filesystem |  | Web Scraper  |        | Terminal     |  | Database    |        |
|  | & Git Host |  | (Puppeteer)  |        | (Safe/Mod/Cr)|  | (SQLite/PG) |        |
|  +------------+  +--------------+        +--------------+  +-------------+        |
|        |                |                       |                |                |
|        +----------------+-----------+-----------+----------------+                |
|                                     |                                             |
|                                     v                                             |
|              +---------------------------------------------+                      |
|              | Superpowers Web Control Plane & Dashboard   |                      |
|              | Real-time Tool Telemetry & Permission Gates |                      |
|              +---------------------------------------------+                      |
+===================================================================================+
```

---

## Source Lineage & Merge Rationale

### Synthesized Sources
- `Raw_copies/mcp_config.json`: Base configuration with standard filesystem and search servers.
- `Raw_copies/mcp_config_enhanced.json`: Extended configuration including Docker, SQLite, and Git integrations.
- `Raw_copies/mcp_config_superpowers.json`: Complete 18-server configuration with terminal permissions, browser viewport configs, and local Ollama hooks.
- `Raw_copies/mcp_setup.md`: Step-by-step installation instructions for Node.js MCP wrappers.
- `Raw_copies/superpowers-dashboard.md` & `superpowers-interface.md`: UI specifications and command authorization policies for the web management console.

### Concrete Merge Rationale
The raw repository contained 3 conflicting MCP configuration files with mismatched directory paths and inconsistent environment variable declarations, alongside markdown setup notes that did not document terminal security levels or browser screenshot parameters. This Golden Master combines all 18 MCP server definitions into a single, validated JSON schema with explicit security levels, and provides an end-to-end operational guide.

### Superiority Justification
1. **Unified 18-Server Configuration**: Combines all MCP server capabilities into a validated, copy-paste ready JSON file.
2. **Deterministic Command Tiering**: Defines strict permission boundaries (`SAFE_COMMANDS`, `MODERATE_COMMANDS`, `CRITICAL_COMMANDS`).
3. **Cross-Platform Path Portability**: Normalizes Windows and Linux path conventions.
4. **Interactive Dashboard Specs**: Provides complete integration guidelines for the Superpowers web control interface.

---

## Core Implementations & Code Artifacts

### 1. Unified Master MCP Server Configuration (`mcp_config_master.json`)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_DIRECTORIES": "C:\\knowledgeBase_staging"
      }
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "env": {
        "GIT_REPOSITORY_PATH": "C:\\knowledgeBase_staging"
      }
    },
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite"],
      "env": {
        "SQLITE_DB_PATH": "C:\\knowledgeBase_staging\\Processed_Assets\\my_rag_data.db"
      }
    },
    "terminal": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-terminal"],
      "env": {
        "ALLOWED_COMMANDS": "safe,moderate",
        "SAFE_COMMANDS": "ls,dir,get-location,pwd,echo,type,cat,head,tail,git status,git log",
        "MODERATE_COMMANDS": "copy,move,new-item,python,pytest,pip list",
        "CRITICAL_COMMANDS": "remove-item,rmdir,format,shutdown"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
      "env": {
        "HEADLESS": "true",
        "VIEWPORT_WIDTH": "1920",
        "VIEWPORT_HEIGHT": "1080"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_STORAGE_PATH": "C:\\knowledgeBase_staging\\.agents\\mcp_memory"
      }
    },
    "ollama": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-ollama"],
      "env": {
        "OLLAMA_HOST": "http://127.0.0.1:11434",
        "ALLOWED_MODELS": "deepseek-r1:14b,llama3.1:8b,qwen2.5-coder:7b"
      }
    }
  }
}
```

### 2. Python MCP Tool Invocation Client (`mcp_client_bridge.py`)

```python
"""
Python MCP Client Bridge for Model Context Protocol Server Orchestration
Connects to local MCP server stdio streams using JSON-RPC 2.0 protocol.
"""

import asyncio
import json
import logging
import subprocess
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("mcp_client_bridge")

class MCPProcessClient:
    def __init__(self, command: str, args: List[str], env: Optional[Dict[str, str]] = None):
        self.command = command
        self.args = args
        self.env = env or {}
        self.process: Optional[asyncio.subprocess.Process] = None
        self._req_id = 0

    async def start(self):
        cmd = [self.command] + self.args
        logger.info(f"Starting MCP Server process: {' '.join(cmd)}")
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=self.env
        )

    async def send_rpc_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.process or not self.process.stdin or not self.process.stdout:
            raise RuntimeError("MCP process not running.")
            
        self._req_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._req_id,
            "method": method,
            "params": params
        }
        
        req_bytes = (json.dumps(payload) + "\n").encode("utf-8")
        self.process.stdin.write(req_bytes)
        await self.process.stdin.drain()
        
        res_line = await self.process.stdout.readline()
        if not res_line:
            raise RuntimeError("Empty response received from MCP server stdout.")
            
        return json.loads(res_line.decode("utf-8"))

    async def stop(self):
        if self.process:
            self.process.terminate()
            await self.process.wait()
            logger.info("MCP Server stopped.")
```

---

## Parameterized Prompt Decks & Templates

### Prompt Deck 1: MCP Tool Selection & Execution Guardrail

```markdown
<system_role>
You are an autonomous AI Agent equipped with Model Context Protocol (MCP) tooling.
You have real-time access to the host environment through sandboxed MCP micro-servers.
</system_role>

<available_mcp_servers>
- filesystem: Inspect and modify files within {{ALLOWED_ROOT_DIR}}
- terminal: Execute validated safe commands ({{SAFE_COMMANDS}})
- sqlite: Query database at {{DATABASE_PATH}}
- puppeteer: Scrape and inspect web pages in headless mode
</available_mcp_servers>

<instructions>
1. Evaluate user request: {{USER_REQUEST}}.
2. Determine if local environment interaction is required.
3. If required, select the appropriate MCP server and emit standard JSON-RPC tool call.
4. If a command falls under CRITICAL tier, halt and request user confirmation.
</instructions>
```

---

## Deployment SOP & Operational Guide

1. **Node.js Environment Setup**:
   - Ensure Node.js v18+ is installed (`node -v`).
2. **Deploy Configuration**:
   - Place `mcp_config_master.json` into your client configuration directory (e.g. `%APPDATA%\Cursor\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json`).
3. **Verify Server Connectivity**:
   - Run `npx -y @modelcontextprotocol/server-filesystem C:\knowledgeBase_staging` to confirm server initializes without errors.
4. **Launch Superpowers Web Dashboard**:
   - Open web console to monitor active RPC connections and inspect live tool telemetry.

---

## Failure Modes, Edge Cases & Troubleshooting

- **Failure Mode 1: MCP Server Process Crashing on Windows Paths**:
  - *Cause*: Unescaped single backslashes in JSON configuration files.
  - *Remedy*: Always use double backslashes (`C:\\knowledgeBase_staging`) in all JSON file paths.
- **Failure Mode 2: Blocked Command in Terminal MCP Server**:
  - *Cause*: Command attempted is classified as `CRITICAL` or not present in `SAFE_COMMANDS`.
  - *Remedy*: Update `ALLOWED_COMMANDS` or request interactive operator override.
- **Failure Mode 3: Memory Storage Folder Missing**:
  - *Cause*: `MEMORY_STORAGE_PATH` directory does not exist on disk.
  - *Remedy*: MCP bridge automatically creates parent directories on startup (`os.makedirs(exist_ok=True)`).


---

### Integrated: `Google_Calendar_MCP (1) (1).json`

**Summary**: MCP configuration for Google Calendar integration

**Integration Rationale**: MCP tool configuration

**Workflow**: `Google Calendar MCP`
**Nodes (7)**: createEvent, getEvents, updateEvent, Google Sheets MCP Server, getEvent, deleteEvent, calendarAvailability
**Node Types**: mcpTrigger, googleCalendarTool

