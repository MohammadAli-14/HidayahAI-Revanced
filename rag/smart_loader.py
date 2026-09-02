"""
Hidayah AI — Smart Document Loader & Arabic/Urdu Chunker
Uses PyMuPDF (fitz) for high-fidelity text & metadata extraction with Arabic RTL support.
"""

import io
import re
import unicodedata
from utils.logger import get_logger

log = get_logger("smart_loader")


def normalize_arabic(text: str, strip_tashkeel: bool = False) -> str:
    """
    Normalize Arabic and Urdu text for reliable semantic and lexical search.
    
    Args:
        text: Raw input text
        strip_tashkeel: If True, removes diacritics (fatha, damma, kasra, sukun, shadda).
    """
    if not text:
        return ""

    # Normalize unicode forms (NFC)
    text = unicodedata.normalize("NFC", text)

    # Normalize Alef variants
    text = re.sub(r"[إأآٱ]", "ا", text)

    # Normalize Persian/Urdu Yeh/Kaf to standard Arabic or vice-versa
    text = re.sub(r"[ىي]", "ي", text)
    text = re.sub(r"ك", "ك", text)

    # Strip control characters & zero-width artifacts
    text = re.sub(r"[\u200B-\u200F\u202A-\u202E\uFEFF]", "", text)

    if strip_tashkeel:
        # Arabic diacritics unicode range 064B - 0652 + 0670
        text = re.sub(r"[\u064B-\u0652\u0670\u0653-\u065F]", "", text)

    # Normalize multiple whitespace / newlines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pages_from_pdf(pdf_file, filename: str = "document.pdf") -> list[dict]:
    """
    Extract text page-by-page from an uploaded PDF file with structural metadata.

    Args:
        pdf_file: Streamlit UploadedFile or file-like object / bytes
        filename: Name of the uploaded file

    Returns:
        List of dicts: [{"page": 1, "text": "...", "filename": "..."}]
    """
    pages_data = []

    # Read bytes from UploadedFile
    if hasattr(pdf_file, "getvalue"):
        pdf_bytes = pdf_file.getvalue()
    elif hasattr(pdf_file, "read"):
        pdf_bytes = pdf_file.read()
        if hasattr(pdf_file, "seek"):
            pdf_file.seek(0)
    elif isinstance(pdf_file, bytes):
        pdf_bytes = pdf_file
    else:
        pdf_bytes = None

    if not pdf_bytes:
        log.error("Empty or invalid PDF file stream")
        return []

    # Attempt extraction via PyMuPDF (Primary - best for RTL Arabic/Urdu)
    try:
        import pymupdf

        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text("text") or ""
            cleaned = page_text.strip()
            if cleaned:
                pages_data.append({
                    "page": page_idx + 1,
                    "text": cleaned,
                    "filename": filename,
                })
        doc.close()
        log.info(f"PyMuPDF extracted {len(pages_data)} pages from {filename}")
        if pages_data:
            return pages_data
    except ImportError:
        log.warning("PyMuPDF not installed. Falling back to PyPDF2.")
    except Exception as e:
        log.warning(f"PyMuPDF extraction error: {e}. Falling back to PyPDF2.")

    # Fallback extraction via PyPDF2
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            cleaned = page_text.strip()
            if cleaned:
                pages_data.append({
                    "page": page_idx + 1,
                    "text": cleaned,
                    "filename": filename,
                })
        log.info(f"PyPDF2 fallback extracted {len(pages_data)} pages from {filename}")
        return pages_data
    except Exception as e:
        log.error(f"PDF extraction failed completely: {e}")
        return []


def chunk_pages(
    pages_data: list[dict],
    chunk_size: int = 400,
    overlap: int = 50,
) -> list[dict]:
    """
    Split extracted pages into cohesive semantic chunks while preserving
    page numbers, document names, and paragraph structure.

    Args:
        pages_data: Output of extract_pages_from_pdf
        chunk_size: Approximate target word count per chunk
        overlap: Overlapping word count between consecutive chunks

    Returns:
        List of chunk dicts:
        [
            {
                "id": "doc.pdf_p1_c0",
                "text": "...",
                "clean_text": "...",
                "page": 1,
                "filename": "doc.pdf",
                "chunk_index": 0,
                "word_count": 350
            },
            ...
        ]
    """
    if not pages_data:
        return []

    chunks = []
    chunk_index = 0

    for page_item in pages_data:
        page_num = page_item["page"]
        filename = page_item["filename"]
        raw_text = page_item["text"]

        # Split into natural paragraphs
        paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [raw_text]

        current_words = []

        for para in paragraphs:
            words = para.split()
            if not words:
                continue

            if len(current_words) + len(words) > chunk_size and current_words:
                chunk_str = " ".join(current_words).strip()
                if chunk_str:
                    clean_str = normalize_arabic(chunk_str, strip_tashkeel=False)
                    chunks.append({
                        "id": f"{filename}_p{page_num}_c{chunk_index}",
                        "text": chunk_str,
                        "clean_text": clean_str,
                        "page": page_num,
                        "filename": filename,
                        "chunk_index": chunk_index,
                        "word_count": len(current_words),
                    })
                    chunk_index += 1

                # Keep overlap from previous words
                current_words = current_words[-overlap:] if len(current_words) > overlap else []

            current_words.extend(words)

        if current_words:
            chunk_str = " ".join(current_words).strip()
            if chunk_str:
                clean_str = normalize_arabic(chunk_str, strip_tashkeel=False)
                chunks.append({
                    "id": f"{filename}_p{page_num}_c{chunk_index}",
                    "text": chunk_str,
                    "clean_text": clean_str,
                    "page": page_num,
                    "filename": filename,
                    "chunk_index": chunk_index,
                    "word_count": len(current_words),
                })
                chunk_index += 1

    return chunks


def load_and_chunk_pdf(
    pdf_file,
    filename: str = "document.pdf",
    chunk_size: int = 400,
    overlap: int = 50,
) -> list[dict]:
    """
    End-to-end pipeline: Extract pages and build structured Islamic chunks.
    """
    pages = extract_pages_from_pdf(pdf_file, filename=filename)
    return chunk_pages(pages, chunk_size=chunk_size, overlap=overlap)
