import os
import sys
from docling.document_converter import DocumentConverter
from chunking import get_docling_chunker, chunk_document, get_contextualized_text
from embedding import get_embedding
from database import MongoManager
from dotenv import load_dotenv

load_dotenv()

def index_pdf(file_path: str):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    # 1. Initialize MongoDB
    mongo = MongoManager()
    if not mongo.connect():
        print("Failed to connect to MongoDB. Exiting.")
        return

    try:
        # 2. Convert PDF to Docling document
        print(f"Converting {file_path}...")
        converter = DocumentConverter()
        result = converter.convert(file_path)
        doc = result.document

        # 3. Chunk the document
        print("Chunking document...")
        chunker = get_docling_chunker()
        chunks = list(chunk_document(doc, chunker))
        print(f"Found {len(chunks)} chunks.")

        # 4. Ensure Vector Index exists
        print("Ensuring vector index exists...")
        # Gemini embeddings are 768 dimensions (if using text-embedding-004)
        # Check if we need to adjust dimensions based on the actual vector length
        mongo.create_vector_index(dimensions=768)

        # 5. Process each chunk
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...", end="\r")
            
            # Get context-enriched text for embedding
            enriched_text = get_contextualized_text(chunk, chunker)
            
            # Generate embedding using Gemini
            raw_vector = get_embedding(enriched_text)
            
            # Convert to BSON Binary vector for MongoDB 8.0
            vector = mongo.to_bson_vector(raw_vector)
            
            # Prepare metadata and sanitize for MongoDB (handle potential large ints)
            metadata = chunk.meta.model_dump()
            
            # Helper to sanitize dict values for MongoDB
            def sanitize_metadata(d):
                if isinstance(d, dict):
                    return {k: sanitize_metadata(v) for k, v in d.items()}
                elif isinstance(d, list):
                    return [sanitize_metadata(v) for v in d]
                elif isinstance(d, int):
                    # MongoDB 8 supports Int64, but if it exceeds that, cast to string
                    if d > 9223372036854775807 or d < -9223372036854775808:
                        return str(d)
                    return d
                return d

            sanitized_meta = sanitize_metadata(metadata)
            
            # Prepare data for MongoDB
            document_data = {
                "text": chunk.text,
                "enriched_text": enriched_text,
                "vector": vector,
                "metadata": sanitized_meta,
                "source": os.path.basename(file_path),
                "chunk_index": i
            }
            
            # Insert into MongoDB
            mongo.insert_chunk(document_data)
        
        print(f"\nSuccessfully indexed {len(chunks)} chunks from {file_path} into MongoDB.")

    except Exception as e:
        print(f"\nAn error occurred during indexing: {e}")
    finally:
        mongo.close()

if __name__ == "__main__":
    pdf_file = "Adamo Resume Jan-2026.pdf"
    index_pdf(pdf_file)
