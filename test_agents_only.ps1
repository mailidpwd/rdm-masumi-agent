# Test RDM Agents Without Server
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Testing RDM Agents (Agent 1 + Agent 2)" -ForegroundColor Cyan  
Write-Host "  No API server needed - Direct agent execution" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv311\Scripts\Activate.ps1

Write-Host "Running complete RDM flow (Agent 1 -> Agent 2)..." -ForegroundColor Green
Write-Host ""

python rdm_agents.py full-flow

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Test Complete!" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

