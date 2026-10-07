import logging
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

from app import rag
from app.schemas import (
    AudioQueryResponse,
    QueryRequest,
    QueryResponse,
    RetrievedChunk,
    RetrieveResponse,
)

logger = logging.getLogger("rag_api")

ALLOWED_AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}

app = FastAPI(title="Agri RAG API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    try:
        answer = rag.answer_query(request.query, request.top_k)
    except Exception:
        logger.exception("Failed to answer query")
        raise HTTPException(status_code=500, detail="Failed to generate an answer")
    return QueryResponse(answer=answer)


@app.post("/retrieve", response_model=RetrieveResponse)
def retrieve(request: QueryRequest):
    try:
        chunks = rag.querier(request.query, request.top_k)
    except Exception:
        logger.exception("Failed to retrieve chunks")
        raise HTTPException(status_code=500, detail="Failed to retrieve context")
    return RetrieveResponse(chunks=[RetrievedChunk(**c) for c in chunks])


@app.post("/audio-query", response_model=AudioQueryResponse)
async def audio_query(
    top_k: int = 3,
    language: str = rag.DEFAULT_LANGUAGE,
    file: UploadFile = File(...),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_AUDIO_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: {suffix or 'unknown'}",
        )
    if language not in rag.ASR_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {language!r}. Supported: {sorted(rag.ASR_MODELS)}",
        )

    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp.flush()
        try:
            # rag.transcribe/answer_query are blocking (model inference + network calls); run them
            # off the event loop so one in-flight audio request doesn't stall every other request.
            transcription = await run_in_threadpool(rag.transcribe, tmp.name, language)
            answer = await run_in_threadpool(rag.answer_query, transcription, top_k)
        except Exception:
            logger.exception("Failed to process audio query")
            raise HTTPException(status_code=500, detail="Failed to process audio")

    return AudioQueryResponse(transcription=transcription, answer=answer)
