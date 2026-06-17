from backend.ingestion.loader import load_pdf
from backend.ingestion.chunker import chunk_documents
from backend.ingestion.embeddings import store_documents

pdf_path = "data/langgraph.pdf"

documents = load_pdf(pdf_path)

chunks = chunk_documents(documents)

store_documents(chunks)

print("Ingestion Complete")