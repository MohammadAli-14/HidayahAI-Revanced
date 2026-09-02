"""
Hidayah AI — RAG Query Engine
Retrieves relevant PDF excerpts using LanceDB Hybrid Search + Reranking,
verifies citations, and generates answers using Gemini 2.5 (or local LLM).
"""

from google import genai
import requests
from utils.config import (
    MODEL_SCHOLAR,
    GEMINI_API_KEY,
    get_gemini_client,
    USE_LOCAL_LLM,
    LOCAL_LLM_URL,
    LOCAL_LLM_MODEL,
)
from rag.vector_store import search_index
from utils.islamic_guardrails import check_fatwa_sensitivity, verify_grounded_citations
from utils.logger import get_logger

log = get_logger("rag_query")

RAG_SYSTEM_PROMPT = """You are Hidayah AI, analyzing a USER-UPLOADED scholarly PDF document.

CRITICAL DISTINCTION:
- Your answers reflect the content of THIS SPECIFIC PDF document only.
- You are NOT issuing personal religious rulings (fatwas).
- Clearly distinguish document author claims from verified classical consensus.
- Quote directly from the PDF when possible, using quotation marks and page citations.
- If the context does not contain enough information, state: "The uploaded document does not contain sufficient details on this specific point."

Guidelines:
1. Answer strictly based on the provided PDF context excerpts below.
2. Cite the exact page number and document name whenever available (e.g. "[Page 4]").
3. Maintain an academic, respectful tone.
4. Support both English, Arabic, and Urdu based on the user's inquiry language.
5. Always conclude with: "Source: Uploaded document analysis. Verify religious rulings with qualified scholars." """


def _generate_local_llm(prompt: str, system_prompt: str) -> str | None:
    """Generate response via local OpenAI-compatible API (Ollama / vLLM / ALLaM)."""
    try:
        payload = {
            "model": LOCAL_LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 2048,
        }
        res = requests.post(f"{LOCAL_LLM_URL}/chat/completions", json=payload, timeout=60)
        if res.status_code == 200:
            data = res.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        log.warning(f"Local LLM fallback failed: {e}")
    return None


def query_pdf(
    question: str,
    index=None,
    chunks: list = None,
    top_k: int = 5,
    filename_filter: str | None = None,
) -> str:
    """
    Answer a question using the RAG pipeline:
    1. Check Islamic Fatwa sensitivity gate
    2. Hybrid Search (LanceDB BM25 + Vector) + Cross-Encoder Rerank
    3. LLM Generation with page-grounded context
    4. Post-generation citation audit
    """
    # 1. Pre-query Fatwa Gate
    fatwa_guard = check_fatwa_sensitivity(question)
    if fatwa_guard:
        return fatwa_guard

    # 2. Retrieve relevant chunks
    relevant_chunks = search_index(
        query=question,
        index=index,
        chunks=chunks or [],
        top_k=top_k,
        filename_filter=filename_filter,
    )

    if isinstance(relevant_chunks, str) and "⚠️ 429" in relevant_chunks:
        return "⚠️ **Scholar Agent is currently resting.** Hidayah AI is receiving a high volume of requests. Please wait a moment and try again."

    if not relevant_chunks:
        return (
            "I could not find relevant information in the uploaded research document for your question. "
            "Please try rephrasing or searching for specific terms."
        )

    # 3. Build structured context with page numbers and document citations
    context_lines = []
    for i, chunk in enumerate(relevant_chunks):
        if isinstance(chunk, dict):
            page_num = chunk.get("page", 1)
            filename = chunk.get("filename", "document.pdf")
            score = chunk.get("relevance_score", "")
            score_str = f" | Relevance: {score}" if score else ""
            text = chunk.get("text", "")
            context_lines.append(f"[Excerpt {i+1} — {filename}, Page {page_num}{score_str}]\n{text}")
        else:
            context_lines.append(f"[Excerpt {i+1}]\n{str(chunk)}")

    context_str = "\n\n---\n\n".join(context_lines)

    prompt = f"""Based on the following excerpts from the uploaded document, answer the user's question accurately.

Document Context Excerpts:
{context_str}

---

User Question: {question}

Provide a concise, well-structured answer with specific page citations from the context."""

    # 4. Generate Answer via Local LLM or Gemini
    raw_answer = None

    if USE_LOCAL_LLM:
        raw_answer = _generate_local_llm(prompt, RAG_SYSTEM_PROMPT)

    if not raw_answer:
        client = get_gemini_client()
        if not client:
            return "⚠️ Gemini API key not configured. Please add GEMINI_API_KEY to your .env file."

        try:
            response = client.models.generate_content(
                model=MODEL_SCHOLAR,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=RAG_SYSTEM_PROMPT,
                    temperature=0.3,
                    max_output_tokens=2048,
                ),
            )
            raw_answer = response.text
        except genai.errors.APIError as e:
            if e.code == 429:
                return "⚠️ **Scholar Agent is currently resting.** Hidayah AI is receiving a high volume of requests. Please wait a moment and try again."
            return f"⚠️ **RAG API Error:** {str(e.message) if hasattr(e, 'message') else str(e)}"
        except Exception as e:
            return f"⚠️ **RAG query error:** An unexpected error occurred. Please try again."

    if not raw_answer:
        return "⚠️ Could not generate an answer from the document. Please try again."

    # 5. Post-generation Grounding & Citation Audit
    verified_answer = verify_grounded_citations(raw_answer, context_str)
    return verified_answer
