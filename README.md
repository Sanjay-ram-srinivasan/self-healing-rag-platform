# Self-Healing RAG Platform

A production-oriented Retrieval-Augmented Generation (RAG) platform designed to improve answer reliability through verification, query rewriting, retry mechanisms, confidence scoring, and source attribution.

The platform allows users to upload documents, build a searchable knowledge base, and interact with an AI assistant that retrieves relevant context before generating responses. Unlike traditional RAG systems, it incorporates self-healing mechanisms to reduce hallucinations and improve response quality.

## Overview

Self-Healing RAG combines document retrieval, large language models, and agent-based verification workflows to create a more reliable AI knowledge assistant.

The system supports multi-format document ingestion, semantic search, user authentication, analytics, and configurable AI behavior through a modern web interface.

## Key Features

* Multi-format document ingestion

  * PDF
  * DOCX
  * PPTX
  * TXT
  * CSV

* Semantic search using vector embeddings

* ChromaDB-powered document retrieval

* Agentic workflow built with LangGraph

* Verification and Critic Agents for response validation

* Query Rewriting and Retry Logic

* Confidence Scoring

* Source Citations

* Google Authentication with Firebase

* User-specific document isolation

* Analytics Dashboard

* Configurable AI and retrieval settings

## System Architecture

```text
Document Upload
      │
      ▼
Document Processing
      │
      ▼
Text Chunking
      │
      ▼
Embedding Generation
      │
      ▼
ChromaDB Vector Store
      │
      ▼
Context Retrieval
      │
      ▼
Answer Generation
      │
      ▼
Verification Agent
      │
      ▼
Critic Agent
      │
      ▼
Query Rewrite & Retry
      │
      ▼
Confidence Scoring
      │
      ▼
Final Response with Sources
```

## Technology Stack

### Backend

* FastAPI
* LangGraph
* Groq (Llama 3)
* ChromaDB
* HuggingFace Embeddings
* Python

### Frontend

* React
* Vite
* Tailwind CSS
* JavaScript

### Authentication

* Firebase Authentication
* Google OAuth

## Project Structure

```text
Self-Healing-RAG/
│
├── backend/
│   ├── agents/
│   ├── nodes/
│   ├── ingestion/
│   ├── vectorstore/
│   ├── app.py
│   └── graph.py
│
├── src/
│   ├── pages/
│   ├── components/
│   ├── services/
│   └── context/
│
├── data/
├── uploads/
├── requirements.txt
├── package.json
└── README.md
```

## Installation

### Clone the Repository

```bash
git clone https://github.com/Sanjay-ram-srinivasan/self-healing-rag-platform.git
cd self-healing-rag-platform
```

### Backend Setup

```bash
pip install -r requirements.txt
uvicorn backend.app:app --reload
```

### Frontend Setup

```bash
npm install
npm run dev
```

## Current Capabilities

* Upload and index documents
* Retrieve context from uploaded files
* Generate grounded answers
* Verify answer quality
* Rewrite queries when retrieval fails
* Track confidence scores
* Manage user authentication
* Monitor platform analytics

## Future Enhancements

* ChatGPT-style persistent chat history
* RAGAS evaluation metrics

  * Faithfulness
  * Context Precision
  * Context Recall
  * Answer Relevance
* OCR support for scanned documents
* Web Search Agent
* Multi-user document collections
* Docker deployment
* Cloud deployment and monitoring

## Author

Sanjay Ram S

B.Tech CSE (AI & ML)
VIT-AP University



## License

This project is intended for educational, research, and portfolio purposes.
