from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

DB_PATH = "chroma_db"

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

def get_vectorstore():
    return Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding_model
    )