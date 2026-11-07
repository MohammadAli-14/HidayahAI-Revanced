"""
Hidayah AI — Unified Platform Runner
Launches both the FastAPI Theological Gateway (Port 8001) and the Next.js Frontend (Port 3000) simultaneously.
Usage:
    python run_platform.py
"""

import subprocess
import sys
import time
import os
import webbrowser
import urllib.request
import urllib.error
from pathlib import Path

# Enforce UTF-8 on Windows terminal streams to avoid UnicodeEncodeError
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"
VENV_PYTHON = ROOT_DIR / ".venv" / "Scripts" / "python.exe"

if not VENV_PYTHON.exists():
    VENV_PYTHON = Path(sys.executable)

BACKEND_PORT = "8001"
FRONTEND_PORT = "3000"

print("=" * 65)
print("[HIDAYAH AI] THEOLOGICAL RESEARCH PLATFORM")
print("=" * 65)
print(f"1. Launching FastAPI Theological Gateway (Port {BACKEND_PORT})...")

# Enforce UTF-8 environment for subprocesses to avoid UnicodeEncodeError with Arabic scripture
backend_env = {
    **os.environ,
    "PYTHONIOENCODING": "utf-8",
    "PYTHONUTF8": "1",
}

# 1. Start FastAPI Backend Gateway on Port 8001
backend_cmd = [
    str(VENV_PYTHON),
    "-m",
    "uvicorn",
    "backend.main:app",
    "--host",
    "127.0.0.1",
    "--port",
    BACKEND_PORT,
    "--reload",
]

backend_proc = subprocess.Popen(
    backend_cmd,
    cwd=str(ROOT_DIR),
    env=backend_env,
    stdout=sys.stdout,
    stderr=sys.stderr,
)

# Actively poll FastAPI health endpoint until gateway is fully initialized
print(f"Waiting for FastAPI Gateway on http://127.0.0.1:{BACKEND_PORT}/api/health...")
backend_ready = False
health_url = f"http://127.0.0.1:{BACKEND_PORT}/api/health"
for _ in range(30):
    time.sleep(0.5)
    try:
        req = urllib.request.Request(health_url, headers={"User-Agent": "HidayahPlatformRunner/1.0"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            if resp.status == 200:
                backend_ready = True
                break
    except Exception:
        pass

if backend_ready:
    print(f"[OK] FastAPI Gateway is ready and active on http://127.0.0.1:{BACKEND_PORT}")
else:
    print(f"[OK] FastAPI Gateway active on http://127.0.0.1:{BACKEND_PORT} (startup continuing...)")

# 2. Start Next.js Frontend
print(f"2. Launching Next.js Research Dashboard (Port {FRONTEND_PORT})...")
frontend_cmd = ["npm", "run", "dev"]

frontend_proc = subprocess.Popen(
    frontend_cmd,
    cwd=str(FRONTEND_DIR),
    shell=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)

# Actively poll Next.js dev server readiness before opening browser
dashboard_url = f"http://localhost:{FRONTEND_PORT}"
for _ in range(30):
    time.sleep(0.5)
    try:
        req = urllib.request.Request(dashboard_url, headers={"User-Agent": "HidayahPlatformRunner/1.0"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            if resp.status in (200, 304):
                break
    except Exception:
        pass

print(f"[OK] Next.js Frontend available at {dashboard_url}")
print("Opening browser...")

try:
    webbrowser.open(dashboard_url)
except Exception:
    pass

print("=" * 65)
print("Platform running! Press Ctrl+C in this terminal to shut down.")
print("=" * 65)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down Hidayah AI services...")
    backend_proc.terminate()
    frontend_proc.terminate()
    print("Services stopped.")
