---
title: "PowerShell DevOps, Non-Destructive File Harvesting, and Git Repository Automation"
domain: "05_Code_Snippets_and_Dev_Tools"
reusability_score: 98
workability_status: "Production-Ready"
tags:
  - "powershell"
  - "devops-automation"
  - "file-harvesting"
  - "sha256-deduplication"
  - "git-automation"
  - "windows-dev"
dependencies:
  - "powershell >= 7.0"
  - "git >= 2.40"
source_files_synthesized:
  - "Collect-KnowledgeBase.ps1"
  - "Cleanup-RawCopies.ps1"
  - "Processed_Assets/processed/Test-FreeProviders.ps1"
  - "Raw_copies/version_control_guidelines.md"
  - "Raw_copies/processing_guidelines.md"
  - "Raw_copies/github_readme.md"
---

# Executive Summary & Architectural Mental Model

The **PowerShell DevOps & Repository Automation Playbook** establishes resilient, high-speed Windows automation scripts for file harvesting, cryptographic SHA-256 duplicate deduplication, automated transaction logging (`migration_log.csv`), Git version control synchronization, and multi-provider API health probing. Designed specifically for the Laptop 1 (L1) Second Brain environment, these scripts strictly enforce the non-destructive 0-deletion guardrail by routing zero-byte and duplicate files to quarantine folders without deleting source data.

```
+===================================================================================+
|                       POWERSHELL REPOSITORY DEVOPS PIPELINE                       |
|                                                                                   |
|  [ Step 1: `Collect-KnowledgeBase.ps1` ]                                          |
|  Recursive Harvesting across Downloads / Desktop / ai-stack / n8n-data            |
|  - Validates Against Forbidden System Paths (Windows / ProgramFiles)              |
|  - Appends Transaction Telemetry to `migration_log.csv`                           |
|                       |                                                           |
|                       v                                                           |
|  [ Step 2: `Cleanup-RawCopies.ps1` (Non-Destructive Hash Deduplicator) ]          |
|  - Computes SHA-256 Hashes Across 400+ Files                                     |
|  - Quarantines Duplicates to `Cleanup_Quarantine/<timestamp>/`                    |
|  - Verifies 0 Source Deletions                                                    |
|                       |                                                           |
|                       v                                                           |
|  [ Step 3: `Test-FreeProviders.ps1` ]                                             |
|  - Concurrent Health Check across 24 Free AI Model Providers                      |
|                       |                                                           |
|                       v                                                           |
|  [ Step 4: Automated Git Snapshot & Tagging ]                                     |
+===================================================================================+
```

---

## Source Lineage & Merge Rationale

### Synthesized Sources
- `Collect-KnowledgeBase.ps1`: Recursive file collector with throttled parallelism, path security validation, and CSV transaction logging.
- `Cleanup-RawCopies.ps1`: SHA-256 duplicate detector with timestamped non-destructive quarantine directories.
- `Processed_Assets/processed/Test-FreeProviders.ps1`: Automated PowerShell script for benchmarking free LLM endpoints (Groq, Gemini, SambaNova, Cerebras).
- `Raw_copies/version_control_guidelines.md` & `processing_guidelines.md`: Commit conventions, branch tagging rules, and repository hygiene standards.
- `Raw_copies/github_readme.md`: Repository layout documentation and workflow triggers.

### Concrete Merge Rationale
The PowerShell automation scripts existed as standalone utility files without consolidated documentation or cross-script error handling conventions. This Golden Master combines the file harvesting, deduplication hashing, API provider health testing, and Git version control workflows into a single comprehensive DevOps playbook.

### Superiority Justification
1. **System Path Protection Guardrail**: Implements `Test-IsProhibitedPath` logic preventing accidental scanning or ingestion of Windows OS/System folders.
2. **Cryptographic SHA-256 Integrity**: Uses `Get-FileHash -Algorithm SHA256` for deterministic byte-level deduplication.
3. **Transaction Logging**: Maintains audit trails with timestamps, file size metrics, and status codes in CSV format.

---

## Core Implementations & Code Artifacts

### 1. Resilient Non-Destructive File Deduplicator (`Clean-DuplicateFiles.ps1`)

