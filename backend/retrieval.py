#!/usr/bin/env python3
"""
RAG Retrieval API for Physical AI & Humanoid Robotics Course

This FastAPI application provides an endpoint to query the Qdrant vector database
containing the Physical AI & Humanoid Robotics course content. It allows the RAG
chatbot to retrieve relevant information based on user queries.
"""

import os
import logging
from typing import List, Optional
from urllib.parse import urljoin
from datetime import datetime

import cohere
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Retrieval API",
    description="API for retrieving Physical AI & Humanoid Robotics course content from Qdrant vector database",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
cohere_api_key = os.getenv('COHERE_API_KEY')
qdrant_url = os.getenv('QDRANT_URL')
qdrant_api_key = os.getenv('QDRANT_API_KEY')
collection_name = os.getenv('COLLECTION_NAME', 'rag_embedding')

if not cohere_api_key:
    raise ValueError("COHERE_API_KEY environment variable is required")

cohere_client = cohere.Client(cohere_api_key)

if qdrant_url:
    qdrant_client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
        timeout=30
    )
else:
    # Use local Qdrant instance if no URL provided
    qdrant_client = QdrantClient(host='localhost', port=6333)


class Chunk(BaseModel):
    """Model for a content chunk returned by the retrieval API."""
    id: str
    text: str
    url: str
    title: str
    module: str
    section: str
    hierarchy_path: str
    word_count: int
    score: float
    created_at: str


class RetrievalResponse(BaseModel):
    """Model for the retrieval API response."""
    query: str
    results: List[Chunk]
    retrieved_count: int
    total_chunks: int
    execution_time: float


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "RAG Retrieval API"}


@app.get("/retrieve", response_model=RetrievalResponse)
def retrieve(
    query: str = Query(..., title="Query", description="The search query", min_length=1),
    k: int = Query(5, title="Number of results", description="Number of top results to return", ge=1, le=20),
    module_filter: Optional[str] = Query(None, title="Module filter", description="Filter results by module"),
    section_filter: Optional[str] = Query(None, title="Section filter", description="Filter results by section")
):
    """
    Retrieve relevant content chunks from the Qdrant database based on the query.

    Args:
        query: The search query
        k: Number of top results to return (default: 5, max: 20)
        module_filter: Optional filter to limit results to a specific module
        section_filter: Optional filter to limit results to a specific section

    Returns:
        RetrievalResponse: Contains the query, results, and metadata
    """
    try:
        import time
        start_time = time.time()

        # Generate embedding for the query
        response = cohere_client.embed(
            texts=[query],
            model='embed-english-v3.0',
            input_type='search_query'
        )

        query_embedding = response.embeddings[0]

        # Prepare search filters
        search_filter = models.Filter()
        if module_filter or section_filter:
            must_conditions = []

            if module_filter:
                must_conditions.append(
                    models.FieldCondition(
                        key="module",
                        match=models.MatchValue(value=module_filter)
                    )
                )

            if section_filter:
                must_conditions.append(
                    models.FieldCondition(
                        key="section",
                        match=models.MatchValue(value=section_filter)
                    )
                )

            if must_conditions:
                search_filter = models.Filter(must=must_conditions)

        # Search in Qdrant
        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=k,
            with_payload=True
        )

        # Convert results to our model
        chunks = []
        for result in search_results:
            payload = result.payload
            chunk = Chunk(
                id=result.id,
                text=payload.get('text', ''),
                url=payload.get('url', ''),
                title=payload.get('title', ''),
                module=payload.get('module', ''),
                section=payload.get('section', ''),
                hierarchy_path=payload.get('hierarchy_path', ''),
                word_count=payload.get('word_count', 0),
                score=result.score,
                created_at=payload.get('created_at', datetime.utcnow().isoformat())
            )
            chunks.append(chunk)

        # Get total number of chunks in collection
        collection_info = qdrant_client.get_collection(collection_name=collection_name)
        total_chunks = collection_info.points_count

        execution_time = time.time() - start_time

        response = RetrievalResponse(
            query=query,
            results=chunks,
            retrieved_count=len(chunks),
            total_chunks=total_chunks,
            execution_time=execution_time
        )

        logger.info(f"Retrieved {len(chunks)} results for query: '{query[:50]}...'")
        return response

    except Exception as e:
        logger.error(f"Error in retrieval: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


@app.get("/modules")
def get_modules():
    """
    Get a list of all available modules in the collection.
    """
    try:
        # Get all unique modules by searching with empty query and using scroll
        scroll_result = qdrant_client.scroll(
            collection_name=collection_name,
            limit=1000,  # Adjust as needed
            with_payload=['module']
        )

        modules = set()
        points, next_page = scroll_result

        for point in points:
            module = point.payload.get('module')
            if module:
                modules.add(module)

        # Continue scrolling if there are more results
        while next_page:
            scroll_result = qdrant_client.scroll(
                collection_name=collection_name,
                limit=1000,
                offset=next_page.offset,
                with_payload=['module']
            )
            points, next_page = scroll_result
            for point in points:
                module = point.payload.get('module')
                if module:
                    modules.add(module)

        return {"modules": sorted(list(modules))}
    except Exception as e:
        logger.error(f"Error getting modules: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get modules: {str(e)}")


@app.get("/health")
def health_check():
    """Detailed health check endpoint."""
    try:
        # Test Qdrant connection
        collections = qdrant_client.get_collections()
        collection_exists = any(col.name == collection_name for col in collections.collections)

        # Get collection info
        if collection_exists:
            collection_info = qdrant_client.get_collection(collection_name=collection_name)
            points_count = collection_info.points_count
        else:
            points_count = 0

        return {
            "status": "healthy",
            "service": "RAG Retrieval API",
            "qdrant_connected": True,
            "collection_exists": collection_exists,
            "collection_points": points_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "RAG Retrieval API",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "retrieval:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )