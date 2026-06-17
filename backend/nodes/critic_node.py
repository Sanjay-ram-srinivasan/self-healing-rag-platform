from backend.agents.critic_agent import evaluate_answer


def critic_node(state):

    evaluation = evaluate_answer(
        state["original_question"],
        state["context"],
        state["answer"]
    )

    return {
        **state,
        "grounded": evaluation["grounded"],
        "confidence": evaluation["confidence"],
        "faithfulness": evaluation["faithfulness"],
        "relevance": evaluation["relevance"],
        "precision": evaluation["precision"],
        "recall": evaluation["recall"],
        "reason": evaluation["reason"]
    }
