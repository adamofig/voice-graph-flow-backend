from fastapi import APIRouter, HTTPException, Query
from app.database import MongoManager
from app.embedding import get_embedding
from typing import List, Dict, Any

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/text")
async def search_by_text(
    query: str = Query(..., description="The search query"),
    limit: int = Query(5, ge=1, le=20)
):
    """
    Traditional MongoDB text search using $text index.
    """
    mongo = MongoManager()
    if not mongo.connect():
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        results = mongo.keyword_search(query, limit=limit)
        return {
            "query": query,
            "type": "text",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text search failed: {str(e)}")
    finally:
        mongo.close()

@router.get("/atlas")
async def search_by_atlas(
    query: str = Query(..., description="The search query"),
    limit: int = Query(5, ge=1, le=20)
):
    """
    Atlas Search using $search operator (requires Atlas Search index).
    """
    print('Starting atlas search')
    mongo = MongoManager()
    if not mongo.connect():
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        results = mongo.atlas_search(query, limit=limit)
        return {
            "query": query,
            "type": "atlas",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Atlas search failed: {str(e)}")
    finally:
        mongo.close()

@router.get("/vector")
async def search_by_vector(
    query: str = Query(..., description="The search query"),
    limit: int = Query(5, ge=1, le=20),
    explain: bool = Query(False, description="Include execution statistics")
):
    """
    Vector search using embeddings and $vectorSearch.
    """
    mongo = MongoManager()
    if not mongo.connect():
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        # Generate embedding
        raw_vector = get_embedding(query)
        bson_vector = mongo.to_bson_vector(raw_vector)
        
        search_output = mongo.vector_search(bson_vector, limit=limit, include_explain=explain)
        
        if explain and isinstance(search_output, dict):
            return {
                "query": query,
                "type": "vector",
                "results": search_output.get("results"),
                "explain": search_output.get("explain")
            }
            
        return {
            "query": query,
            "type": "vector",
            "results": search_output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")
    finally:
        mongo.close()
