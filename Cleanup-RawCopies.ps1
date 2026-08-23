<#
.SYNOPSIS
    Robust clean-up script for KnowledgeBase_Staging\Raw_copies (or any directory).
    Performs safe clean-up operations without deleting original files from source.
    Moves identified files to a timestamped quarantine folder (Vault) and outputs a summary report.
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory=$true, Position=0)]
    [string]$SourcePath,

    [string]$QuarantineRoot
)

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "$timestamp : $Message"
    Write-Host $line
    if ($logFile) { Add-Content -Path $logFile -Value $line }
}

if (-not (Test-Path -Path $SourcePath -PathType Container)) {
    Write-Error "Source path does not exist or is not a directory: $SourcePath"
    exit 1
}

if (-not $QuarantineRoot) {
    $QuarantineRoot = Join-Path -Path $SourcePath -ChildPath 'Cleanup_Quarantine'
}
if (-not (Test-Path -Path $QuarantineRoot -PathType Container)) {
    try { New-Item -ItemType Directory -Path $QuarantineRoot -Force | Out-Null }
    catch { Write-Error "Failed to create quarantine directory: $QuarantineRoot"; exit 1 }
}

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$quarantineBase = Join-Path -Path $QuarantineRoot -ChildPath $timestamp
New-Item -ItemType Directory -Path $quarantineBase -Force | Out-Null

$logFile = Join-Path -Path $quarantineBase -ChildPath 'cleanup_log.txt'
Write-Log "=== Clean-up started ==="
Write-Log "Source path: $SourcePath"
Write-Log "Vault (quarantine) base: $quarantineBase"

$tempCount = 0
$zeroCount = 0
$dupCount = 0
$uniqueDupSets = 0

$tempExtensions = @('.tmp', '.temp', '.log', '.bak', '.old', '.wbk', '.dmp')
$sourceRoot = (Get-Item $SourcePath).FullName

# Helper to get safe relative path string
function Get-RelPath {
    param($fullPath)
    if ($fullPath.StartsWith($sourceRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $fullPath.Substring($sourceRoot.Length).TrimStart('\','/')
    }
    return $fullPath
}

# 1. Temporary files
Write-Log "Scanning for temporary files..."
$tempFiles = Get-ChildItem -Path $SourcePath -Recurse -File -Include $tempExtensions -ErrorAction SilentlyContinue
foreach ($file in $tempFiles) {
    try {
        $relative = Get-RelPath $file.FullName
        $dest = Join-Path -Path $quarantineBase -ChildPath ("temp_" + ($relative -replace '[\\:/]', '_'))
        $destDir = Split-Path -Path $dest -Parent
        if (-not (Test-Path -Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
        Move-Item -Path $file.FullName -Destination $dest -Force
        Write-Log ("Moved temporary file: {0} -> {1}" -f $file.FullName, $dest)
        $tempCount++
    } catch { Write-Log "ERROR moving temporary $($file.FullName): $_" }
}

# 2. Zero-byte files
Write-Log "Scanning for zero-byte files..."
$zeroBytes = Get-ChildItem -Path $SourcePath -Recurse -File | Where-Object { $_.Length -eq 0 }
foreach ($file in $zeroBytes) {
    try {
        $relative = Get-RelPath $file.FullName
        $dest = Join-Path -Path $quarantineBase -ChildPath ("zero_" + ($relative -replace '[\\:/]', '_'))
        $destDir = Split-Path -Path $dest -Parent
        if (-not (Test-Path -Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
        Move-Item -Path $file.FullName -Destination $dest -Force
        Write-Log ("Moved zero-byte file: {0} -> {1}" -f $file.FullName, $dest)
        $zeroCount++
    } catch { Write-Log "ERROR moving zero-byte $($file.FullName): $_" }
}

# 3. Duplicate files (SHA-256)
Write-Log "Scanning for duplicate files (SHA-256)..."
$allFiles = Get-ChildItem -Path $SourcePath -Recurse -File -ErrorAction SilentlyContinue
$hashTable = @{}
foreach ($file in $allFiles) {
    try {
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        $hash = [System.BitConverter]::ToString($sha256.ComputeHash($bytes)).Replace('-', '').ToLower()
        $sha256.Dispose()
        if (-not $hashTable.ContainsKey($hash)) { $hashTable[$hash] = @() }
        $hashTable[$hash] += $file.FullName
    } catch { Write-Log "ERROR hashing $($file.FullName): $_" }
}

foreach ($hash in $hashTable.Keys) {
    $files = $hashTable[$hash]
    if ($files.Count -gt 1) {
        $uniqueDupSets++
        $sorted = $files | Sort-Object
        $toKeep = $sorted[0]
        $duplicates = $sorted[1..($sorted.Count-1)]
        foreach ($dup in $duplicates) {
            try {
                $relative = Get-RelPath $dup
                $dest = Join-Path -Path $quarantineBase -ChildPath ("dup_" + ($relative -replace '[\\:/]', '_'))
                $destDir = Split-Path -Path $dest -Parent
                if (-not (Test-Path -Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
                Move-Item -Path $dup -Destination $dest -Force
                Write-Log ("Moved duplicate file: {0} -> {1} (keeping {2})" -f $dup, $dest, $toKeep)
                $dupCount++
            } catch { Write-Log "ERROR moving duplicate: $_" }
        }
    }
}

# Summary Report
Write-Log "`n=== SUMMARY REPORT ===`n"
Write-Log "Temporary files moved to Vault: $tempCount"
Write-Log "Zero-byte files moved to Vault:  $zeroCount"
Write-Log "Duplicate file sets found:       $uniqueDupSets"
Write-Log "Duplicate files moved to Vault:  $dupCount"
Write-Log "Files purged (deleted):          0"
Write-Log "Vault location: $quarantineBase"
Write-Log "Log file: $logFile"
Write-Log "=== Clean-up finished ==="