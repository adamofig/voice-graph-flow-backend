# RAG System & Docling Service

This project provides a robust Retrieval-Augmented Generation (RAG) backend. It features document conversion via [Docling](https://github.com/DS4SD/docling) and a searchable vector database powered by **MongoDB 8.0**.

## Setup with `uv`

This project uses [uv](https://docs.astral.sh/uv/) for fast, reliable Python package management.

### 1. Install uv
If you haven't already, install `uv`:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install dependencies
Sync the project dependencies and create a virtual environment:
```bash
uv sync
```

### 3. Environment Variables
Create a `.env` file with your credentials:
```env
MONGODB_URI=your_mongodb_connection_string
GEMINI_API_KEY=your_gemini_api_key
```

### 4. Run the API Service
Start the FastAPI server:
```bash
uv run python main.py
```
The service will start at `http://localhost:8000`.

## Key Features & Scripts

### Indexing Documents
To index a local PDF into MongoDB:
```bash
uv run python index_document.py
```

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
