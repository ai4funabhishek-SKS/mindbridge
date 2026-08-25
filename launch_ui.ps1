<#
.SYNOPSIS
    Launches mindbridge Web UI Wizard
    
.DESCRIPTION
    Starts the FastAPI web server and opens the browser to the wizard.
    Handles virtual environment, dependencies, and graceful shutdown.
    
.NOTES
    Run from project root directory
#>

param(
    [switch]$NoBrowser,
    [switch]$NoInstall,
    [int]$Port = 7860,
    [string]$Host = "127.0.0.1",
    [string]$ConfigPath = "mindbridge_config.yaml"
)

# Colors
$colors = @{
    Cyan = [ConsoleColor]::Cyan
    Green = [ConsoleColor]::Green
    Yellow = [ConsoleColor]::Yellow
    Red = [ConsoleColor]::Red
    Gray = [ConsoleColor]::Gray
}

function Write-Color($message, $color) {
    Write-Host $message -ForegroundColor $colors[$color]
}

function Write-Section($title) {
    Write-Host ""
    Write-Host ("═" * 60) -ForegroundColor Cyan
    Write-Host "  $title" -ForegroundColor Cyan
    Write-Host ("═" * 60) -ForegroundColor Cyan
}

# Set location to project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

Write-Section "🧠 mindbridge Web UI Launcher"

# Check Python
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    Write-Error "Python not found in PATH. Please install Python 3.10+"
    exit 1
}
Write-Host "Python: $pythonPath" -ForegroundColor Gray

# Check if web_ui directory exists
$webUiDir = Join-Path $scriptDir "web_ui"
if (-not (Test-Path $webUiDir)) {
    Write-Color "⚠️ Web UI not found at $webUiDir" "Yellow"
    Write-Host "Run the setup script first to create Web UI files." -ForegroundColor Yellow
    exit 1
}

# Check virtual environment
$venvPath = Join-Path $scriptDir ".venv"
$useVenv = Test-Path $venvPath

if (-not $NoInstall -and -not $useVenv) {
    Write-Section "📦 Creating Virtual Environment"
    Write-Host "Creating virtual environment at $venvPath..." -ForegroundColor Cyan
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment"
        exit 1
    }
    Write-Color "✅ Virtual environment created" "Green"
    $useVenv = $true
}

# Determine python executable
if ($useVenv) {
    if ($IsWindows) {
        $venvPython = Join-Path $venvPath "Scripts\python.exe"
    } else {
        $venvPython = Join-Path $venvPath "bin/python"
    }
    if (Test-Path $venvPython) {
        $pythonExe = $venvPython
    } else {
        Write-Warning "Virtual environment python not found, using system python"
        $pythonExe = "python"
    }
} else {
    $pythonExe = "python"
}

Write-Host "Using Python: $pythonExe" -ForegroundColor Gray

# Install/upgrade dependencies
if (-not $NoInstall) {
    Write-Section "📦 Installing Dependencies"
    $requirements = @(
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.23.0",
        "pyyaml>=6.0",
        "pydantic>=2.0",
        "pydantic-settings>=2.0",
        "python-multipart>=0.0.6",
        "jinja2>=3.1.0",
        "watchdog>=3.0.0",
        "pyyaml>=6.0"
    )
    
    foreach ($req in $requirements) {
        Write-Host "Installing $req..." -ForegroundColor Gray
        & $pythonExe -m pip install --quiet $req
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to install $req"
        }
    }
    Write-Color "✅ Dependencies installed" "Green"
}

# Check config file
$configPath = Join-Path $scriptDir $ConfigPath
if (-not (Test-Path $configPath)) {
    Write-Warning "Config file not found: $ConfigPath"
    Write-Host "Creating default config from template..." -ForegroundColor Yellow
    Copy-Item "mindbridge_config.yaml" $configPath -Force
}

# Check web UI files
$webUiMain = Join-Path $webUiDir "main.py"
if (-not (Test-Path $webUiMain)) {
    Write-Error "Web UI main.py not found at $webUiMain"
    exit 1
}

# Start the server
Write-Section "🚀 Starting mindbridge Web UI"
Write-Host "Host: 127.0.0.1" -ForegroundColor Gray
Write-Host "Port: 7860" -ForegroundColor Gray
Write-Host "Config: $ConfigPath" -ForegroundColor Gray
Write-Host ""

# Set environment variables
$env:MINDBRIDGE_CONFIG = (Resolve-Path $ConfigPath).Path
$env:PYTHONPATH = (Resolve-Path ".").Path + ";" + $env:PYTHONPATH

# Open browser
if (-not $NoBrowser) {
    $url = "http://127.0.0.1:7860"
    Write-Host "Opening browser to $url..." -ForegroundColor Cyan
    Start-Process "http://127.0.0.1:7860"
}

Write-Section "🚀 Starting Server"
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
try {
    & python -m uvicorn web_ui.main:app --host 127.0.0.1 --port 7860 --reload
} catch {
    Write-Error "Server error: $_"
    exit 1
} finally {
    Write-Host ""
    Write-Color "👋 Server stopped" "Yellow"
}