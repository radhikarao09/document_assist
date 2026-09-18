# Document Assistant

An AI-powered Document Assistant that allows users to upload PDF documents and ask questions about their content.

## Features

- Upload PDF documents through a simple web interface
- Ask natural-language questions about the document
- Retrieve relevant information from the uploaded PDF
- Generate answers using an LLM
- Supports general questions, summaries, key topics, and explanations

## Technologies Used

- Python
- FastAPI
- OpenAI API
- RAG (Retrieval-Augmented Generation)
- Embeddings
- Vector Search
- HTML, CSS, JavaScript

# Document Assistant

An AI-powered Document Assistant that preserves the existing browser workflow for uploading a machine-readable PDF and asking questions about it.

## Architecture

The application uses a Supervisor Agent and specialized agents orchestrated by LangGraph:

- **Supervisor Agent** coordinates the graph and decides when retrieval should be retried.
- **Document Processing Agent** validates, extracts, chunks, and indexes uploaded PDFs.
- **Query Agent** normalizes questions and classifies their intent.
- **Retrieval Agent** runs semantic and keyword retrieval strategies independently.
- **Evidence Agent** merges and re-ranks retrieved evidence before it reaches the LLM.
- **Answer Generation Agent** generates an answer using only approved document context.
- **Validation Agent** checks whether the answer is supported and can trigger a bounded retry.

Reusable behavior is centralized in `app/services/` for document processing, embeddings, vector search, LLM access, ingestion, and document state. FastAPI routes delegate to the application service and do not contain business logic.

## RAG Flow

```text
Upload PDF
	-> Document Processing Agent
	-> page-aware chunks and embeddings

Question
	-> Supervisor / LangGraph state
	-> Query Agent
	-> Semantic Retrieval Agent + Keyword Retrieval Agent (parallel)
	-> Evidence Agent
	-> Answer Generation Agent
	-> Validation Agent
	-> answer or bounded retrieval retry
```

LangGraph is used because the workflow has explicit typed state, parallel retrieval branches, conditional validation, and a retry path. It is more expressive than a fixed sequential function chain while keeping agent responsibilities visible.

## Project Structure

```text
app/
├── agents/       specialized agent responsibilities
├── api/          thin FastAPI routes
├── core/         settings, logging, and dependency container
├── schemas/      Pydantic request, evidence, and validation models
├── services/     reusable document, embedding, retrieval, and LLM services
└── workflow/     LangGraph state and orchestration
```

The older standalone RAG modules remain available for compatibility and reference, but new application behavior uses the centralized services and workflow.

## How to Run

1. Install dependencies with `pip install -r requirements.txt`.
2. Add `OPENAI_API_KEY` to `.env`.
3. Start the application with `uvicorn main:app --reload`.
4. Open `http://127.0.0.1:8000/`.

## Current PDF Limitation

The application supports PDFs with machine-readable or printed text. Handwritten or scanned image-only PDFs are not reliably supported because OCR is not currently included.
