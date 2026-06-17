from typing import TypedDict


class GraphState(TypedDict):
    query_type: str
    original_question: str
    question: str
    context: str
    answer: str
    confidence: float
    faithfulness: float
    relevance: float
    precision: float
    recall: float
    grounded: bool
    reason: str
    attempts: int
    sources: list
    collection_id: str
    user_id: str
    search_source: str
