from backend.vectorstore.chroma import get_vectorstore


def retrieve_documents(query, collection_id=None, user_id=None):
    db = get_vectorstore()
    
    search_kwargs = {}
    
    filters = []
    if user_id:
        filters.append({"user_id": user_id})
    if collection_id and collection_id != "all":
        filters.append({"collection_id": collection_id})
        
    if len(filters) == 1:
        search_kwargs["filter"] = filters[0]
    elif len(filters) > 1:
        search_kwargs["filter"] = {"$and": filters}

    try:
        scored_docs = db.similarity_search_with_relevance_scores(query, k=8, **search_kwargs)
        filtered_docs = [
            doc for doc, score in scored_docs
            if float(score or 0) >= 0.35
        ]
        if filtered_docs:
            return filtered_docs[:4]
    except Exception:
        pass

    try:
        docs = db.max_marginal_relevance_search(query, k=4, fetch_k=12, **search_kwargs)
        if docs:
            return docs
    except Exception:
        pass

    return db.similarity_search(query, k=3, **search_kwargs)
