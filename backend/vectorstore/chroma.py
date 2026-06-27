import sys
import logging

logger = logging.getLogger(__name__)

# Fallback/override for older SQLite versions on Linux (Chroma requires sqlite3 >= 3.35.0)
try:
    import sqlite3
    if sqlite3.sqlite_version_info < (3, 35, 0):
        try:
            import pysqlite3
            sys.modules["sqlite3"] = pysqlite3
            logger.info("[Chroma] Successfully patched sqlite3 with pysqlite3 for compatibility.")
        except ImportError:
            logger.warning("[Chroma] SQLite version %s is older than required (3.35.0) and pysqlite3 is not available. ChromaDB initialization may fail.", sqlite3.sqlite_version)
except ImportError:
    pass

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