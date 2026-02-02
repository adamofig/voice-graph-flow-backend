import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from app.api.uploader import router as uploader_router
from app.api.search_api import router as search_router
from typing import Dict, List, Optional
from app.database import MongoManager
from app.embedding import get_embedding
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Docling & RAG API")

# Allow CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# converter = DocumentConverter()  # Moved to api/uploader.py
mongo = MongoManager()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@app.on_event("startup")
async def startup_db_client():
    if mongo.connect():
        # Ensure indices exist
        mongo.create_vector_index(dimensions=1536)
        mongo.create_text_index()
    else:
        print("Warning: Could not connect to MongoDB on startup.")

@app.on_event("shutdown")
async def shutdown_db_client():
    mongo.close()
    try:
        client.close()
    except:
        pass

# Include routers
app.include_router(uploader_router)
app.include_router(search_router)



@app.get("/llm")
async def ask_llm(
    query: str = Query(..., description="The query text for the LLM")
):
    """
    Get a response from the Gemini LLM for the given query text.
    """
    try:
        # Use the async client to generate content
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=query,
            config=types.GenerateContentConfig(
                temperature=0.7,
            )
        )
        
        return {
            "query": query,
            "response": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM request failed: {str(e)}")

@app.get("/llm-with-rag")
async def ask_llm_with_rag(
    query: str = Query(..., description="The query text for the RAG and LLM"),
    type: str = Query("keyword", enum=["keyword", "semantic"], description="Type of search to perform for context"),
    limit: int = Query(3, ge=1, le=10, description="Number of context documents to retrieve")
):
    """
    Combines search with Gemini LLM. 
    First retrieves relevant context from MongoDB, then sends it to the LLM.
    Defaults to keyword search as embeddings might have issues.
    """
    if mongo.db is None:
        if not mongo.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        # 1. Search for context based on type
        if type == "keyword":
            search_results = mongo.keyword_search(query, limit=limit)
        else:
            # Semantic search
            raw_vector = get_embedding(query)
            bson_vector = mongo.to_bson_vector(raw_vector)
            search_results = mongo.vector_search(bson_vector, limit=limit)
        
        # 2. Format context for LLM
        context_text = "\n\n".join([f"Source {i+1}:\n{res.get('text', '')}" for i, res in enumerate(search_results)])
        
        # 3. Construct the prompt with context
        prompt = f"""
You are a helpful assistant. Use the following context to answer the user's question. 
If the context doesn't contain the answer, say that you don't know based on the provided information, but try to be as helpful as possible with what is given.

Context:
{context_text}

Question: {query}
"""
        
        # 4. Get response from Gemini
        response = await client.aio.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
            )
        )
        
        # 5. Return combined results
        return {
            "query": query,
            "search_type": type,
            "results": search_results,
            "llm_response": response.text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG process failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "db_connected": mongo.db is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
