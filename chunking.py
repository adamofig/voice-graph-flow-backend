from typing import Iterator
from docling.chunking import HybridChunker
from docling_core.types.doc import DoclingDocument
from docling_core.transforms.chunker.base import BaseChunk

def get_docling_chunker(tokenizer_model: str = "sentence-transformers/all-MiniLM-L6-v2") -> HybridChunker:
    """
    Returns a configured HybridChunker instance.
    
    The HybridChunker balances document structure (headings, lists, etc.) 
    with token limits of the embedding model.
    
    Args:
        tokenizer_model (str): The name of the transformer model to use for tokenization.
                               Should match the embedding model being used.
    """
    return HybridChunker(tokenizer_model=tokenizer_model)

def chunk_document(doc: DoclingDocument, chunker: HybridChunker = None) -> Iterator[BaseChunk]:
    """
    Chunks a DoclingDocument using the provided chunker (or a default one).
    
    Args:
        doc (DoclingDocument): The document to chunk.
        chunker (HybridChunker, optional): An instance of HybridChunker.
    
    Yields:
        BaseChunk: Chunks of the document.
    """
    if chunker is None:
        chunker = get_docling_chunker()
    
    return chunker.chunk(dl_doc=doc)

def get_contextualized_text(chunk: BaseChunk, chunker: HybridChunker) -> str:
    """
    Returns the enriched text for a chunk, including context like parent headers.
    
    This is the text that should be sent to the embedding model.
    """
    return chunker.contextualize(chunk=chunk)

if __name__ == "__main__":
    # Example usage (dry run)
    print("Docling Chunking Utility Loaded.")
    print("Example usage:")
    print("1. Convert document: doc = DocumentConverter().convert(source).document")
    print("2. Chunk: chunks = chunk_document(doc)")
    print("3. Process: for chunk in chunks: text = get_contextualized_text(chunk, chunker)")
