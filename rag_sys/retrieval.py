import os
import re
from concurrent.futures import ThreadPoolExecutor
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from llm_client import translate

load_dotenv()

TELUGU_RE = re.compile(r"[ఀ-౿]")

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-small",
    openai_api_version="2023-05-15",
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
)

vector_store = Chroma(
    persist_directory="/Users/vivekindlamuri/rag_system/my_vector_db",
    embedding_function=embeddings,
)




def querier(query: str, top_k: int = 3):
    # The knowledge base mixes English and Telugu documents. A query embedded in only its
    # original language tends to match documents in that same language/script, even when a
    # differently-worded document in the other language is the more relevant match. Searching
    # with a translated variant of the query too, and merging results by score, bridges that gap.
    other_language = "English" if TELUGU_RE.search(query) else "Telugu"
    translated = translate(query, other_language)

    query_variants = [query]
    if translated.strip() and translated.strip() != query.strip():
        query_variants.append(translated)

    # Distance scores from different query embeddings aren't on a directly comparable scale, so
    # merging by raw score can let a mediocre same-language match crowd out the translated
    # variant's true hit. Interleaving round-robin across variants guarantees each one's best
    # matches make it into the final top_k instead of being outscored away.
    #
    # Each variant's search is an independent, blocking network call (embed + Chroma lookup), so
    # run them concurrently instead of waiting on one before starting the next.
    with ThreadPoolExecutor(max_workers=len(query_variants)) as pool:
        per_variant_results = list(pool.map(
            lambda q: vector_store.similarity_search_with_score(q, k=top_k),
            query_variants,
        ))

    seen = set()
    ranked_docs = []
    for round_idx in range(top_k):
        for variant_results in per_variant_results:
            if len(ranked_docs) >= top_k or round_idx >= len(variant_results):
                continue
            doc, _ = variant_results[round_idx]
            key = (doc.metadata.get("source"), doc.page_content)
            if key in seen:
                continue
            seen.add(key)
            ranked_docs.append(doc)

    retrieved_chunks = []
    for doc in ranked_docs:
        meta = doc.metadata
        retrieved_chunks.append({
            "text": doc.page_content,
            "crop": meta.get("crop"),
            "region": meta.get("region"),
            "language": meta.get("language"),
            "source": meta.get("source"),
            "topic": meta.get("topic"),
        })
    return retrieved_chunks


if __name__ == "__main__":
    query = input("What can I help you with? ")
    for chunk in querier(query):
        print(chunk)
