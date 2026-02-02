from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
import tempfile
from docling.document_converter import DocumentConverter
from scripts.chunking import get_docling_chunker, chunk_document, get_contextualized_text
from app.embedding import get_embedding
from app.database import MongoManager

router = APIRouter()
converter = DocumentConverter()

def sanitize_metadata(d):
    """Helper to sanitize dict values for MongoDB"""
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

def save_vector_chunks(doc, filename: str):
    """
    Chunks the document, generates embeddings, and saves to MongoDB.
    Returns the number of chunks processed.
    """
    mongo = MongoManager()
    if not mongo.connect():
        print("Failed to connect to MongoDB for chunking.")
        return 0

    try:
        print(f"Chunking document: {filename}")
        chunker = get_docling_chunker()
        chunks = list(chunk_document(doc, chunker))
        print(f"Found {len(chunks)} chunks.")

        # Ensure Vector Index exists (1536 for Gemini)
        mongo.create_vector_index(dimensions=1536)

        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...", end="\r")
            
            # Get context-enriched text for embedding
            enriched_text = get_contextualized_text(chunk, chunker)
            
            # Generate embedding using Gemini
            raw_vector = get_embedding(enriched_text)
            
            # Convert to BSON Binary vector for MongoDB 8.0
            vector = mongo.to_bson_vector(raw_vector)
            
            # Prepare metadata and sanitize
            metadata = chunk.meta.model_dump()
            sanitized_meta = sanitize_metadata(metadata)
            
            # Prepare data for MongoDB
            document_data = {
                "text": chunk.text,
                "enriched_text": enriched_text,
                "vector": vector,
                "metadata": sanitized_meta,
                "source": filename,
                "chunk_index": i
            }
            
            # Insert into MongoDB
            mongo.insert_chunk(document_data)
        
        print(f"\nSuccessfully indexed {len(chunks)} chunks from {filename} into MongoDB.")
        return len(chunks)
    except Exception as e:
        print(f"Error in save_vector_chunks: {e}")
        return 0
    finally:
        mongo.close()

@router.post("/convert")
async def convert_to_md(file: UploadFile = File(...)):
    """
    Receives a file from the frontend, prints its info, and converts it to markdown.
    """
    # Print data for now as requested
    print(f"Received file: {file.filename}")
    print(f"Content Type: {file.content_type}")
    
    # We can't easily get size without reading, but let's try to seek
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    print(f"File Size: {file_size} bytes")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, file.filename)
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            print(f"Starting conversion for {file.filename}...")
            result = converter.convert(temp_file_path)
            markdown_content = result.document.export_to_markdown()
            
            print(f"Conversion successful for {file.filename}")

            # NEW: Save chunks to vector database
            chunks_count = save_vector_chunks(result.document, file.filename)
            
            return {
                "message": "File processed successfully",
                "filename": file.filename,
                "markdown": markdown_content,
                "chunks_indexed": chunks_count
            }
        except Exception as e:
            print(f"Conversion failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
