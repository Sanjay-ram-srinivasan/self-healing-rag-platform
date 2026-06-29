from backend.vectorstore.chroma import get_vectorstore

BATCH_SIZE = 64


def store_documents(chunks):
    db = get_vectorstore()

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        db.add_documents(batch)

    print("Documents stored successfully")
