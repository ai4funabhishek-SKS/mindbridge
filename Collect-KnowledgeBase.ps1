[CmdletBinding()]
param (
    [string]$StagingBase = 'C:\KnowledgeBase_Staging',
    [string]$DestinationRoot = 'C:\KnowledgeBase_Staging\Raw_copies',
    [string]$CsvLogPath = 'C:\KnowledgeBase_Staging\migration_log.csv',
    # Expanded extension list
    [string[]]$FileExtensions = @('.txt', '.doc', '.docx', '.pdf', '.md', '.json', '.xls', '.xlsx'),
    [int]$MaxThrottle = 4
)

$ErrorActionPreference = 'Stop'

function Test-IsProhibitedPath {
    param ([string]$Path)
    try { $normalized = [System.IO.Path]::GetFullPath($Path) } catch { return $true }
    $prohibitedRoots = @(
        $env:ProgramFiles, "${env:ProgramFiles(x86)}", $env:Windir,
        'C:\Program Files', 'C:\Program Files (x86)', 'C:\Windows'
    ) | Where-Object { [string]::IsNullOrWhiteSpace($_) -eq $false } | ForEach-Object {
        try { [System.IO.Path]::GetFullPath($_) } catch { $_ }
    }
    foreach ($forbidden in $prohibitedRoots) {
        if ($normalized.StartsWith($forbidden, [System.StringComparison]::OrdinalIgnoreCase)) { return $true }
    }
    return $false
}

$AllowedSources = @(
    "$env:USERPROFILE\Downloads",
    "$env:USERPROFILE\Desktop",
    "C:\ai-stack",
    "C:\n8n-data"
)

foreach ($dir in @($StagingBase, $DestinationRoot)) {
    if (-not (Test-Path -Path $dir -PathType Container)) {
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
    }
}

$csvSyncLock = New-Object System.Object

function Initialize-CsvLog {
    if (-not (Test-Path -Path $CsvLogPath -PathType Leaf)) {
        "SourcePath,DestinationPath,Status,Timestamp,ErrorMessage" | Out-File -FilePath $CsvLogPath -Encoding utf8 -Force
    }
}

function Get-ProcessedFiles {
    if (-not (Test-Path -Path $CsvLogPath -PathType Leaf)) { return @{} }
    $completed = @{}
    try {
        $records = Import-Csv -Path $CsvLogPath -ErrorAction SilentlyContinue
        foreach ($r in $records) {
            if ($r.Status -eq 'SUCCESS' -and $r.SourcePath) { $completed[$r.SourcePath] = $true }
        }
    } catch {
        Write-Warning "Could not read transaction log. Re-evaluating files."
    }
    return $completed
}

function Write-TransactionLog {
    param ([string]$Source, [string]$Destination, [string]$Status, [string]$ErrorReason = '')
    [System.Threading.Monitor]::Enter($csvSyncLock)
    try {
        $timestamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
        $cleanSource = $Source.Replace('"', '""')
        $cleanDest = $Destination.Replace('"', '""')
        $cleanError = $ErrorReason.Replace('"', '""')
        $line = """$cleanSource"",""$cleanDest"",""$Status"",""$timestamp"",""$cleanError"""
        Add-Content -Path $CsvLogPath -Value $line -Encoding utf8
    } finally {
        [System.Threading.Monitor]::Exit($csvSyncLock)
    }
}

Initialize-CsvLog
$ProcessedMap = Get-ProcessedFiles
$TargetFiles = [System.Collections.Generic.List[System.IO.FileInfo]]::new()
$SkippedAlreadyDone = 0

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host " PHASE 1 EXTENDED: SCANNING NEW FILE TYPES" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

foreach ($src in $AllowedSources) {
    if (Test-IsProhibitedPath -Path $src) { continue }
    if (-not (Test-Path -Path $src -PathType Container)) { continue }
    Write-Host " Scanning: ${src}..." -ForegroundColor Gray
    try {
        $files = Get-ChildItem -Path $src -Recurse -File -ErrorAction Stop | 
            Where-Object { $FileExtensions -contains $_.Extension.ToLower() }
        foreach ($f in $files) {
            if ($ProcessedMap.ContainsKey($f.FullName)) {
                $SkippedAlreadyDone++
            } else {
                $TargetFiles.Add($f)
            }
        }
    } catch {
        Write-Host " [ERROR] Access denied scanning ${src}: $_" -ForegroundColor Red
    }
}

if ($TargetFiles.Count -eq 0) {
    Write-Host "No new files found. Phase 1 is fully complete!" -ForegroundColor Green
    exit 0
}

Write-Host " Found $($TargetFiles.Count) new files to collect." -ForegroundColor Cyan

$SuccessCount = 0
$Counter = 0
$TotalToProcess = $TargetFiles.Count

foreach ($file in $TargetFiles) {
    $Counter++
    $percent = [math]::Round(($Counter / $TotalToProcess) * 100)
    Write-Progress -Activity "Collecting Knowledge Base Files" -Status "Processing $Counter of $TotalToProcess" -PercentComplete $percent

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
    $ext = $file.Extension
    $destPath = Join-Path -Path $DestinationRoot -ChildPath $file.Name
    
    if (Test-Path -Path $destPath -PathType Leaf) {
        $timeStamp = (Get-Date).ToString("yyyyMMdd_HHmmss_fff")
        $destPath = Join-Path -Path $DestinationRoot -ChildPath "${baseName}_${timeStamp}${ext}"
    }

    try {
        Copy-Item -Path $file.FullName -Destination $destPath -Force -ErrorAction Stop
        $SuccessCount++
        Write-TransactionLog -Source $file.FullName -Destination $destPath -Status "SUCCESS"
    } catch {
        Write-TransactionLog -Source $file.FullName -Destination $destPath -Status "FAILED" -ErrorReason $_.Exception.Message
    }
}

Write-Progress -Activity "Collecting Knowledge Base Files" -Completed
Write-Host "Successfully added $SuccessCount new files to Raw_copies." -ForegroundColor Green
