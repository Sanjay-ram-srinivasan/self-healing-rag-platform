from backend.vectorstore.chroma import get_vectorstore

def store_documents(chunks):
    db = get_vectorstore()

    db.add_documents(chunks)

    print("Documents stored successfully")