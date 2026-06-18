from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

DB_PATH = "chroma_db"

# Load once when server starts
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"token": os.getenv("HF_TOKEN")}
)

vectorstore = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embedding_model
)

def get_vectorstore():
    return vectorstore