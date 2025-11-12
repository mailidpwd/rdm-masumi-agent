# RDM API Server Startup Script
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Starting RDM API Server with Masumi Integration" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv311\Scripts\Activate.ps1

# Verify Python version
Write-Host "Python version:" -ForegroundColor Yellow
python --version

# Start the server
Write-Host ""
Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "API will be available at: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python main.py api

