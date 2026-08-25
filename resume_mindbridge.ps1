<#
.SYNOPSIS
    mindbridge Auto-Resume Script
    Shows project status and provides quick actions after restart

.DESCRIPTION
    Run this script after system restart or when starting a new session
    to quickly see project status and resume work.

.NOTES
    Author: mindbridge
    Version: 1.0
#>

param(
    [switch]$ShowHelp,
    [switch]$RunTests,
    [switch]$StartUI,
    [switch]$RunIngestion
)

# Colors
$colors = @{
    Cyan = [ConsoleColor]::Cyan
    Green = [ConsoleColor]::Green
    Yellow = [ConsoleColor]::Yellow
    Red = [ConsoleColor]::Red
    Gray = [ConsoleColor]::Gray
    White = [ConsoleColor]::White
}

function Write-Color($message, $color) {
    Write-Host $message -ForegroundColor $colors[$color]
}

function Write-Section($title) {
    Write-Host ""
    Write-Color "═══ $title ═══" "Cyan"
}

# Set location to project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

if ($ShowHelp) {
    Write-Color "mindbridge Auto-Resume Helper" "Cyan"
    Write-Host "Usage: .\resume_mindbridge.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -ShowHelp     Show this help"
    Write-Host "  -RunTests     Run full test suite after showing status"
    Write-Host "  -StartUI      Launch Web UI after showing status"
    Write-Host "  -RunIngestion Run weekly knowledge school ingestion"
    exit 0
}

Write-Color "╔════════════════════════════════════════════════════╗" "Cyan"
Write-Color "║           🧠 mindbridge Auto-Resume                  ║" "Cyan"
Write-Color "╚════════════════════════════════════════════════════╝" "Cyan"
Write-Host ""

# 1. Project State Summary
Write-Section "📋 Project State"
if (Test-Path "PROJECT_STATE.md") {
    $state = Get-Content "PROJECT_STATE.md" -Raw
    # Show first 50 lines
    $lines = $state -split "`n"
    $lines[0..([math]::Min(50, $lines.Count - 1))] | ForEach-Object { Write-Host $_ }
    if ($lines.Count -gt 50) { Write-Color "... (see PROJECT_STATE.md for full details)" "Gray" }
} else {
    Write-Color "⚠️ PROJECT_STATE.md not found" "Yellow"
}

# 2. Git Status
Write-Section "📦 Git Status"
$gitStatus = git status --short 2>$null
if ($LASTEXITCODE -eq 0) {
    if ($gitStatus) {
        Write-Color "Modified files:" "Yellow"
        $gitStatus | ForEach-Object { Write-Host "  $_" }
    } else {
        Write-Color "✅ Working tree clean" "Green"
    }
    
    $lastCommit = git log --oneline -1 2>$null
    if ($lastCommit) {
        Write-Host "Last commit: $lastCommit"
    }
} else {
    Write-Color "⚠️ Not a git repository" "Yellow"
}

# 3. Database Health
Write-Section "🗄️ Database Health"
if (Test-Path "Processed_Assets\my_rag_data.db") {
    try {
        $conn = [System.Data.SQLite.SQLiteConnection]::new("Data Source=Processed_Assets\my_rag_data.db;Read Only=True")
        $conn.Open()
        
        $tables = @("documents", "chunks", "chunks_fts", "chunk_embeddings", "doc_anchors", "kg_nodes", "kg_edges")
        foreach ($table in $tables) {
            $cmd = $conn.CreateCommand()
            $cmd.CommandText = "SELECT COUNT(*) FROM [$table]"
            $count = $cmd.ExecuteScalar()
            Write-Host "  $table : $count"
        }
        $conn.Close()
    } catch {
        Write-Color "  ⚠️ Database error: $_" "Red"
    }
} else {
    Write-Color "  ⚠️ Database not found" "Yellow"
}

# 4. Docker/Ollama Status
Write-Section "🐳 Docker / Ollama"
$dockerRunning = (Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue) -ne $null
if ($dockerRunning) {
    Write-Color "✅ Docker Desktop running" "Green"
    
    # Check Ollama
    try {
        $ollamaResponse = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -ErrorAction Stop
        if ($ollamaResponse.models) {
            Write-Color "✅ Ollama running with $($ollamaResponse.models.Count) models" "Green"
            $ollamaResponse.models | ForEach-Object { Write-Host "    - $($_.name)" }
        }
    } catch {
        Write-Color "⚠️ Ollama not responding" "Yellow"
    }
} else {
    Write-Color "⚠️ Docker Desktop not running" "Yellow"
}

# 5. Test Status
Write-Section "🧪 Test Suite"
try {
    $testResult = python -m pytest tests/ -q --tb=no 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Color "✅ All tests passing" "Green"
        # Extract pass count
        if ($testResult -match '(\d+) passed') {
            Write-Host "  $($matches[1]) tests passed"
        }
    } else {
        Write-Color "❌ Some tests failing" "Red"
        Write-Host $testResult
    }
} catch {
    Write-Color "⚠️ Could not run tests" "Yellow"
}

# 6. Quick Actions
Write-Section "⚡ Quick Actions"
Write-Host "  1. Run tests:        python -m pytest tests/ -q"
Write-Host "  2. Search (ask):     python search_engine.py 'your question' --mode ask"
Write-Host "  3. Search (hybrid):  python search_engine.py 'query' --mode hybrid"
Write-Host "  4. Launch Web UI:    .\launch_ui.ps1"
Write-Host "  5. Run ingestion:    python weekly_school.py"
Write-Host "  6. Start scheduler:  .\setup_scheduler.ps1"
Write-Host "  7. Push to GitHub:   git push"
Write-Host ""

# Execute requested actions
if ($RunTests) {
    Write-Section "🧪 Running Full Test Suite"
    python -m pytest tests/ -v --tb=short
}

if ($StartUI) {
    Write-Section "🚀 Launching Web UI"
    & ".\launch_ui.ps1"
}

if ($RunIngestion) {
    Write-Section "🏫 Running Knowledge School Ingestion"
    python weekly_school.py
}

Write-Color "═══ Ready to continue! ═══" "Green"