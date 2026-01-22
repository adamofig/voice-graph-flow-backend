# RAG System Overiew

Welcome to the RAG (Retrieval-Augmented Generation) System documentation. This project aims to build a robust, high-performance RAG pipeline for processing unstructured documents and providing intelligent insights.

## Project Vision
The final system will be a full-scale RAG implementation using state-of-the-art tools:
- **Docling**: For high-quality data extraction from unstructured files (PDFs, etc.).
- **Gemini**: For generating high-dimensional embeddings (using `google-genai` SDK) and powering the LLM responses.
- **MongoDB 8**: Leveraging its new vector search capabilities for efficient storage and retrieval.

## Current Status
- PDF-to-Markdown conversion service (FastAPI + Docling).
- Gemini Embedding integration (`embedding.py` using `google-genai`).
- **Search Service**: Native keyword search ($text) and semantic vector search via the `/search` endpoint.
- **MongoDB Atlas & 8.0 Integration**: Flexible connection support and BSON-optimized vector storage (`database.py` and `index_document.py`).

## Documentation Index

- [Technical Reference: Docling Usage](file:///Users/adamo/Documents/Rag_system/docs/techinical-reference/docling.md) - Details on how we use Docling for document parsing.
- [Technical Reference: MongoDB Integration](file:///Users/adamo/Documents/Rag_system/docs/techinical-reference/mongodb.md) - Explains local vector search and BSON compression.
- [System Architecture](file:///Users/adamo/Documents/Rag_system/docs/techinical-reference/architecture.md) - Overview of the full RAG pipeline.
- [Project Roadmap](file:///Users/adamo/Documents/Rag_system/docs/roadmap.md) - Our path from conversion service to full RAG.

## Project Management

This project uses [uv](https://docs.astral.sh/uv/) for Python package management. `uv` is an extremely fast Python package installer and resolver, written in Rust.

### Adding Dependencies

To add new dependencies to the project, use the `uv add` command:

```bash
uv add <package-name>
```

For development dependencies:

```bash
uv add --dev <package-name>
```

## Getting Started

### Installation

1.  **Install uv** (if you haven't already):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
2.  **Install dependencies**:
    ```bash
    uv sync
    ```

### Running the Service

To run the current document conversion service:

```bash
uv run python main.py
```

Then send a POST request to `/convert` with a PDF file.

### Querying the System

To perform a search across your indexed documents:

```bash
# Keyword Search (Default)
curl "http://localhost:8000/search?query=full+stack&type=keyword"

# Semantic Search
curl "http://localhost:8000/search?query=AI+Engineer&type=semantic"
```

The system will return the most relevant chunks along with their source and metadata.

