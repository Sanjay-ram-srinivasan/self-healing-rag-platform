from backend.agents.rewriter_agent import rewrite_query


def rewrite_node(state):

    new_question = rewrite_query(
        state["question"]
    )

    attempts = state.get(
        "attempts",
        1
    )

    return {
        **state,
        "question": new_question,
        "attempts": attempts + 1
    }