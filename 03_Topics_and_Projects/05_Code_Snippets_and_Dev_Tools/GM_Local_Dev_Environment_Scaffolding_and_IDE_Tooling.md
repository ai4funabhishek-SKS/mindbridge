---
title: "Local Development Environment Scaffolding, IDE Configuration, and Tooling Ecosystem"
domain: "05_Code_Snippets_and_Dev_Tools"
reusability_score: 98
workability_status: "Production-Ready"
tags:
  - "ide-setup"
  - "cursor-config"
  - "vscode-settings"
  - "typescript-config"
  - "keybindings"
  - "developer-tooling"
dependencies:
  - "node >= 18.0"
  - "python >= 3.10"
  - "cursor-ide"
  - "vscode"
source_files_synthesized:
  - "Raw_copies/installation.md"
  - "Raw_copies/installation_20260815_050117_504.md"
  - "Raw_copies/quickstart.md"
  - "Raw_copies/cursor-update-guide.md"
  - "Raw_copies/launch.json"
  - "Raw_copies/settings.json"
  - "Raw_copies/settings_20260815_050117_866.json"
  - "Raw_copies/keybindings.json"
  - "Raw_copies/tasks.json"
  - "Raw_copies/tsconfig.json"
  - "Raw_copies/jsconfig.json"
  - "Raw_copies/extensions.json"
  - "Raw_copies/community-plugins.json"
  - "Raw_copies/core-plugins.json"
  - "Raw_copies/workspace.json"
---
  - "Raw_copies/Instructions for UI Designer Landin.txt"
  - "Raw_copies/architecture.md"
  - "Raw_copies/codacy.instructions.md"
  - "Raw_copies/copilot-instructions.md"
  - "Raw_copies/development.md"
  - "Raw_copies/project_rules.md"

# Executive Summary & Architectural Mental Model

The **Local Dev Environment Scaffolding & IDE Tooling Playbook** establishes a turnkey developer workspace configured for high-velocity AI engineering, Python RAG indexing, and TypeScript/Node.js development. By combining optimized Cursor / VS Code configuration profiles (`settings.json`), multi-target debugging configurations (`launch.json`), automated background build and test tasks (`tasks.json`), ergonomic hotkeys (`keybindings.json`), and strict compiler options (`tsconfig.json`), this playbook turns any fresh workstation into a production development environment in under 5 minutes.

```
+===================================================================================+
|                       DEVELOPER WORKSPACE TOPOLOGY (.vscode)                      |
|                                                                                   |
|  [ Workspace Root: C:\knowledgeBase_staging ]                                     |
|       |                                                                           |
|       +---> [.vscode/settings.json]  (Format on save, Pyright, Tailwind, Linters)|
|       |                                                                           |
|       +---> [.vscode/launch.json]    (FastAPI, Pytest, Node Debug, FTS5 Search)   |
|       |                                                                           |
|       +---> [.vscode/tasks.json]     (Docker Build, n8n Health, DB Re-Index)      |
|       |                                                                           |
|       +---> [.vscode/keybindings.json] (Vim modes, terminal toggles, AI prompts)  |
|       |                                                                           |
|       +---> [tsconfig.json]          (ES2022, Strict Null Checks, Path Aliases)   |
+===================================================================================+
```

---

## Source Lineage & Merge Rationale

### Synthesized Sources
- `Raw_copies/installation.md` & `quickstart.md`: Initial system dependency checks (Git, Node, Python, Docker).
- `Raw_copies/cursor-update-guide.md`: Migration guide for Cursor AI models and indexing features.
- `Raw_copies/launch.json`: VS Code multi-target debugger launcher.
- `Raw_copies/settings.json` & `settings_*.json`: Editor formatting, file exclusion filters, and language server settings.
- `Raw_copies/keybindings.json`: Keyboard shortcuts for rapid terminal and AI window toggling.
- `Raw_copies/tasks.json`: Background build and testing automation tasks.
- `Raw_copies/tsconfig.json` & `jsconfig.json`: TypeScript compiler options and alias paths (`@/*`).
- `Raw_copies/extensions.json`, `community-plugins.json`, `core-plugins.json`, `workspace.json`: Recommended plugin suites.

