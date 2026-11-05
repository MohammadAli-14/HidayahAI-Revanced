"""
Hidayah AI — Scholar Agent API Routes
Provides Server-Sent Events (SSE) streaming and REST completions for the AI Scholar.
"""

from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import re

from sse_starlette.sse import EventSourceResponse

from agents.router import classify_intent_heuristic
from agents.scholar import (
    get_scholar_response,
    prepare_scholar_context,
    is_local_llm_active,
    stream_scholar_local,
    format_hadith_card,
    SCHOLAR_SYSTEM_PROMPT,
)
from utils.fiqh_kb import lookup_fiqh_topic, FIQH_KNOWLEDGE_BASE
from utils.config import (
    MODEL_SCHOLAR,
    get_gemini_client,
    USE_LOCAL_LLM,
    LOCAL_LLM_URL,
    LOCAL_LLM_MODEL,
)
from utils.logger import get_logger

log = get_logger("routes_scholar")
router = APIRouter(prefix="/scholar", tags=["Scholar"])


class ScholarQueryRequest(BaseModel):
    query: str
    intent: Optional[str] = None
    active_pdf_name: Optional[str] = None
    ayahs_context: Optional[List[Dict[str, Any]]] = None
    ayah_window: Optional[List[Dict[str, Any]]] = None
    tafseer_language: Optional[str] = "en"
    pdf_context: Optional[str] = None
    use_local_llm: Optional[bool] = None


def _parse_sources_from_content(content: str):
    """Parse out structured sources from the trailing Sources: block."""
    marker = "\n\nSources:\n"
    if marker not in content:
        return content, []

    answer, raw_sources = content.split(marker, 1)
    sources = []
    for line in raw_sources.splitlines():
        source_line = line.strip()
        if not source_line.startswith("- "):
            continue
        body = source_line[2:].strip()
        parsed = {
            "type": "source",
            "source": body,
            "label": body,
            "canonical": "verified" if "canonical:verified" in body else "unverified",
            "url": "",
        }
        if " — " in body:
            parts = [p.strip() for p in body.split(" — ")]
            if parts[-1].startswith("http"):
                parsed["url"] = parts[-1]
                parsed["label"] = " — ".join(parts[:-1]).strip()
        sources.append(parsed)

    return answer, sources


