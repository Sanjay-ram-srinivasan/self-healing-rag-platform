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
You are an expert document question-answering assistant.

IMPORTANT RULES:

1. Answer ONLY using the provided context.
2. Use ALL relevant information from the context.
3. Combine information from multiple chunks when necessary.
4. Provide complete and detailed answers.
5. If the answer exists in the context, NEVER say "I don't know".
6. Only say "I don't know" when the information is completely absent from the context.
7. For descriptive questions, organize the answer using bullet points.
8. For educational topics, include:
   - Definition
   - Characteristics
   - Habitat (if available)
   - Reproduction (if available)
   - Examples (if available)
   - Other important details

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
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