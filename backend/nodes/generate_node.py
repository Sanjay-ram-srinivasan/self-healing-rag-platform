from backend.agents.answer_agent import generate_answer


def generate_node(state):

    answer = generate_answer(
        state["question"],
        state["context"]
    )

    return {
        **state,
        "answer": answer
    }