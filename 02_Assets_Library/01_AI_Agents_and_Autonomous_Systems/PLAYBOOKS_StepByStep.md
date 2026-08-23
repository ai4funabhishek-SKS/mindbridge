# STEP-BY-STEP PLAYBOOKS
## PB1 OmniRoute Upgrade: npm install -g omniroute@latest → verify 3.8.50 → restart.
## PB2 Add Provider: Dashboard → Providers → API Key Tab → + Add → Paste → TEST&SAVE.
## PB3 Troubleshoot 401/403: New key regen. Check multi-key: CF (2), Doubao (2),
##    SparkDesk (3), Baidu/Tencent (2). Regional geo: Chinese providers need CN VPN.
## PB4 Ollama Local: 1) `ollama serve` window. 2) pull qwen2.5:7b + phi4:14b.
##    3) Add provider Ollama base=http://localhost:11434 any key. 4) Weight=50.
## PB5 Test Runner: cd project → .\Test-FreeProviders.ps1 -Mode Full -IncludeFailover
## PB6 Monthly schtasks: schtasks /Create /TN "OmniRoute Monthly Health Check"
##    /TR project\run_monthly_tests.bat /SC MONTHLY /ST 09:00
## PB7 Rollback: Rename folder .omniroute.BACKUP-PRE-* → .omniroute + pin npm old.
