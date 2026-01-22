# MongoDB Search & Integration

This document explains how the RAG System integrates with **MongoDB 8.0+** for efficient vector storage, semantic search, and native keyword search.

## Overview

The system uses MongoDB as a vector database to store document chunks and their corresponding embeddings. It leverages native vector search capabilities introduced in MongoDB to allow for fast, local similarity searches.

## Key Features

### 1. Native Vector Indexing
The system automatically initializes a native vector index on the `vectorData` collection. 
- **Algorithm**: HNSW (Hierarchical Navigable Small World)
- **Similarity Metric**: Cosine Similarity
- **Dimensions**: 768 (Optimized for Gemini `text-embedding-004`)

This index is created via the `MongoManager.create_vector_index()` method in `database.py`.

### 2. Native Keyword Search Indexing
The system also initializes a native MongoDB text index on the `text` field.
- **Field**: `text`
- **Algorithm**: Standard MongoDB text search weighting.

This index is created via `MongoManager.create_text_index()` and enables powerful keyword-based queries via the `$text` operator.

> [!IMPORTANT]
> For **MongoDB Atlas** users (especially on M0/Free tiers), native vector indices may need to be created manually through the Atlas UI or using the Atlas Search index syntax if the direct `createIndexes` command is restricted.

### 2. Flexible Connection & Atlas Support
The system is designed to connect to both local instances and **MongoDB Atlas** clusters.
- **URI Support**: Supports `mongodb+srv://` connection strings.
- **Automatic DB Selection**: `MongoManager` automatically extracts the database name from the connection URI if provided (e.g., `...mongodb.net/my_database`).
- **Connection Logic**: Handled in `database.py` using `MongoClient.get_default_database()`.

### 3. BSON Vector Compression
To optimize storage and performance, embeddings are converted from standard float arrays to **BSON Binary Format (Type 9)** before insertion.
- **Benefit**: Native support in MongoDB 8.0 for vectorized operations and optimized storage.
- **Implementation**: Handled by `MongoManager.to_bson_vector()` using `bson.binary.Binary.from_vector`.

## Data Schema

Each document in the `vectorData` collection follows this structure:

```json
{
  "text": "The raw chunk text...",
  "enriched_text": "Text contextualized with document metadata...",
  "vector": BinData(9, "AQID..."), 
  "metadata": {
    "page": 1,
    "section": "Introduction"
  },
  "source": "filename.pdf",
  "chunk_index": 0
}
```

### Vector Search (Semantic)

To perform a vector search locally, use the `$vectorSearch` aggregation stage:

```python
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "vector",
            "queryVector": <BSON_QUERY_VECTOR>,
            "numCandidates": 100,
            "limit": 5
        }
    }
]
results = collection.aggregate(pipeline)
```

> [!NOTE]
> Ensure you convert your query string to an embedding and then to BSON format before running the search.

### Keyword Search (Text)

To perform a keyword search, use the `$text` operator:

```python
pipeline = [
    {
        "$match": {
            "$text": {"$search": "your search query"}
        }
    },
    {
        "$sort": {"score": {"$meta": "textScore"}}
    }
]
results = collection.aggregate(pipeline)
```
