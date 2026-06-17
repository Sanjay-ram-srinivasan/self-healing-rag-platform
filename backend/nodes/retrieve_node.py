import os

from backend.agents.retriever import retrieve_documents


def retrieve_node(state):

    docs = retrieve_documents(
        state["question"],
        state.get("collection_id"),
        state.get("user_id")
    )

    context = "\n".join(
        [doc.page_content for doc in docs]
    )

    unique_sources = set()
    sources = []

    for doc in docs:

        raw_source = doc.metadata.get(
            "source",
            "unknown"
        )
        source = os.path.basename(str(raw_source)) if raw_source else "unknown"

        page = doc.metadata.get(
            "page",
            "N/A"
        )

        key = (source, page)

        if key not in unique_sources:

            unique_sources.add(key)

            sources.append({
                "source": source,
                "page": page
            })

    return {
        **state,
        "context": context,
        "sources": sources
    }
