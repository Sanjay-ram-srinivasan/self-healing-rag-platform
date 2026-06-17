from langgraph.graph import (
    StateGraph,
    END
)

from backend.state import GraphState

from backend.nodes.retrieve_node import retrieve_node
from backend.nodes.generate_node import generate_node
from backend.nodes.critic_node import critic_node
from backend.nodes.rewrite_node import rewrite_node
from backend.nodes.web_search_node import web_search_node

def should_web_search(state):
    context = state.get("context", "")
    if not context.strip() or len(context.strip()) < 100:
        return "web_search"
    return "generate"


def should_retry(state):

    if (
        not state["grounded"]
        and state["attempts"] < 3
    ):
        return "rewrite"

    return END


workflow = StateGraph(GraphState)

workflow.add_node(
    "retrieve",
    retrieve_node
)

workflow.add_node(
    "generate",
    generate_node
)

workflow.add_node(
    "web_search",
    web_search_node
)

workflow.add_node(
    "critic",
    critic_node
)

workflow.add_node(
    "rewrite",
    rewrite_node
)

workflow.set_entry_point(
    "retrieve"
)

workflow.add_conditional_edges(
    "retrieve",
    should_web_search,
    {
        "web_search": "web_search",
        "generate": "generate"
    }
)

workflow.add_edge(
    "web_search",
    "generate"
)

workflow.add_edge(
    "generate",
    "critic"
)

workflow.add_conditional_edges(
    "critic",
    should_retry,
    {
        "rewrite": "rewrite",
        END: END
    }
)

workflow.add_edge(
    "rewrite",
    "retrieve"
)

graph = workflow.compile()


def run_self_healing_rag(question, query_type="Document Question", collection_id=None, user_id=None):

    result = graph.invoke({
        "query_type": query_type,
        "original_question": question,
        "question": question,
        "context": "",
        "answer": "",
        "confidence": 0,
        "faithfulness": 0,
        "relevance": 0,
        "precision": 0,
        "recall": 0,
        "grounded": False,
        "reason": "",
        "attempts": 1,
        "sources": [],
        "collection_id": collection_id,
        "user_id": user_id,
        "search_source": "Documents"
    })

    return {
        "answer": result["answer"],
        "confidence": result["confidence"],
        "faithfulness": result["faithfulness"],
        "relevance": result["relevance"],
        "precision": result["precision"],
        "recall": result["recall"],
        "grounded": result["grounded"],
        "reason": result["reason"],
        "attempts": result["attempts"],
        "sources": result["sources"],
        "search_source": result.get("search_source", "Documents")
    }
