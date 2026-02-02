# MongoDB Search Implementation Details

This document provides a detailed technical overview of how search is implemented in the RAG system, covering the three distinct search strategies available.

## Search Strategies Overview

| Feature | Traditional Search ($text) | Atlas Search ($search) | Vector Search ($vectorSearch) |
| :--- | :--- | :--- | :--- |
| **Method** | Token matching | Full-text + Fuzzy | Semantic (Meaning) |
| **Ranking** | Word frequency (TF-IDF) | Advanced (BM25) | Cosine Similarity |
| **Fuzzy Support** | ❌ No | ✅ Yes (Max 2 edits) | ✅ Implicitly (Semantic) |
| **Requires Atlas** | ❌ No | ✅ Yes | ✅ Yes (for Atlas-managed) |
| **Metadata** | Text score | Highlights, Details | Vector Score |

---

## 1. Traditional Text Search (`$text`)

Uses MongoDB's native text index. This is the simplest and fastest way to search for exact keywords.

### Requirements
- A **Text Index** on the target field (e.g., `text`).
- In this project, indices are automatically ensured on startup in `app/main.py`.

### Implementation
```python
# app/database.py
pipeline = [
    { "$match": { "$text": { "$search": query_text } } },
    { "$addFields": { "score": { "$meta": "textScore" } } },
    { "$sort": { "score": { "$meta": "textScore" } } }
]
```

---

## 2. Atlas Search (`$search`)

Leverages the Lucene-powered engine in MongoDB Atlas for "Google-like" search capabilities.

### Key Features
- **Fuzzy Matching**: Handles typos automatically (controlled by `maxEdits`).
- **Highlighting**: Returns the exact snippet where the match occurred with `highlights`.
- **Score Details**: Provides a breakdown of why a document was ranked highly.

### Configuration (Atlas UI)
You must create an **Atlas Search Index** (Standard) on the collection. Default dynamic mapping works, but specific field mapping is recommended for production.

### Implementation
```python
# app/database.py
pipeline = [
    {
        "$search": {
            "index": "text_index",
            "text": {
                "query": query_text,
                "path": "text",
                "fuzzy": {"maxEdits": 1}
            },
            "scoreDetails": True,
            "highlight": { "path": "text" }
        }
    },
    {
        "$project": {
            "text": 1,
            "score": { "$meta": "searchScore" },
            "scoreDetails": { "$meta": "searchScoreDetails" },
            "highlights": { "$meta": "searchHighlights" }
        }
    }
]
```

---

## 3. Vector Search (`$vectorSearch`)

The core of the RAG pipeline. It finds documents based on their semantic meaning rather than keywords.

### How it works
1.  **Embedding**: The query is converted into a 1536-dimensional vector using Gemini (`text-embedding-004`).
2.  **K-Nearest Neighbors (kNN)**: MongoDB finds vectors closest to the query vector in the 1536D space using the HNSW (Hierarchical Navigable Small Worlds) algorithm.

### Requirements
- **Vector Index**: A native MongoDB 8.0 vector index.
- **Data**: Documents must have a `vector` field populated with Gemini embeddings.

### Implementation
```python
# app/database.py
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "vector",
            "queryVector": query_vector,
            "numCandidates": 100,
            "limit": limit
        }
    },
    {
        "$project": {
            "text": 1,
            "score": { "$meta": "vectorSearchScore" }
        }
    }
]
```

### Explain Mode

The `explain=true` parameter provides deep insight into how MongoDB executed the vector search. This is useful for debugging index usage and performance.

#### Key Explain Fields:
- **`query.type`**: usually `WrappedKnnQuery` for ANN (Approximate Nearest Neighbor) searches.
- **`metadata.mongotVersion`**: The version of the search engine.
- **`metadata.lucene`**: Details about the underlying Lucene index, including `totalSegments` and `totalDocs`.
- **`stats`** (Optional): If verbosity is high, contains `millisElapsed` and `invocationCounts` for stages like `match` and `score`.

## API Endpoints

- `GET /search/text?query=...`
- `GET /search/atlas?query=...`
- `GET /search/vector?query=...&explain=true|false`

---
> [!TIP]
> Use **Atlas Search** when you want typo tolerance and highlighting. Use **Vector Search** when you want to find conceptually related information even if keywords don't match.
