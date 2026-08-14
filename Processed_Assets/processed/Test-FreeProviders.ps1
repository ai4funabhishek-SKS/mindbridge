<#
.SYNOPSIS
OmniRoute Free Providers E2E Test Runner (PowerShell 5.1 compatible)
.DESCRIPTION
Tests every configured provider via OmniRoute's local API endpoint.
Validates: (1) Auth, (2) Inference response format, (3) Error handling, (4) Failover.
Outputs: Color-coded console report + CSV log.
.USAGE
1. Ensure OmniRoute is running: open http://localhost:20128
2. Open PowerShell as regular user
3. Run: cd "C:\ai-stack\OmniRoute-FreeProviders-Config"
4. Quick test: .\Test-FreeProviders.ps1 -Mode Quick
5. Full test:  .\Test-FreeProviders.ps1 -Mode Full -IncludeFailover
#>
param(
  [ValidateSet("Quick","Full")][string]$Mode = "Quick",
  [switch]$IncludeFailover,
  [string]$OmniRouteBase = "http://localhost:20128",
  [string]$AuthHeaderValue = ""
)

$ErrorActionPreference = "Continue"

# PowerShell 5.1 compatibility helper (replaces the PS7+ ?? null-coalesce operator)
function Get-FirstNonEmpty([object[]]$Values, [object]$Default = "N/A") {
  foreach ($v in $Values) {
    if ($null -ne $v -and "$v" -ne "" -and $v -isnot [System.DBNull]) { return $v }
  }
  return $Default
}

$Report = @()
$TestPrompt = "Reply with exactly and only: OK-OMNIROUTE-TEST"
$Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