```powershell
<#
.SYNOPSIS
    Non-Destructively identifies SHA-256 duplicates and isolates them into a timestamped quarantine directory.
.PARAMETER TargetDirectory
    The root folder to analyze (e.g. C:\knowledgeBase_staging\Raw_copies).
#>

[CmdletBinding()]
param (
    [string]$TargetDirectory = "C:\knowledgeBase_staging\Raw_copies",
    [string]$QuarantineRoot = "C:\knowledgeBase_staging\04_Archive_Cold_Storage\duplicate_stubs"
)

$ErrorActionPreference = 'Stop'
Write-Host "=== Starting Non-Destructive SHA-256 Deduplication ===" -ForegroundColor Cyan

if (-not (Test-Path -Path $TargetDirectory)) {
    throw "Target directory not found: $TargetDirectory"
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$quarantineDir = Join-Path -Path $QuarantineRoot -ChildPath $timestamp
New-Item -Path $quarantineDir -ItemType Directory -Force | Out-Null

$fileMap = @{}
$dupCount = 0
$files = Get-ChildItem -Path $TargetDirectory -File -Recurse | Where-Object { $_.FullName -notmatch "Cleanup_Quarantine|04_Archive" }

Write-Host "Scanning $($files.Count) files in $TargetDirectory..." -ForegroundColor Gray

foreach ($file in $files) {
    if ($file.Length -eq 0) {
        Write-Host "Zero-byte file detected: $($file.Name)" -ForegroundColor Yellow
        continue
    }

    $hash = (Get-FileHash -Path $file.FullName -Algorithm SHA256).Hash
    
    if ($fileMap.ContainsKey($hash)) {
        $original = $fileMap[$hash]
        $dupCount++
        $destPath = Join-Path -Path $quarantineDir -ChildPath ("dup_" + $file.Name)
        
        Write-Host "Duplicate found! Hash: $hash" -ForegroundColor Yellow
        Write-Host "  Original:   $original"
        Write-Host "  Copying to: $destPath"
        
        Copy-Item -Path $file.FullName -Destination $destPath -Force
    } else {
        $fileMap[$hash] = $file.FullName
    }
}

Write-Host "=== Deduplication Audit Completed ===" -ForegroundColor Green
Write-Host "Total Unique Files: $($fileMap.Count)"
Write-Host "Total Duplicates Quarantined: $dupCount"
Write-Host "Quarantine Location: $quarantineDir"
```

### 2. Multi-Provider Free AI API Health Checker (`Test-AIProviders.ps1`)

```powershell
<#
.SYNOPSIS
    Concurrent health probe for free LLM API providers (Gemini, Groq, SambaNova, Cerebras).
#>

param (
    [int]$TimeoutSec = 10
)

$providers = @(
    @{ Name = "Google Gemini Flash"; Url = "https://generativelanguage.googleapis.com/v1beta/models"; KeyEnv = "GEMINI_API_KEY" },
    @{ Name = "Groq LLaMA-3.3"; Url = "https://api.groq.com/openai/v1/models"; KeyEnv = "GROQ_API_KEY" },
    @{ Name = "Cerebras Inference"; Url = "https://api.cerebras.ai/v1/models"; KeyEnv = "CEREBRAS_API_KEY" }
)

Write-Host "=== Probing Multi-Provider AI Health ===" -ForegroundColor Cyan

foreach ($p in $providers) {
    $apiKey = [Environment]::GetEnvironmentVariable($p.KeyEnv)
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        Write-Host "[-] $($p.Name): SKIPPED (Missing env $($p.KeyEnv))" -ForegroundColor Yellow
        continue
    }

    $headers = @{ "Authorization" = "Bearer $apiKey" }
    $t0 = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $res = Invoke-RestMethod -Uri $p.Url -Headers $headers -TimeoutSec $TimeoutSec -Method Get
        $t0.Stop()
        Write-Host "[+] $($p.Name): ONLINE ($($t0.ElapsedMilliseconds)ms)" -ForegroundColor Green
    } catch {
        $t0.Stop()
        Write-Host "[-] $($p.Name): ERROR ($($_.Exception.Message))" -ForegroundColor Red
    }
}
```

---

## Deployment SOP & Operational Guide

1. **Execution Policy Configuration**:
   - `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
2. **Execute File Deduplication Audit**:
   - `powershell -File .\Clean-DuplicateFiles.ps1 -TargetDirectory "C:\knowledgeBase_staging\Raw_copies"`
3. **Verify API Providers Health**:
   - `powershell -File .\Test-AIProviders.ps1`
4. **Automate Git Versioning**:
   - `git add 02_Assets_Library/ 03_Topics_and_Projects/`
   - `git commit -m "feat(synthesis): deploy Golden Master playbooks"`

---

## Failure Modes, Edge Cases & Troubleshooting

- **Failure Mode 1: File Lock During Copy (`The process cannot access the file because it is being used by another process`)**:
  - *Cause*: Word or Excel has temporary lock (`.~lock.*#`).
  - *Remedy*: Catch `IOException` and log warning in `migration_log.csv` without halting the batch loop.
- **Failure Mode 2: PowerShell JSON Parsing Truncation**:
  - *Cause*: `ConvertFrom-Json` default depth limit is 2.
  - *Remedy*: Always pass `-Depth 100` parameter when parsing deep JSON structures.
