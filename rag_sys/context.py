import torch
from transformers import pipeline
from langchain_core.messages import SystemMessage, HumanMessage
from llm_client import llm
from retrieval import querier

MODEL_PATH = "/Users/vivekindlamuri/rag_system/models/telugu_whisper"
LANGUAGE_CODE = "te"

AGRI_SYSTEM_PROMPT = """You are a helpful agricultural assistant for farmers, especially those growing crops in Andhra Pradesh, India. Farmers may ask you questions in English or Telugu about crops, irrigation, pests, diseases, seed varieties, and related topics.

Always follow this order when answering a farmer's question:
1. First, carefully read the "Retrieved context" section below. It comes from a curated knowledge base of agricultural documents (government reports, research papers, extension guides).
2. If the retrieved context answers the question, base your answer on it and cite the source(s) using only the exact "Source:" names given in the retrieved context — never invent, guess, or embellish a document, institution, or program name that was not literally given to you.
3. If the retrieved context is missing or insufficient, fall back on your own general agricultural knowledge to fill the gap. In that case, do not cite any source at all — just say plainly that this part of the answer is from general knowledge, not the knowledge base.
4. Keep answers practical, concise, and actionable for a farmer, avoiding unnecessary jargon.
5. If neither the retrieved context nor your general knowledge is enough to answer confidently, say so honestly instead of guessing.
"""

if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

whisper_asr = pipeline(
    "automatic-speech-recognition",
    model=MODEL_PATH,
    device=device,
)

whisper_asr.model.config.forced_decoder_ids = (
    whisper_asr.tokenizer.get_decoder_prompt_ids(
        language=LANGUAGE_CODE, task="transcribe"
    )
)

def transcribe(audio_path: str) -> str:
    result = whisper_asr(audio_path)
    return result["text"]


def _drop_unverified_citations(answer: str, retrieved: list) -> str:
    known_sources = {c["source"] for c in retrieved if c.get("source")}
    kept_lines = [
        line for line in answer.splitlines()
        if "source" not in line.lower()
        or any(src in line for src in known_sources)
    ]
    return "\n".join(kept_lines).strip()


def answer_query(query: str, top_k: int = 3) -> str:
    retrieved = querier(query, top_k)

    if retrieved:
        context_block = "\n\n".join(
            f"[Source: {c['source']} | Topic: {c['topic']} | Region: {c['region']}]\n{c['text']}"
            for c in retrieved
        )
    else:
        context_block = "(No relevant documents found in the knowledge base.)"

    user_message = f"Retrieved context:\n{context_block}\n\nFarmer's question:\n{query}"

    response = llm.invoke([
        SystemMessage(content=AGRI_SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ])
    return _drop_unverified_citations(response.content, retrieved)


def transcribe_and_answer(audio_path: str, top_k: int = 3) -> str:
    query = transcribe(audio_path)
    print(f"Transcribed Telugu query: {query}")
    return answer_query(query, top_k)


if __name__ == "__main__":
    mode = input("Query by (t)ext or (a)udio? ").strip().lower()
    if mode == "a":
        audio_path = input("Path to Telugu audio file: ")
        answer = transcribe_and_answer(audio_path)
    else:
        query = input("What can I help you with? ")
        answer = answer_query(query)

    print(answer)
