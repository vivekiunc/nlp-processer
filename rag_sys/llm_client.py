import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

CHAT_DEPLOYMENT = "gpt-4.1-mini"

llm = AzureChatOpenAI(
    azure_deployment=CHAT_DEPLOYMENT,
    openai_api_version="2023-05-15",
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
)


def translate(text: str, target_language: str) -> str:
    response = llm.invoke([
        SystemMessage(content=f"Translate the user's text into {target_language}. Reply with only the translation, nothing else — no quotes, no explanation."),
        HumanMessage(content=text),
    ])
    return response.content.strip()
