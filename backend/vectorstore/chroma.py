from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import os

DB_PATH = "chroma_db"

def get_vectorstore():
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    return Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding_model
    )