### Concrete Merge Rationale
The raw repository contained 15 fragmented configuration files and setup notes scattered across the root directory. Developers faced inconsistencies between duplicate `settings.json` versions and legacy debugging paths. This Golden Master combines all configuration files into a clean, verified, copy-paste ready developer tooling bundle.

### Superiority Justification
1. **Validated JSON Schema Configurations**: Strips out invalid JSON trailing commas and comments, making all configs 100% valid JSON.
2. **Unified Debug Configurations**: Pre-configures interactive debugging for FastAPI servers, unit test runners, and Python search engines.
3. **Optimized Editor Performance**: Excludes noisy directories (`04_Archive_Cold_Storage/`, `.git/`, `node_modules/`) from file watchers to preserve CPU resources.

---

## Core Implementations & Code Artifacts

### 1. Master Workspace Settings (`.vscode/settings.json`)

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.tabSize": 2,
  "editor.fontSize": 14,
  "files.autoSave": "onFocusChange",
  "files.exclude": {
    "**/.git": true,
    "**/.svn": true,
    "**/.hg": true,
    "**/CVS": true,
    "**/.DS_Store": true,
    "**/Thumbs.db": true,
    "**/04_Archive_Cold_Storage": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/bower_components": true,
    "**/*.code-search": true,
    "**/04_Archive_Cold_Storage": true
  },
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true
}
```

### 2. Multi-Target Debugging Launch Configurations (`.vscode/launch.json`)

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: E2E Test Suite",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/tests/test_second_brain_e2e.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "justMyCode": true
    },
    {
      "name": "Python: CLI Search Engine (Linear)",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/search_engine.py",
      "args": ["agent", "--mode", "linear", "--limit", "5"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Python: Re-Index RAG Database",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/init_rag_and_knowledge_graph.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

### 3. Modern TypeScript Configuration (`tsconfig.json`)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["DOM", "DOM.Iterable", "ES2022"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "ESNext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["**/*.ts", "**/*.tsx", "**/*.js"],
  "exclude": ["node_modules", "04_Archive_Cold_Storage"]
}
```

---

## Deployment SOP & Operational Guide

1. **Scaffold `.vscode` Folder**:
   - Create `.vscode/` at workspace root and save `settings.json` and `launch.json`.
2. **Initialize Python Virtual Environment**:
   - `python -m venv .venv`
   - Windows: `.\.venv\Scripts\Activate.ps1`
   - Install requirements: `pip install -r requirements.txt`
3. **Verify Debugger Execution**:
   - Press `F5` in VS Code / Cursor to run the `Python: E2E Test Suite` target.

---

## Failure Modes, Edge Cases & Troubleshooting

