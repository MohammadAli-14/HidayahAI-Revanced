"""
Hidayah AI — Theological Gateway & API Server
FastAPI entrypoint serving Quran data, Hadith Takhrīj, Tafseer, RAG, and AI Scholar streaming.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time

from backend.config import CORS_ORIGINS
from backend.routes.quran import router as quran_router
from backend.routes.tafsir import router as tafsir_router
from backend.routes.hadith import router as hadith_router
from backend.routes.scholar import router as scholar_router
from backend.routes.rag import router as rag_router
from backend.routes.names import router as names_router

app = FastAPI(
    title="Hidayah AI — Theological Research Gateway",
    description="High-performance async API for Quranic research, Hadith authentication, and scholarly RAG.",
    version="2.0.0",
)

# CORS Middleware for Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers under /api
app.include_router(quran_router, prefix="/api")
app.include_router(tafsir_router, prefix="/api")
app.include_router(hadith_router, prefix="/api")
app.include_router(scholar_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
app.include_router(names_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Hidayah AI Gateway",
        "version": "2.0.0",
        "timestamp": time.time(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=True)
