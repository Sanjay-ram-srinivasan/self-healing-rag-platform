from backend.evaluation import evaluate_rag_response

def evaluate_answer(question, context, answer):
    return evaluate_rag_response(question, context, answer)
