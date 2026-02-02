import os
from docling.document_converter import DocumentConverter
from chunking import get_docling_chunker, chunk_document, get_contextualized_text

def test_chunking():
    source = "Adamo Resume Jan-2026.pdf"
    if not os.path.exists(source):
        print(f"Error: {source} not found.")
        return

    print(f"Converting {source}...")
    converter = DocumentConverter()
    result = converter.convert(source)
    doc = result.document

    print("Chunking document...")
    chunker = get_docling_chunker()
    chunks = list(chunk_document(doc, chunker))

    print(f"Found {len(chunks)} chunks.\n")

    for i, chunk in enumerate(chunks[:5]):  # Show first 5 chunks
        print(f"--- Chunk {i} ---")
        text = chunk.text
        enriched_text = get_contextualized_text(chunk, chunker)
        
        print(f"Original Text (first 100 chars): {text[:100]}...")
        print(f"Enriched Text (first 100 chars): {enriched_text[:100]}...")
        print(f"Metadata: {chunk.meta.model_dump()}\n")

if __name__ == "__main__":
    test_chunking()