# --- Auth header handling (401 bypass) ---
$Headers = @{}
if ($AuthHeaderValue -ne "") {
  $Headers["Authorization"] = "Bearer $AuthHeaderValue"
} else {
  $envPath = "C:\Users\FTT\.omniroute\.env"
  if (Test-Path $envPath) {
    $envContent = Get-Content $envPath -Raw
    if ($envContent -match "API_KEY[=:]\s*(\S+)") {
      $Headers["Authorization"] = "Bearer $($Matches[1])"
    } elseif ($envContent -match "AUTH_TOKEN[=:]\s*(\S+)") {
      $Headers["Authorization"] = "Bearer $($Matches[1])"
    }
  }
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " OmniRoute Free Providers E2E Test Runner" -ForegroundColor Cyan
$authStatus = if ($Headers.Count -gt 0) { "YES" } else { "NONE" }
Write-Host (" Mode: {0} | Base: {1} | Auth: {2}" -f $Mode, $OmniRouteBase, $authStatus) -ForegroundColor Gray
Write-Host "=============================================" -ForegroundColor Cyan

# --- Step 0: Verify OmniRoute Server is Alive ---
Write-Host ""
Write-Host "[0/4] Checking OmniRoute server health..." -ForegroundColor Yellow
try {
  $HealthParams = @{
    Uri = "$OmniRouteBase/api/health"
    TimeoutSec = 5
    ErrorAction = "Stop"
  }
  if ($Headers.Count -gt 0) { $HealthParams["Headers"] = $Headers }
  $Health = Invoke-RestMethod @HealthParams
  Write-Host "  [OK] OmniRoute server ONLINE" -ForegroundColor Green
  $ver = Get-FirstNonEmpty @($Health.version, $Health.build) "N/A"
  $up  = Get-FirstNonEmpty @($Health.uptime, $Health.startedAt) "N/A"
  Write-Host ("     Version: {0} | Uptime: {1}" -f $ver, $up) -ForegroundColor Gray
} catch {
  $status = 0
  try { $status = [int]$_.Exception.Response.StatusCode.value__ } catch {}
  if ($status -eq 401) {
    Write-Host "  [WARN] Server ONLINE but requires auth (401 UNAUTHORIZED)." -ForegroundColor Yellow
    Write-Host "     Re-run with: -AuthHeaderValue <YOUR_DASHBOARD_API_KEY>" -ForegroundColor Yellow
    Write-Host "     Quick checks work via DASHBOARD UI instead (Providers -> TEST button)." -ForegroundColor Gray
  } else {
    Write-Host "  [FAIL] SERVER OFFLINE! Cannot run tests." -ForegroundColor Red
    Write-Host "     Start server: omniroute server start" -ForegroundColor Yellow
    exit 1
  }
}

# --- Step 1: Get List of Configured Providers ---
Write-Host ""
Write-Host "[1/4] Fetching configured providers from OmniRoute..." -ForegroundColor Yellow
try {
  $ProvParams = @{
    Uri = "$OmniRouteBase/api/providers"
    TimeoutSec = 10
    ErrorAction = "Stop"
  }
  if ($Headers.Count -gt 0) { $ProvParams["Headers"] = $Headers }
  $Providers = Invoke-RestMethod @ProvParams
  if ($Providers -is [array]) {
    $AllProvs = $Providers
  } elseif ($Providers.providers -is [array]) {
    $AllProvs = $Providers.providers
  } elseif ($Providers.data -is [array]) {
    $AllProvs = $Providers.data
  } else {
    $AllProvs = @($Providers)
  }
  $Configured = $AllProvs | Where-Object {
    $_.configured -eq $true -or
    $_.hasApiKey -eq $true -or
    $_.status -eq "connected" -or
    $_.enabled -eq $true
  }
  Write-Host ("  [OK] Found {0} configured providers out of {1} total" -f $Configured.Count, $AllProvs.Count) -ForegroundColor Green
  if ($Configured.Count -eq 0) {
    Write-Host "  [WARN] No providers configured yet. Complete signup steps first." -ForegroundColor Yellow
    exit 0
  }
} catch {
  Write-Host ("  [FAIL] Failed to fetch providers: {0}" -f $_) -ForegroundColor Red
  exit 1
}

# --- Step 2: Inference Test per Provider ---
Write-Host ""
Write-Host "[2/4] Running inference tests on each provider..." -ForegroundColor Yellow
$TestCount = if ($Mode -eq "Quick") { 1 } else { 3 }

foreach ($Provider in $Configured) {
  $PIDV = Get-FirstNonEmpty @($Provider.id, $Provider.key, $Provider.name)
  $PName = Get-FirstNonEmpty @($Provider.name, $PIDV)
  $DefaultModel = Get-FirstNonEmpty @($Provider.defaultModel, $Provider.model, "gpt-4o-mini")
  Write-Host ""
  Write-Host ("  --- Testing: {0} [{1}] ---" -f $PName, $PIDV) -ForegroundColor White

  for ($i = 1; $i -le $TestCount; $i++) {
    $PWarm = $Stopwatch.ElapsedMilliseconds
    try {
      $BodyObj = @{
        model = $DefaultModel
        messages = @(@{ role = "user"; content = $TestPrompt })
        max_tokens = 50
        temperature = 0
        stream = $false
        provider = $PIDV
      }
      $Body = $BodyObj | ConvertTo-Json -Depth 5

      $CallParams = @{
        Uri = "$OmniRouteBase/v1/chat/completions"
        Method = "Post"
        Body = $Body
        ContentType = "application/json"
        TimeoutSec = 30
        ErrorAction = "Stop"
      }
      if ($Headers.Count -gt 0) { $CallParams["Headers"] = $Headers }

      $Resp = Invoke-RestMethod @CallParams
      $Latency = $Stopwatch.ElapsedMilliseconds - $PWarm

      $Choices = $Resp.choices
      if (-not $Choices -or $Choices.Count -eq 0) {
        throw "No choices returned in response"
      }
      $Content = $Choices[0].message.content
      if ([string]::IsNullOrWhiteSpace($Content)) {
        $Content = "[EMPTY RESPONSE]"
      }
      $Usage = Get-FirstNonEmpty @($Resp.usage, @{}) @{}
      $TokensIn  = Get-FirstNonEmpty @($Usage.prompt_tokens, $Usage.input_tokens, 0) 0
      $TokensOut = Get-FirstNonEmpty @($Usage.completion_tokens, $Usage.output_tokens, 0) 0
      $ProvUsed = Get-FirstNonEmpty @($Resp.provider_used, $PIDV)

      if ($Content -match "OK-OMNIROUTE") { $Status = "PASS"; $Color = "Green" }
      else { $Status = "PARTIAL"; $Color = "Yellow" }

      $previewLen = [Math]::Min(80, $Content.Length)
      Write-Host ("    [{0}/{1}] {2} via:{3} [TIME] {4} ms | [IN] {5} -> [OUT] {6}" -f
        $i, $TestCount, $Status, $ProvUsed, $Latency, $TokensIn, $TokensOut) -ForegroundColor $Color
      Write-Host ("       Preview: {0}" -f $Content.Substring(0, $previewLen)) -ForegroundColor Gray

      $respPreviewLen = [Math]::Min(120, $Content.Length)
      $Report += [PSCustomObject]@{
        Timestamp = Get-Date -Format o
        ProviderID = $PIDV
        ProviderName = $PName
        ProviderUsed = $ProvUsed
        TestNumber = $i
        Status = $Status
        LatencyMs = $Latency
        PromptTokens = $TokensIn
        CompletionTokens = $TokensOut
        ResponsePreview = $Content.Substring(0, $respPreviewLen)
        Error = $null
      }
    } catch {
      $ErrMsg = $_.Exception.Message
      $HttpCode = 0
      try { $HttpCode = [int]$_.Exception.Response.StatusCode.value__ } catch {}
      Write-Host ("    [{0}/{1}] FAIL  HTTP {2}" -f $i, $TestCount, $HttpCode) -ForegroundColor Red
      $shortErrLen = [Math]::Min(100, $ErrMsg.Length)
      $shortErr = if ($ErrMsg.Length -gt 100) { $ErrMsg.Substring(0,100) + "..." } else { $ErrMsg }
      Write-Host ("       Error: {0}" -f $shortErr) -ForegroundColor DarkRed

      $Report += [PSCustomObject]@{
        Timestamp = Get-Date -Format o
        ProviderID = $PIDV
        ProviderName = $PName
        ProviderUsed = $null
        TestNumber = $i
        Status = "FAIL"
        LatencyMs = $null
        PromptTokens = $null
        CompletionTokens = $null
        ResponsePreview = $null
        Error = $ErrMsg
      }
    }
  }
}

# --- Step 3: Failover Routing Test (Optional) ---
if ($IncludeFailover -and $Configured.Count -ge 3) {
  Write-Host ""
  Write-Host "[3/4] Testing multi-provider failover routing..." -ForegroundColor Yellow
  try {
    $BodyObj = @{
      model = "gpt-4o-mini"
      messages = @(@{ role = "user"; content = "Say exactly 'ROUTING-OK' as 1 word" })
      max_tokens = 20
      temperature = 0
      stream = $false
    }
    $Body = $BodyObj | ConvertTo-Json -Depth 5

    $RouteParams = @{
      Uri = "$OmniRouteBase/v1/chat/completions"
      Method = "Post"
      Body = $Body
      ContentType = "application/json"
      TimeoutSec = 45
      ErrorAction = "Stop"
    }
    if ($Headers.Count -gt 0) { $RouteParams["Headers"] = $Headers }

    $RResp = Invoke-RestMethod @RouteParams
    $UsedProvider = Get-FirstNonEmpty @($RResp.provider_used, "N/A")
    $Content = $RResp.choices[0].message.content
    if ($Content -match "ROUTING-OK") {
      Write-Host ("  [OK] AUTO-ROUTING PASS! Chosen provider: {0}" -f $UsedProvider) -ForegroundColor Green
      Write-Host ("     Response: {0}" -f $Content) -ForegroundColor Gray
    } else {
      Write-Host ("  [WARN] Got response but not exact match. Chosen provider: {0}" -f $UsedProvider) -ForegroundColor Yellow
      Write-Host ("     Response: {0}" -f $Content) -ForegroundColor Gray
    }
  } catch {
    Write-Host ("  [WARN] Failover test had issue: {0}" -f $_) -ForegroundColor Yellow
  }
} else {
  if (-not $IncludeFailover) {
    Write-Host ""
    Write-Host "[3/4] Skipping failover test (use -IncludeFailover flag to enable)" -ForegroundColor Gray
  } else {
    Write-Host ""
    Write-Host ("[3/4] Skipping failover test (need >=3 configured providers, currently {0})" -f $Configured.Count) -ForegroundColor Gray
  }
}

# --- Step 4: Summary Report ---
Write-Host ""
Write-Host "[4/4] Generating summary report..." -ForegroundColor Yellow
$PassCount    = ($Report | Where-Object { $_.Status -eq "PASS" }).Count
$FailCount    = ($Report | Where-Object { $_.Status -eq "FAIL" }).Count
$PartialCount = ($Report | Where-Object { $_.Status -eq "PARTIAL" }).Count
$Total = $Report.Count
$TotalRuntime = $Stopwatch.Elapsed.ToString("mm\:ss")

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$testDir = "$PSScriptRoot\test_results"
if (-not (Test-Path $testDir)) { New-Item -ItemType Directory -Path $testDir -Force | Out-Null }
$CsvPath = "$testDir\TestResults_FreeProviders_$ts.csv"
$Report | Export-Csv -Path $CsvPath -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host (" TEST RUN COMPLETE - TOTAL TIME: {0}" -f $TotalRuntime) -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ("  Total Tests Run : {0}" -f $Total) -ForegroundColor White
if ($Total -gt 0) {
  $pctP = [math]::Round(100*$PassCount/$Total, 1)
  $pctF = [math]::Round(100*$FailCount/$Total, 1)
  $pctX = [math]::Round(100*$PartialCount/$Total, 1)
  Write-Host ("  [OK] Passed       : {0}  ({1}%)" -f $PassCount, $pctP) -ForegroundColor Green
  Write-Host ("  [WARN] Partial    : {0}  ({1}%)" -f $PartialCount, $pctX) -ForegroundColor Yellow
  Write-Host ("  [FAIL] Failed     : {0}  ({1}%)" -f $FailCount, $pctF) -ForegroundColor Red
} else {
  Write-Host "  (No tests executed - check output above for reason)" -ForegroundColor Gray
}
Write-Host ("  [CSV] CSV Log     : {0}" -f $CsvPath) -ForegroundColor Gray
Write-Host "=============================================" -ForegroundColor Cyan

if ($FailCount -gt 0) {
  Write-Host ""
  Write-Host "[TIP] FAILURES TO DEBUG (top 10 shown):" -ForegroundColor Yellow
  $Report | Where-Object { $_.Status -eq "FAIL" } | Select-Object -First 10 | ForEach-Object {
    $e = $_.Error
    if ($e.Length -gt 100) { $e = $e.Substring(0,100) + "..." }
    Write-Host ("  * {0} [{1}]: {2}" -f $_.ProviderName, $_.TestNumber, $e) -ForegroundColor DarkRed
  }
}

# Quick recommendations
if ($Total -gt 0 -and $PassCount/$Total -lt 0.80) {
  Write-Host ""
  Write-Host "[INFO] RECOMMENDATION: PASS rate below 80%. Investigate failures and re-test:" -ForegroundColor Cyan
  Write-Host "   1. 401 errors -> re-paste/regen API keys" -ForegroundColor White
  Write-Host "   2. 403 errors -> check provider ToS or regional geo settings" -ForegroundColor White
  Write-Host "   3. 429 errors -> lower routing weight & set Hard Cap to 50%" -ForegroundColor White
  Write-Host "   4. 500 errors -> provider transient outage; retry later (circuit-breaker will help)" -ForegroundColor White
}
Write-Host ""
