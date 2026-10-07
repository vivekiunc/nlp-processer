"""Shared test setup.

rag_sys modules use bare imports (`from retrieval import querier`) and do real,
network-touching work at import time: they build an AzureOpenAIEmbeddings
client, open the Chroma persistent store, build an AzureChatOpenAI client, and
load a Whisper ASR model from disk. None of that should happen just to import
a module in a test process, so we put rag_sys on sys.path and stub those
heavy/networked dependencies *before* anything imports rag_sys or app code.

Individual tests then monkeypatch the specific call they care about
(`llm.invoke`, `vector_store.similarity_search_with_score`, `translate`, ...)
with controlled fake behavior.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parent.parent
RAG_SYS_DIR = ROOT / "rag_sys"

for path in (str(ROOT), str(RAG_SYS_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

sys.modules["transformers"] = MagicMock()
sys.modules["transformers"].pipeline = MagicMock(return_value=MagicMock())

fake_langchain_openai = MagicMock()
fake_langchain_openai.AzureOpenAIEmbeddings = MagicMock(return_value=MagicMock())
fake_langchain_openai.AzureChatOpenAI = MagicMock(return_value=MagicMock())
sys.modules["langchain_openai"] = fake_langchain_openai

fake_langchain_chroma = MagicMock()
fake_langchain_chroma.Chroma = MagicMock(return_value=MagicMock())
sys.modules["langchain_chroma"] = fake_langchain_chroma