@router.post("/ask")
async def ask_scholar(req: ScholarQueryRequest):
    """
    Standard HTTP endpoint for the Scholar Agent.
    Runs complete Islamic guardrails, intent routing, and citation checking.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    intent = req.intent or classify_intent_heuristic(req.query, req.active_pdf_name)

    # Run blocking generation in thread pool
    full_response = await asyncio.to_thread(
        get_scholar_response,
        query=req.query,
        intent=intent,
        ayahs_context=req.ayahs_context,
        ayah_window=req.ayah_window,
        tafseer_language=req.tafseer_language or "en",
        pdf_context=req.pdf_context,
        use_local_llm=req.use_local_llm,
    )

    clean_answer, sources = _parse_sources_from_content(full_response)
    fiqh_topic = lookup_fiqh_topic(req.query)
    fiqh_matrix = {
        "title": fiqh_topic.get("title", ""),
        "classical_consensus": fiqh_topic.get("classical_consensus", ""),
        "schools": fiqh_topic.get("schools", {}),
        "adab_note": fiqh_topic.get("adab_note", ""),
    } if fiqh_topic else None

    return {
        "intent": intent,
        "answer": clean_answer,
        "sources": sources,
        "fiqh_matrix": fiqh_matrix,
        "raw_response": full_response,
    }


@router.post("/stream")
async def stream_scholar(req: ScholarQueryRequest, request: Request):
    """
    Server-Sent Events (SSE) streaming endpoint for the AI Scholar.
    Streams tokens in real time to the Next.js client for ultra-smooth UI updates.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    intent = req.intent or classify_intent_heuristic(req.query, req.active_pdf_name)

    async def event_generator():
        # Anti-buffering initial flush pad (forces proxy to send headers immediately)
        yield {
            "comment": " " * 1024,
        }

        # 1. Send metadata
        yield {
            "event": "meta",
            "data": json.dumps({"intent": intent, "status": "thinking"}),
        }

        # 2. Send live progress step
        engine_label = "Local HidayahLM 3B (Offline)" if req.use_local_llm else "Gemini 2.5 Flash"
        yield {
            "event": "progress",
            "data": json.dumps({"step": f"Consulting canonical Hadith & Quranic corpus ({engine_label})..."}),
        }
        await asyncio.sleep(0.01)

        # 3. Assemble context in thread pool
        bundle = await asyncio.to_thread(
            prepare_scholar_context,
            query=req.query,
            intent=intent,
            ayahs_context=req.ayahs_context,
            ayah_window=req.ayah_window,
            tafseer_language=req.tafseer_language or "en",
            pdf_context=req.pdf_context,
            use_local_llm=req.use_local_llm,
        )

        # 4. Fiqh matrix if matched
        if bundle.fiqh_topic:
            yield {
                "event": "fiqh_matrix",
                "data": json.dumps({
                    "fiqh_matrix": {
                        "title": bundle.fiqh_topic.get("title", ""),
                        "classical_consensus": bundle.fiqh_topic.get("classical_consensus", ""),
                        "schools": bundle.fiqh_topic.get("schools", {}),
                        "adab_note": bundle.fiqh_topic.get("adab_note", ""),
                    }
                }),
            }

        # 5. Format structured sources
        structured_sources = []
        for src_line in bundle.grounded_sources:
            parsed = {
                "type": "source",
                "source": src_line,
                "label": src_line,
                "canonical": "verified" if "canonical:verified" in src_line else "unverified",
                "url": "",
            }
            if " — " in src_line:
                parts = [p.strip() for p in src_line.split(" — ")]
                if parts[-1].startswith("http"):
                    parsed["url"] = parts[-1]
                    parsed["label"] = " — ".join(parts[:-1]).strip()
            structured_sources.append(parsed)

        # 6. Instant Fast-Path: Unauthentic Hadith, Direct Hadith Lookup, or Fatwa Advisory
        if bundle.fast_response:
            yield {
                "event": "sources",
                "data": json.dumps({"sources": structured_sources}),
            }
            clean_answer, parsed_sources = _parse_sources_from_content(bundle.fast_response)
            if parsed_sources and not structured_sources:
                structured_sources = parsed_sources
                yield {
                    "event": "sources",
                    "data": json.dumps({"sources": structured_sources}),
                }

            # Fast response token emission
            words = re.split(r"(\s+)", clean_answer)
            for i in range(0, len(words), 4):
                if await request.is_disconnected():
                    break
                chunk = "".join(words[i:i + 4])
                yield {
                    "event": "token",
                    "data": json.dumps({"token": chunk}),
                }
                await asyncio.sleep(0.01)

            yield {
                "event": "done",
                "data": json.dumps({"completed": True}),
            }
            return

        # 7. General Research Query: Send sources upfront so badges display immediately
        yield {
            "event": "sources",
            "data": json.dumps({"sources": structured_sources}),
        }

        # Stream advisory notice if sensitive
        if bundle.sensitivity_info.get("is_sensitive") and bundle.sensitivity_info.get("advisory_notice"):
            advisory = bundle.sensitivity_info["advisory_notice"] + "\n\n"
            yield {
                "event": "token",
                "data": json.dumps({"token": advisory}),
            }

        if bundle.hadith_ref and not bundle.is_direct_lookup:
            hadith_card = format_hadith_card(bundle.hadith_ref) + "\n\n### 📖 Scholarly Analysis\n\n"
            yield {
                "event": "token",
                "data": json.dumps({"token": hadith_card}),
            }

        # 8. True live streaming from Gemini or Local LLM
        client = get_gemini_client()
        local_active = bundle.local_active
        has_streamed_tokens = False

        if local_active:
            try:
                import threading
                local_queue = asyncio.Queue()
                loop = asyncio.get_running_loop()

                def _local_worker():
                    try:
                        for token in stream_scholar_local(bundle.full_prompt):
                            loop.call_soon_threadsafe(local_queue.put_nowait, token)
                        loop.call_soon_threadsafe(local_queue.put_nowait, None)
                    except Exception as exc:
                        log.warning(f"Local LLM streaming worker error: {exc}")
                        loop.call_soon_threadsafe(local_queue.put_nowait, exc)

                threading.Thread(target=_local_worker, daemon=True).start()

                t_start = loop.time()
                while True:
                    if await request.is_disconnected():
                        break
                    try:
                        item = await asyncio.wait_for(local_queue.get(), timeout=2.0)
                        if item is None:
                            break
                        if isinstance(item, Exception):
                            break
                        has_streamed_tokens = True
                        yield {
                            "event": "token",
                            "data": json.dumps({"token": item}),
                        }
                    except asyncio.TimeoutError:
                        elapsed = int(loop.time() - t_start)
                        # Keep-alive heartbeat comment so reverse proxy & browser never timeout
                        yield {
                            "comment": "keep-alive",
                        }
                        if not has_streamed_tokens:
                            if elapsed % 3 == 0 and elapsed > 0:
                                if elapsed < 8:
                                    step_desc = f"Loading HidayahLM 3B weights into memory ({elapsed}s)..."
                                elif elapsed < 32:
                                    step_desc = f"Evaluating scripture & Tafseer context on CPU ({elapsed}s)..."
                                else:
                                    step_desc = f"Synthesizing theological response ({elapsed}s)..."

                                yield {
                                    "event": "progress",
                                    "data": json.dumps({"step": step_desc}),
                                }
                            if elapsed >= 90:
                                log.warning(f"Local LLM exceeded 90s TTFT on CPU ({elapsed}s). Aborting to cloud failover.")
                                break
            except Exception as loc_err:
                log.warning(f"Local LLM streaming failed, falling back to Gemini: {loc_err}")

        # Automatic failover: If local model was not requested OR if local model failed/offline:
        if not has_streamed_tokens:
            if local_active:
                failover_notice = "> ℹ️ *Local HidayahLM 3B took too long or is offline (port 11434). Automatically switched to Gemini 2.5 Flash.*\n\n"
                yield {
                    "event": "token",
                    "data": json.dumps({"token": failover_notice}),
                }

            if client:
                try:
                    import threading
                    from google import genai
                    queue = asyncio.Queue()
                    loop = asyncio.get_running_loop()

                    def _worker():
                        try:
                            stream = client.models.generate_content_stream(
                                model=MODEL_SCHOLAR,
                                contents=bundle.full_prompt,
                                config=genai.types.GenerateContentConfig(
                                    system_instruction=SCHOLAR_SYSTEM_PROMPT,
                                    temperature=0.3,
                                    max_output_tokens=4096,
                                ),
                            )
                            for chunk in stream:
                                if chunk.text:
                                    loop.call_soon_threadsafe(queue.put_nowait, chunk.text)
                            loop.call_soon_threadsafe(queue.put_nowait, None)
                        except Exception as exc:
                            loop.call_soon_threadsafe(queue.put_nowait, exc)

                    threading.Thread(target=_worker, daemon=True).start()

                    t_gem_start = loop.time()
                    while True:
                        if await request.is_disconnected():
                            break
                        try:
                            item = await asyncio.wait_for(queue.get(), timeout=2.0)
                            if item is None:
                                break
                            if isinstance(item, Exception):
                                raise item
                            has_streamed_tokens = True
                            yield {
                                "event": "token",
                                "data": json.dumps({"token": item}),
                            }
                        except asyncio.TimeoutError:
                            yield {
                                "comment": "keep-alive",
                            }
                            if loop.time() - t_gem_start > 35.0:
                                break
                except Exception as e:
                    log.error(f"Gemini streaming error: {e}")
                    yield {
                        "event": "token",
                        "data": json.dumps({"token": f"\n\n⚠️ **Streaming notice:** Connection to model interrupted ({e})."}),
                    }
            else:
                yield {
                    "event": "token",
                    "data": json.dumps({"token": "⚠️ **Scholar Agent error:** Gemini client is not configured and local Ollama is offline."}),
                }

        yield {
            "event": "done",
            "data": json.dumps({"completed": True}),
        }

    headers = {
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
        "Content-Type": "text/event-stream",
    }
    return EventSourceResponse(event_generator(), headers=headers)


