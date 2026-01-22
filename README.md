# RAG System & Docling Service

> [!NOTE]
> **Proof of Concept (PoC)**: This project is a quick demonstration of RAG (Retrieval-Augmented Generation) skills, integrating modern document conversion and vector search. It is intended as a technical showcase.

This project provides a robust RAG backend featuring document conversion via [Docling](https://github.com/DS4SD/docling) and a searchable vector database powered by **MongoDB 8.0**.

## Quick Start & Environment Setup

This project uses [uv](https://docs.astral.sh/uv/) for fast, reliable Python package and environment management.

### 1. Install uv
If you haven't already, install `uv`:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create the Environment & Install Dependencies
Sync the project to automatically create a virtual environment and install all required local dependencies:
```bash
uv sync
```
*Note: This will create a `.venv` directory in your project root.*

### 3. Configure Environment Variables
Create a `.env` file in the root directory to store your API keys and connection strings:
```env
MONGODB_URI=your_mongodb_connection_string
GEMINI_API_KEY=your_gemini_api_key
```

### 4. Run the API Service
Start the FastAPI server using `uv`:
```bash
uv run python main.py
```
The service will start at `http://localhost:8000`.

## Key Features & Scripts

### Indexing Documents
To index a local PDF into MongoDB for search:

```bash
# Ingest the default file (walmart relocation.pdf)
uv run python index_document.py

# Ingest a specific file
uv run python index_document.py path/to/your/document.pdf
```

The script will:
1. Connect to MongoDB using `MONGODB_URI`.
2. Convert the PDF to structured text using Docling.
3. Chunk the document.
4. Generate embeddings for each chunk using Google Gemini.
5. Store the chunks and vectors in the `vectorData` collection.

### API Endpoints

#### `GET /search`
Search across indexed documents.
- **Query Params**:
  - `query`: Your search team.
  - `type`: `keyword` (default) or `semantic`.
  - `limit`: Number of results (default: 5).

#### `POST /convert`
Upload a file to convert it to Markdown.
- **Body**: `file` (multipart/form-data)

#### `GET /health`
Check service and database status.

## Running with Docker

You can also run the service using Docker. The image uses a multi-stage build based on `python:3.12.7-slim-bookworm` and `uv`.

### 1. Build the Image
```bash
docker build -t rag-system .
```

### 2. Run the Container
Make sure you have a `.env` file in the current directory, or pass environment variables directly.
```bash
docker run -p 8080:8080 --env-file .env rag-system
```
The service will be available at `http://localhost:8080`.

## Documentation
For more details, see the [docs/](file:///Users/adamo/Documents/Rag_system/docs/index.md) directory.
