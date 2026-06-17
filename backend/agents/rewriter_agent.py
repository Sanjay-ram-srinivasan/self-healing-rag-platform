import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)

def rewrite_query(query):

    prompt = f"""
    Rewrite this query
    to improve document retrieval.

    Query:
    {query}
    """

    response = llm.invoke(prompt)

    return response.content