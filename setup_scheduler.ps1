<#
.SYNOPSIS
    Sets up Windows Task Scheduler for mindbridge Knowledge School
    
.DESCRIPTION
    Creates a scheduled task to run the Knowledge School weekly on Sunday at 2 AM
    Includes proper error handling, logging, and notifications.
    
.NOTES
    Requires Administrator privileges
    Run as Administrator for best results
#>

param(
    [switch]$Force,
    [switch]$Remove,
    [switch]$TestRun,
    [string]$ScheduleTime = "02:00",
    [string]$DayOfWeek = "Sunday",
    [string]$EmailRecipient = "Aiadoptionconsultant@gmail.com"
)

# Require admin
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script requires Administrator privileges. Please run PowerShell as Administrator."
    exit 1
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$scriptPath = Join-Path $scriptDir "weekly_school.py"
$pythonPath = (Get-Command python).Source
$logPath = Join-Path $scriptDir "logs\knowledge_school.log"

if ($Remove) {
    Write-Host "Removing Knowledge School scheduled task..." -ForegroundColor Yellow
    try {
        Unregister-ScheduledTask -TaskName "KnowledgeSchool" -Confirm:$false -ErrorAction Stop
        Write-Host "✅ Task removed successfully" -ForegroundColor Green
    } catch {
        Write-Error "Failed to remove task: $_"
    }
    exit 0
}

# Validate script exists
if (-not (Test-Path $scriptPath)) {
    Write-Error "weekly_school.py not found at $scriptPath"
    exit 1
}

if (-not (Test-Path $pythonPath)) {
    Write-Error "Python not found in PATH"
    exit 1
}

# Create logs directory
$logDir = Join-Path (Split-Path $scriptDir) "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Create scheduled task
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $DayOfWeek -At $ScheduleTime
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopIfGoingOnBatteries `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -RunOnlyIfNetworkAvailable `
    -AllowStartOnDemand

$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

$taskName = "KnowledgeSchool"
$description = "mindbridge Knowledge School - Weekly automated ingestion (Monitor → Classify → Enrich → Index → Verify → Report)"

if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    if (-not $Force) {
        Write-Warning "Task '$taskName' already exists. Use -Force to overwrite."
        exit 1
    }
    Write-Host "Updating existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description $description `
    -Force

Write-Host "✅ Scheduled task '$taskName' created successfully" -ForegroundColor Green
Write-Host ""
Write-Host "Schedule: Every $DayOfWeek at $ScheduleTime"
Write-Host "Script: $scriptPath"
Write-Host "Python: $pythonPath"
Write-Host "Log: $logPath"
Write-Host ""

if ($TestRun) {
    Write-Host "Running test execution..." -ForegroundColor Cyan
    & python $scriptPath --test
}

# Show next run time
$task = Get-ScheduledTask -TaskName $taskName
$nextRun = $task | Get-ScheduledTaskInfo | Select-Object NextRunTime
Write-Host ""
Write-Host "Next run: $($nextRun.NextRunTime)" -ForegroundColor Green

# Enable task history
Write-Host ""
Write-Host "Enabling task history..." -ForegroundColor Cyan
wevtutil sl Microsoft-Windows-TaskScheduler/Operational /e:true /q:false /l:100 /rt:false /ms:10485760 2>$null | Out-Null
Write-Host "✅ Task history enabled" -ForegroundColor Green

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Management Commands:"
Write-Host "  View task:     Get-ScheduledTask -TaskName KnowledgeSchool"
Write-Host "  Run now:       Start-ScheduledTask -TaskName KnowledgeSchool"
Write-Host "  View history:  Get-WinEvent -LogName 'Microsoft-Windows-TaskScheduler/Operational' | Where-Object `{` `$_.Id -eq 201 -and `$_.Message -like '*KnowledgeSchool*' `}`"
Write-Host "  Disable:       Disable-ScheduledTask -TaskName KnowledgeSchool"
Write-Host "  Enable:        Enable-ScheduledTask -TaskName KnowledgeSchool"
Write-Host "  Remove:        .\setup_scheduler.ps1 -Remove"
Write-Host ""
Write-Host "Email notifications will be sent to: Aiadoptionconsultant@gmail.com" -ForegroundColor Cyan
Write-Host "Make sure EMAIL_USERNAME and EMAIL_APP_PASSWORD environment variables are set" -ForegroundColor Yellow