import re


GREETING_PATTERNS = {
    "hi",
    "hello",
    "hey",
    "hiya",
    "good morning",
    "good afternoon",
    "good evening",
}

SMALL_TALK_PATTERNS = {
    "how are you",
    "what's up",
    "whats up",
    "who are you",
    "how's it going",
    "hows it going",
    "how do you work",
    "tell me about yourself",
    "nice to meet you",
    "thank you",
    "thanks",
}

DOCUMENT_HINTS = {
    "document",
    "file",
    "pdf",
    "ppt",
    "pptx",
    "doc",
    "docx",
    "csv",
    "xlsx",
    "upload",
    "uploaded",
    "page",
    "chapter",
    "slide",
    "according to",
    "in the documents",
    "from the document",
    "summarize",
    "summary",
    "what does",
    "explain",
    "list",
    "compare",
}


def classify_query(question):
    normalized = _normalize(question)

    if normalized in GREETING_PATTERNS:
        return "Greeting"

    if normalized in SMALL_TALK_PATTERNS:
        return "Small Talk"

    if any(hint in normalized for hint in DOCUMENT_HINTS):
        return "Document Question"

    if len(normalized.split()) <= 3 and any(token in normalized for token in {"hi", "hey", "hello"}):
        return "Greeting"

    if any(phrase in normalized for phrase in SMALL_TALK_PATTERNS):
        return "Small Talk"

    return "Document Question"


def build_direct_response(category):
    if category == "Greeting":
        return "Hello! Ask me anything about the uploaded documents, and I'll help you find the relevant information."

    return "I'm here to help with questions about the uploaded documents. Ask about a file, topic, page, or summary whenever you're ready."


def _normalize(text):
    return re.sub(r"\s+", " ", text.strip().lower())
