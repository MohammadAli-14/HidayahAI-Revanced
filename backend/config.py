"""
Hidayah AI — Backend Configuration
Configures environment variables, paths, and API settings for FastAPI.
"""

import sys
from pathlib import Path

# Ensure root directory is on sys.path so utils, agents, rag can be imported seamlessly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.config import (
    GEMINI_API_KEY,
    TAVILY_API_KEY,
    USE_LOCAL_LLM,
    LOCAL_LLM_URL,
    LOCAL_LLM_MODEL,
    LANCEDB_DIR,
    JUZ_DATA,
    AUDIO_MODES,
)

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "*",
]