@router.get("/ollama-status")
async def get_ollama_status():
    """Check if local Ollama daemon is active and responsive on port 11434."""
    try:
        import requests
        base_url = LOCAL_LLM_URL.replace("/v1", "")
        resp = requests.get(f"{base_url}/api/tags", timeout=1.0)
        if resp.status_code == 200:
            models = [m.get("name") for m in resp.json().get("models", [])]
            return {"online": True, "models": models}
    except Exception:
        pass
    return {"online": False, "models": []}


@router.get("/fiqh-matrix")
async def get_fiqh_matrix(query: str = Query(..., description="Query on prayer, fasting, or jurisprudence topic")):
    """
    Return structured comparative jurisprudence (Fiqh al-Muqāran) across the 4 Sunni Madhhabs
    (Hanafi, Maliki, Shafi'i, Hanbali) with primary scriptural proofs and scholarly references.
    """
    topic = lookup_fiqh_topic(query)
    if topic:
        return {
            "matched": True,
            "title": topic.get("title", ""),
            "classical_consensus": topic.get("classical_consensus", ""),
            "schools": topic.get("schools", {}),
            "adab_note": topic.get("adab_note", ""),
        }

    available = [
        {"key": k, "title": v["title"]}
        for k, v in FIQH_KNOWLEDGE_BASE.items()
    ]
    return {
        "matched": False,
        "message": f"No direct 4-Madhhab pre-indexed matrix for '{query}'.",
        "available_topics": available,
    }

