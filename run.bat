@echo off
title Hidayah AI Platform Runner
echo ================================================================
echo  [33m HIDAYAH AI -- THEOLOGICAL RESEARCH WORKSTATION[0m
echo ================================================================
echo Launching FastAPI Theological Gateway (Port 8001) ^& Next.js (Port 3000)...
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run_platform.py
) else (
    python run_platform.py
)

pause
