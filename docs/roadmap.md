# Project Roadmap

This roadmap outlines the journey from our current document conversion service to a full-featured RAG system.

## Phase 1: Foundation (Completed)
- [x] Basic FastAPI service implementation.
- [x] Docling integration for PDF to Markdown conversion.
- [x] Technical documentation setup.

## Phase 2: Knowledge Processing (Completed)
- [x] Integration with Google Gemini Embedding API (using `google-genai`).
- [x] Implementation of `get_embedding` function in `embedding.py`.
- [x] Implementation of a semantic chunking strategy using Docling's `HybridChunker`.
- [x] Implementation of `chunk_document` and `get_contextualized_text` in `chunking.py`.
- [ ] Local storage of processed chunks for testing.

## Phase 3: Vector Intelligence (Completed)
- [x] Setup of MongoDB 8 database.
- [x] Implementation of Vector Indexes in MongoDB.
- [x] Pipeline to save Markdown chunks and their Gemini embeddings into MongoDB.

## Phase 4: Intelligent Retrieval
- [ ] Development of the retrieval service using MongoDB Vector Search.
- [ ] Context injection logic for LLM prompts.
- [ ] Basic Q&A interface via API.

## Phase 5: Production & Polish
- [ ] Performance optimization of the indexing pipeline.
- [ ] Comprehensive testing suite for retrieval accuracy.
- [ ] User documentation for the final RAG interface.
