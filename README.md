# 🚀 Self-Healing RAG Platform

> An Enterprise-Grade Agentic Retrieval-Augmented Generation (RAG) Platform designed to improve AI answer reliability through verification, self-correction, query rewriting, confidence scoring, and source attribution.

---

## 📖 Overview

Traditional Retrieval-Augmented Generation (RAG) systems often suffer from hallucinations, retrieval failures, and unreliable responses when relevant context is missing or incomplete.

The **Self-Healing RAG Platform** addresses these challenges by introducing an intelligent multi-agent workflow that continuously evaluates, verifies, and improves generated responses before presenting them to the user.

The platform allows users to upload documents, create a private knowledge base, and interact with an AI assistant capable of retrieving relevant information, validating responses, rewriting failed queries, and providing confidence scores with source citations.

Unlike conventional RAG systems, this platform incorporates **self-healing mechanisms** that significantly improve answer accuracy and trustworthiness.

---

# 🎯 Problem Statement

Large Language Models are powerful but often generate:

* Hallucinated responses
* Incorrect facts
* Unsupported claims
* Low-quality retrieval results
* Answers without transparency

Organizations require AI systems that are:

* Reliable
* Explainable
* Verifiable
* Traceable
* Scalable

This project was built to solve those challenges.

---

# ✨ Key Features

## 📄 Multi-Format Document Ingestion

Upload and index documents in multiple formats:

* PDF
* DOCX
* PPTX
* TXT
* CSV

---

## 🔍 Semantic Search

Uses vector embeddings for meaning-based retrieval instead of keyword matching.

Benefits:

* Better context retrieval
* Improved relevance
* Faster knowledge access

---

## 🧠 Agentic Self-Healing Workflow

Built using **LangGraph** to orchestrate multiple AI agents.

### Retrieval Agent

Retrieves relevant document chunks from ChromaDB.

### Answer Agent

Generates answers using retrieved context.

### Verification Agent

Checks whether the answer is grounded in the retrieved information.

### Critic Agent

Detects:

* Hallucinations
* Missing context
* Weak reasoning
* Unsupported claims

### Query Rewrite Agent

Automatically reformulates user questions when retrieval quality is poor.

---

## 🔄 Retry Mechanism

If retrieval or answer quality is insufficient:

1. Query is rewritten.
2. Retrieval is attempted again.
3. New answer is generated.
4. Verification is repeated.

This process improves reliability without requiring user intervention.

---

## 📊 Confidence Scoring

Every response receives a confidence score based on:

* Retrieval quality
* Verification results
* Critic evaluation
* Source grounding

Example:

```text
Confidence Score: 92%
Status: Verified
```

---

## 📚 Source Attribution

Every answer includes references to supporting document chunks.

Benefits:

* Transparency
* Explainability
* Trust

---

## 🔐 Authentication & Security

Integrated with Firebase Authentication.

Supported Login Methods:

* Google Sign-In
* Email Authentication

Features:

* Secure user authentication
* User-specific document isolation
* Protected APIs

---

## 📈 Analytics Dashboard

Monitor platform performance using:

* Total Queries
* Verified Responses
* Failed Responses
* Success Rate
* Confidence Trends
* Retrieval Performance

---

## ⚙️ Configurable AI Settings

Customize:

* Temperature
* Top-K Retrieval
* Retry Count
* Chunk Size
* Chunk Overlap
* Verification Threshold

---

# 🏗️ System Architecture

```text
                        ┌─────────────────┐
                        │ User Question   │
                        └────────┬────────┘
                                 │
                                 ▼
                      ┌─────────────────────┐
                      │ Retrieval Agent     │
                      └────────┬────────────┘
                               │
                               ▼
                    ┌───────────────────────┐
                    │ ChromaDB Vector Store │
                    └────────┬──────────────┘
                             │
                             ▼
                   ┌────────────────────────┐
                   │ Answer Generation Agent│
                   └────────┬───────────────┘
                            │
                            ▼
                  ┌──────────────────────────┐
                  │ Verification Agent       │
                  └────────┬─────────────────┘
                           │
                           ▼
                  ┌──────────────────────────┐
                  │ Critic Agent             │
                  └────────┬─────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
          Verified              Needs Retry
                │                     │
                ▼                     ▼
      Confidence Score      Query Rewrite Agent
                │                     │
                └──────────┬──────────┘
                           ▼
                  Final Response
                  + Source Citations
```

---

# 🛠️ Technology Stack

## Backend

* FastAPI
* LangGraph
* LangChain
* Groq API
* Llama 3 70B
* ChromaDB
* HuggingFace Embeddings
* Python

---

## Frontend

* React
* Vite
* Tailwind CSS
* JavaScript

---

## Authentication

* Firebase Authentication
* Google OAuth

---

## Vector Database

* ChromaDB

---

## Embedding Model

* sentence-transformers/all-MiniLM-L6-v2

---

# 📂 Project Structure

```text
Self-Healing-RAG/
│
├── backend/
│   │
│   ├── agents/
│   │   ├── answer_agent.py
│   │   ├── critic_agent.py
│   │   ├── retriever.py
│   │   └── rewriter_agent.py
│   │
│   ├── ingestion/
│   │   ├── document_loader.py
│   │   ├── chunker.py
│   │   └── embeddings.py
│   │
│   ├── nodes/
│   │   ├── retrieve_node.py
│   │   ├── generate_node.py
│   │   ├── critic_node.py
│   │   └── rewrite_node.py
│   │
│   ├── vectorstore/
│   │   └── chroma.py
│   │
│   ├── app.py
│   ├── auth.py
│   ├── analytics.py
│   └── graph.py
│
├── src/
│   ├── pages/
│   ├── components/
│   ├── services/
│   ├── context/
│   └── hooks/
│
├── uploads/
├── data/
├── chroma_db/
├── requirements.txt
├── package.json
└── README.md
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/Sanjay-ram-srinivasan/self-healing-rag-platform.git

cd self-healing-rag-platform
```

---

## Backend Setup

Create Virtual Environment

```bash
python -m venv .venv
```

Activate Environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / Mac

```bash
source .venv/bin/activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Run Backend

```bash
uvicorn backend.app:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger Docs:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

Install Packages

```bash
npm install
```

Run Frontend

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

# 🔄 Workflow

1. User uploads documents.
2. Documents are chunked.
3. Embeddings are generated.
4. Chunks are stored in ChromaDB.
5. User asks a question.
6. Retrieval Agent fetches context.
7. Answer Agent generates response.
8. Verification Agent validates grounding.
9. Critic Agent reviews answer quality.
10. Query Rewrite Agent retries if needed.
11. Confidence score is calculated.
12. Final answer is returned with sources.

---

# 📊 Current Capabilities

✅ Document Upload

✅ Semantic Search

✅ ChromaDB Retrieval

✅ Agentic Workflow

✅ Verification Pipeline

✅ Query Rewriting

✅ Confidence Scoring

✅ Source Attribution

✅ Firebase Authentication

✅ Analytics Dashboard

✅ Multi-Document Knowledge Base

---

# 🔮 Future Enhancements

## Advanced Evaluation

* RAGAS Integration
* Faithfulness
* Context Precision
* Context Recall
* Answer Relevance

---

## OCR Support

Extract text from:

* Scanned PDFs
* Images
* Handwritten Notes

---

## Web Search Agent

Combine:

* Internal Knowledge Base
* Real-Time Internet Search

---

## Persistent Conversations

ChatGPT-style:

* Session Memory
* Conversation History
* Context Retention

---

## Multi-Tenant Architecture

* Teams
* Organizations
* Shared Collections

---

# 🎓 Learning Outcomes

This project demonstrates practical experience with:

* Agentic AI Systems
* Retrieval-Augmented Generation
* LangGraph Workflows
* FastAPI Development
* Firebase Authentication
* Vector Databases
* Semantic Search
* LLM Evaluation
* AI Reliability Engineering
* Production AI Architecture

---

# 👨‍💻 Author

## Sanjay Ram S

B.Tech Computer Science Engineering (AI & ML)

Vellore Institute of Technology – Andhra Pradesh (VIT-AP)


---

# 📄 License

This project is developed for:

* Educational Purposes
* Research
* Portfolio Demonstration
* Learning and Experimentation

Feel free to fork, modify, and learn from this project.
