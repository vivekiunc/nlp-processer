"""Bridges the FastAPI app to the rag_sys pipeline.

rag_sys modules use bare imports (e.g. `from retrieval import querier`), so they
only resolve when the rag_sys directory itself is on sys.path. We add it here
before importing, rather than touching rag_sys's import style.
"""
import sys
from pathlib import Path

RAG_SYS_DIR = Path(__file__).resolve().parent.parent / "rag_sys"
if str(RAG_SYS_DIR) not in sys.path:
    sys.path.insert(0, str(RAG_SYS_DIR))

from context import ASR_MODELS, DEFAULT_LANGUAGE, answer_query, transcribe  # noqa: E402
from retrieval import querier  # noqa: E402

__all__ = ["ASR_MODELS", "DEFAULT_LANGUAGE", "answer_query", "transcribe", "querier"]
