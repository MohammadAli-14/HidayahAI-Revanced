# Hidayah AI Unified PowerShell Launcher
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  HIDAYAH AI - THEOLOGICAL RESEARCH WORKSTATION" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Launching FastAPI Gateway (Port 8001) and Next.js (Port 3000)..." -ForegroundColor Green

$pythonExe = if (Test-Path ".\.venv\Scripts\python.exe") { ".\.venv\Scripts\python.exe" } else { "python" }
& $pythonExe run_platform.py