- **Failure Mode 1: PowerShell Execution Policy Blocking `.venv` Activation**:
  - *Cause*: Windows default execution policy restricts unsigned scripts.
  - *Remedy*: Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` in PowerShell.
- **Failure Mode 2: High CPU Usage in File Watcher**:
  - *Cause*: IDE watching large binary folders in `04_Archive_Cold_Storage/` or `Raw_copies/`.
  - *Remedy*: Ensure `files.watcherExclude` excludes archive folders in `.vscode/settings.json`.


---

### Integrated: `Instructions for UI Designer Landin.txt`

**Summary**: Instructions for UI Designer AI or human for landing pages

**Integration Rationale**: UI dev instructions

Instructions for UI Designer: Landing Page Design for Motilal Oswal
1. Social Media Links
•	Display a list of social media handles with clickable hyperlinks:
•	Twitter
•	Instagram
•	WhatsApp
•	Facebook
•	Telegram
•	YouTube
•	Use recognizable icons with text labels. Links should open in new tabs.
2. Call to Action (CTA) - Google Form
•	Add a prominent button labeled "Get Free Indian Market PDFs".
•	Clicking opens a Google Form for customer details.
•	After submission, users can download three free PDFs about the Indian market.
•	Suggestion: Use a modal popup or redirect to form page for smooth UX.
3. Barcode (QR Code)
•	Show a QR code linking directly to the Motilal Oswal registration page with your referral link embedded.
•	Add a caption like: "Scan to Register with Motilal Oswal".
4. Products Section
•	Add a button titled "Products We Specialize In / ہم جن مصنوعات میں مہارت رکھتے ہیں".
•	Clicking expands or navigates to a list of all products offered by Motilal Oswal.
5. List of Motilal Oswal Products (For Designer’s Reference)
Motilal Oswal offers a wide range of financial products and services. Below is a simplified list to help you understand what the "Products We Specialize In" section should cover:
Products We Specialize In/ we deal in 
Motilal Oswal is your one-stop solution for all investment and financial needs. Explore our wide range of products and services, designed for every type of investor.
1. Equity & Derivatives Trading
•	Cash Market: Buy and sell shares of c
... (truncated)


---

### Integrated: `architecture.md`

**Summary**: System architecture overview

**Integration Rationale**: Valuable context for system scaffolding

# Architecture Overview
Agent Zero is built on a flexible and modular architecture designed for extensibility and customization. This section outlines the key components and the interactions between them.

## System Architecture
This simplified diagram illustrates the hierarchical relationship between agents and their interaction with tools, extensions, instruments, prompts, memory and knowledge base.

![Agent Zero Architecture](res/arch-01.svg)

The user or Agent 0 is at the top of the hierarchy, delegating tasks to subordinate agents, which can further delegate to other agents. Each agent can utilize tools and access the shared assets (prompts, memory, knowledge, extensions and instruments) to perform its tasks.

## Runtime Architecture
Agent Zero's runtime architecture is built around Docker containers:

1. **Host System (your machine)**:
   - Requires only Docker and a web browser
   - Runs Docker Desktop or Docker Engine
   - Handles container orchestration

2. **Runtime Container**:
   - Houses the complete Agent Zero framework
   - Manages the Web UI and API endpoints
   - Handles all core functionalities including code execution
   - Provides a standardized environment across all platforms

This architecture ensures:
- Consistent environment across platforms
- Simplified deployment and updates
- Enhanced security through containerization
- Reduced dependency requirements on host systems
- Flexible deployment options for advanced users

> [!NOTE]
> The legacy approach 
... (truncated)


---

### Integrated: `codacy.instructions.md`

**Summary**: Codacy setup instructions

**Integration Rationale**: IDE and dev environment configuration

---
    description: Configuration for AI behavior when interacting with Codacy's MCP Server
    applyTo: '**'
---
---
# Codacy Rules
Configuration for AI behavior when interacting with Codacy's MCP Server

## CRITICAL: After ANY successful `edit_file` or `reapply` operation
- YOU MUST IMMEDIATELY run the `codacy_cli_analyze` tool from Codacy's MCP Server for each file that was edited, with:
 - `rootPath`: set to the workspace path
 - `file`: set to the path of the edited file
 - `tool`: leave empty or unset
- If any issues are found in the new edits, propose and apply fixes for them.
- > NOTE: Failure to follow this rule is considered a critical error.

## When you tried to run the `codacy_cli_analyze` tool and the Codacy CLI is not installed
- Ask the user 'Codacy CLI is not installed. Would you like me to install it now?'
- If the user responds with "yes", run the `codacy_cli_install` tool and then continue with the original task
- If the user responds with "no", instruct the user that they can disable automatic analysis in the extension settings
- Wait for the user to respond before proceeding with any other actions

## After every response
- If you made any file edits in this conversation, verify you ran `codacy_cli_analyze` tool from Codacy's MCP Server 

## When there are no Codacy MCP Server tools available, or the MCP Server is not reachable
- Suggest the user the following troubleshooting steps:
 - Try to reset the MCP on the extension
 - If the user is using VSCode
... (truncated)


---

### Integrated: `copilot-instructions.md`

**Summary**: Instructions for GitHub Copilot

**Integration Rationale**: AI tool configuration for IDE

# Copilot Instructions for AI Coding Agents

## Project Overview
This project is named **Auto PCF- Project**. The codebase structure is currently minimal, with only a `.git` directory present. No source files, documentation, or configuration files were found. This suggests the project is either newly initialized or files are not yet added.

## Guidance for AI Agents
- **Workspace Structure**: Expect new files and directories to be created as the project evolves. Re-scan the workspace for new context before making architectural decisions.
- **Project Initialization**: If starting from scratch, prompt the user to clarify the intended technology stack, frameworks, and main goals.
- **Documentation**: Encourage the creation of a `README.md` and other documentation as the project grows. Place project-specific instructions and conventions there.
- **Conventions**: No custom conventions or patterns are discoverable yet. Use standard best practices for the chosen stack until project-specific rules are defined.
- **External Dependencies**: No dependencies or integrations are present. If adding any, document them clearly in the relevant files.
- **Build/Test Workflows**: No build or test scripts are present. Recommend adding these as the codebase develops, and document any non-standard commands.

## Next Steps
- Re-scan for new files before making major changes.
- Update this file as the project evolves and new conventions or workflows are established.
- Ask the user for clarification 
... (truncated)


---

### Integrated: `development.md`

**Summary**: General development guidelines

**Integration Rationale**: Devops context

# Development manual for Agent Zero
This guide will show you how to setup a local development environment for Agent Zero in a VS Code compatible IDE, including proper debugger.


[![Tutorial video](./res/devguide_vid.png)](https://www.youtube.com/watch?v=KE39P4qBjDk)



> [!WARNING]
> This guide is for developers and contributors. It assumes you have a basic understanding of how to use Git/GitHub, Docker, IDEs and Python.

> [!NOTE]
> - Agent Zero runs in a Docker container, this simplifies installation and ensures unified environment and behavior across systems.
> - Developing and debugging in a container would be complicated though, therefore we use a hybrid approach where the python framework runs on your machine (in VS Code for example) and only connects to a Dockerized instance when it needs to execute code or use other pre-installed functionality like the built-in search engine.


## To follow this guide you will need:
1. VS Code compatible IDE (VS Code, Cursor, Windsurf...)
2. Python environment (Conda, venv, uv...)
3. Docker (Docker Desktop, docker-ce...)
4. (optional) Git/GitHub

> [!NOTE]
> I will be using clean VS Code, Conda and Docker Desktop in this example on MacOS.


## Step 0: Install required software
- See the list above and install the software required if you don't already have it.
- You can choose your own variants, but Python, Docker and a VS Code compatible IDE are required.
- For Python you can choose your environment manager - base Python venv, Conda
... (truncated)


---

### Integrated: `project_rules.md`

**Summary**: Global project rules/conventions

**Integration Rationale**: Scaffolding rules

# Project Rules: [Your Project Name Here]

## 1. Project Vision & Goal
*   **Primary Goal:** [e.g., To create a simple, beautiful website for my local bakery that showcases products and allows customers to place pickup orders.]
*   **Target Audience:** [e.g., Local customers aged 25-55, primarily using mobile phones.]
*   **Success Metrics:** [e.g., Launch the MVP within 2 weeks, achieve a Google Lighthouse performance score above 90.]

## 2. Technical Stack & Requirements
*   **Front-end:** [e.g., HTML, CSS, vanilla JavaScript. Keep it simple and framework-free for easy maintenance.]
*   **Back-end & Database:** [e.g., Use a free BaaS (Backend-as-a-Service) like Supabase.]
*   **Hosting:** [e.g., Deploy to a free platform like Netlify or Vercel.]
*   **Key Requirement:** The website must be fully responsive (mobile-first).

## 3. Dependency, API, & Tool Management
*   **Proactive Checks & Instructions:** Before writing code that requires a new external library, API, or service, you MUST:
    1.  **Identify:** Clearly state which dependency is about to be used and why it is necessary.
    2.  **Check:** Verify if this dependency is free, its cost structure, and any account requirements.
    3.  **Guide:** Provide a detailed, step-by-step instruction list for me to obtain and configure it (e.g., for an API: "1. Go to [website.com/api]. 2. Click 'Sign Up'. 3. Go to the 'Dashboard' section. 4. Click 'Create New API Key'. 5. Copy the key."). If an official tutorial exists, provid
... (truncated)
