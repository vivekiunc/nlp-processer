import json
import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv()

embeddings = AzureOpenAIEmbeddings(azure_deployment = "text-embedding-3-small", openai_api_version = "2023-05-15", azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT"), api_key = os.environ.get("AZURE_OPENAI_API_KEY"))
doct = []
with open("/Users/vivekindlamuri/rag_system/knowledge/knowledge_base.jsonl", "r", encoding = "utf-8") as f:
    for line in f:
        record = json.loads((line.strip()))
        docs = record.pop("text")
        meta_dict = record

        doc = Document(page_content = docs, metadata = meta_dict)
        doct.append(doc)

pdf_count = len(doct)
print(f"Loaded the {pdf_count} text chunks of data from JSONL for pdf")

with open("/Users/vivekindlamuri/rag_system/knowledge/knowledge_base1.jsonl", "r", encoding = "utf-8") as f:
    for line in f:
        record = json.loads((line.strip()))
        docs = record.pop("text")
        meta_dict = record

        doc = Document(page_content = docs, metadata = meta_dict)
        doct.append(doc)


text_count = len(doct) - pdf_count
print(f"Loaded the {text_count} text chunks of data from JSONL for text files")
print("Loaded all JSONL chunks")

vector_store = Chroma.from_documents(documents = doct,embedding = embeddings, persist_directory="./my_vector_db")
print(f"Converted text to vectors using AzureOpenAI and stored in Chroma DB")

    