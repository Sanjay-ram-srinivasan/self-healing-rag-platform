import json
import os
import re

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)


def evaluate_rag_response(question, context, answer):
    prompt = f"""
You are a RAG evaluation system.

Score the answer using only the supplied question and retrieved context.
Return strict JSON only.

Question:
{question}

Retrieved Context:
{context}

Answer:
{answer}

Instructions:
1. faithfulness: How well the answer is supported by the retrieved context.
2. relevance: How directly the answer addresses the user's question.
3. precision: How precise and non-noisy the retrieved context is for this answer.
4. recall: How completely the retrieved context covers the information needed to answer.
5. grounded should be false if the answer includes unsupported factual claims.
6. confidence should be an overall confidence score for the answer quality and grounding.
7. reason should be a short explanation.

Return JSON in this exact shape:
{{
  "grounded": true,
  "confidence": 92,
  "faithfulness": 94,
  "relevance": 90,
  "precision": 88,
  "recall": 91,
  "reason": "Short explanation"
}}
"""

    response = llm.invoke(prompt)
    content = response.content

    try:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            return {
                "grounded": bool(parsed.get("grounded", False)),
                "confidence": _bounded_score(parsed.get("confidence", 0)),
                "faithfulness": _bounded_score(parsed.get("faithfulness", 0)),
                "relevance": _bounded_score(parsed.get("relevance", 0)),
                "precision": _bounded_score(parsed.get("precision", 0)),
                "recall": _bounded_score(parsed.get("recall", 0)),
                "reason": str(parsed.get("reason", "RAG evaluation completed")),
            }
    except Exception:
        pass

    return {
        "grounded": False,
        "confidence": 0,
        "faithfulness": 0,
        "relevance": 0,
        "precision": 0,
        "recall": 0,
        "reason": "RAG evaluation parsing failed",
    }


def _bounded_score(value):
    try:
        return max(0.0, min(100.0, float(value)))
    except (TypeError, ValueError):
        return 0.0
