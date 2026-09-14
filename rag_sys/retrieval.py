import os
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

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
    results = vector_store.similarity_search(query, k=top_k)
    retrieved_chunks = []
    for doc in results:
        meta = doc.metadata
        retrieved_chunks.append({
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
