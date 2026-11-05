"""
Hidayah AI — RAG & Document Knowledge Base API Routes
Handles scholarly PDF uploads, chunking, and persistent LanceDB indexing.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional, Dict, Any
import io

from rag.smart_loader import load_and_chunk_pdf
from rag.lancedb_store import IslamicLanceStore
from utils.logger import get_logger

log = get_logger("routes_rag")
router = APIRouter(prefix="/rag", tags=["RAG"])


@router.get("/documents")
async def list_documents():
    """List all indexed scholarly PDF documents in LanceDB."""
    store = IslamicLanceStore()
    if not store.is_available():
        return {"documents": [], "total_chunks": 0}

    docs = store.list_indexed_documents()
    total_chunks = sum(d.get("chunk_count", 0) for d in docs)
    return {
        "documents": docs,
        "total_chunks": total_chunks,
    }


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a scholarly Islamic PDF, extract text with Arabic normalization,
    chunk semantically, and index into LanceDB with Tantivy BM25.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        content = await file.read()
        file_obj = io.BytesIO(content)

        # Chunk the PDF
        chunks = load_and_chunk_pdf(file_obj, filename=file.filename)
        if not chunks:
            raise HTTPException(status_code=422, detail="No extractable text found in this PDF.")

        # Index in LanceDB
        store = IslamicLanceStore()
        if not store.is_available():
            raise HTTPException(status_code=500, detail="LanceDB vector store is unavailable.")

        success = store.index_chunks(chunks, replace_existing_file=True)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to index document chunks into LanceDB.")

        return {
            "success": True,
            "filename": file.filename,
            "chunks_indexed": len(chunks),
            "message": f"Successfully indexed {len(chunks)} chunks into LanceDB.",
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error processing PDF upload: {e}")
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")
