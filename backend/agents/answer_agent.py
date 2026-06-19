import os
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

logger = logging.getLogger("performance")

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)

def generate_answer(question, context):

    if context:
        logger.info(f"[ANSWER] Context length: {len(context)} chars")
        logger.info(f"[ANSWER] Question: {question}")

        preview = context[:500].replace("\n", " ")
        logger.info(f"[ANSWER] Context Preview: {preview}")

    prompt = f"""
You are an expert Biology professor.

Answer ONLY from the provided context.

Instructions:
- Use ALL information available in the context.
- Combine information from multiple chunks.
- Do not say "I don't know" if relevant information exists in the context.
- If information is not present, simply omit that section.
- Provide a detailed and structured answer.
- Include:
  1. Definition
  2. Habitat
  3. Pigments
  4. Stored Food
  5. Cell Wall
  6. Reproduction
  7. Special Characteristics
  8. Summary

Context:
{context}

Question:
{question}

Detailed Answer:
"""

    try:
        response = llm.invoke(prompt)

        logger.info(
            f"[ANSWER] Generated response length: {len(response.content)} chars"
        )

        return response.content

    except Exception as e:
        logger.error(f"[ANSWER ERROR] {str(e)}")
        return "Unable to generate answer from the retrieved context."