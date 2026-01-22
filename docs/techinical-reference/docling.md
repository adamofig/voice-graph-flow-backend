# Docling Technical Reference

[Docling](https://github.com/DS4SD/docling) is the core engine used in this project for document parsing and extraction.

## Why Docling?
Docling excels at extracting structured information from unstructured sources like PDFs. It handles complex layouts, including tables and multi-column text, significantly better than standard PDF-to-text libraries.

## Implementation in this Project

The main entry point for document conversion is `main.py`.

### FastAPI Service
We expose a `/convert` endpoint that:
1. Receives an uploaded file (`UploadFile`).
2. Saves it to a temporary directory.
3. Uses `DocumentConverter` from `docling` to process the file.
4. Exports the result to Markdown format.

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert(temp_file_path)
markdown_content = result.document.export_to_markdown()
```

## Semantic Chunking

Following document conversion, we use Docling's native chunking capabilities to prepare the data for embedding and vector storage.

### HybridChunker
We utilize the `HybridChunker` class, which provides a balance between document hierarchy and token constraints:
- **Hierarchical**: It respects document structure (headings, lists, groups).
- **Token-Aware**: It ensures chunks stay within the maximum sequence length of the embedding model (defaulting to 512 tokens).
- **Enrichment**: The `contextualize()` method is used to prepend header hierarchies to each chunk.

### Why Contextualization?
In a standard RAG pipeline, a chunk like *"05/2022 - 01/2025"* has no meaning. By using `contextualize()`, Docling prepends the relevant headings (e.g., *"Instinto X > AI Engineer"*). 
*   **Search Benefit**: When a user queries "Where did Adamo work?", the vector search will match against the enriched text containing the company name, even if the company name isn't in the specific paragraph chunk.

### Understanding Metadata (Provenance)
Each chunk contains rich metadata that should be indexed alongside the embedding:
- **Headings**: The trail of titles leading to the content.
- **Page Number**: Useful for providing citations in AI responses.
- **Bounding Boxes (BBox)**: Exact coordinates on the page. This allows for features like highlighting the source text in a PDF viewer.

### Usage in Code
The logic is encapsulated in `chunking.py`:

```python
from docling.chunking import HybridChunker
from chunking import get_docling_chunker, chunk_document, get_contextualized_text

# 1. Initialize Chunker (matched to embedding model limits)
chunker = get_docling_chunker()

# 2. Process Document
chunks = chunk_document(doc, chunker)

# 3. Get Context-Enriched Text for Embedding
for chunk in chunks:
    # Use this for embedding creation
    enriched_text = get_contextualized_text(chunk, chunker)
    
    # Use this for storing in DB for later retrieval display
    original_text = chunk.text
    
    # Use this for citations/UI features
    page_number = chunk.meta.doc_items[0].prov[0].page_no
```

## Key Benefits
- **Layout Awareness**: Preserves the structural hierarchy of the document.
- **Contextualization**: Header paths are embedded with the content, improving retrieval accuracy.
- **Rich Metadata**: Provides provenance (page numbers, coordinates) for transparent AI responses.
- **Markdown Export**: Provides an LLM-friendly format out of the box.
