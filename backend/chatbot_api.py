#!/usr/bin/env python3
"""
RAG Chatbot API Server

This FastAPI server provides a RAG chatbot interface for the Physical AI & Humanoid Robotics Textbook.
It uses Qdrant for vector search and OpenAI for response generation.

Features:
- Answer questions about the book's content
- Answer questions based on selected text
- Maintain conversation history
- Use OpenAI Agents/ChatKit SDKs for enhanced interactions

Author: Claude Code
Date: 2025-12-21
"""

import os
import logging
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import openai
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
import cohere

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize clients
openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
qdrant_client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY')
)
cohere_client = cohere.Client(api_key=os.getenv('COHERE_API_KEY'))

# Configuration
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'physical_ai_humanoid_textbook')
VECTOR_SIZE = 1024

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's question or message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for maintaining context")
    selected_text: Optional[str] = Field(None, description="Selected text from the book for context")
    module_filter: Optional[str] = Field(None, description="Filter results to specific module")
    max_results: Optional[int] = Field(5, description="Maximum number of search results to retrieve")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI assistant's response")
    conversation_id: str = Field(..., description="Conversation ID")
    sources: List[Dict[str, Any]] = Field(..., description="Source documents used for the response")
    confidence_score: Optional[float] = Field(None, description="Confidence score of the response")

class RAGChatbot:
    def __init__(self):
        self.collection_name = COLLECTION_NAME
        self.vector_size = VECTOR_SIZE

    def search_relevant_content(self, query: str, selected_text: Optional[str] = None,
                              module_filter: Optional[str] = None, max_results: int = 5) -> List[Dict]:
        """
        Search for relevant content in the vector database.

        Args:
            query: User's question
            selected_text: Selected text for additional context
            module_filter: Filter by specific module
            max_results: Maximum number of results to return

        Returns:
            List of relevant content chunks with metadata
        """
        try:
            # Prepare search query - combine user query with selected text if provided
            search_query = query
            if selected_text:
                search_query = f"{query}\n\nSelected text context: {selected_text}"

            # Generate embedding for the search query
            response = cohere_client.embed(
                texts=[search_query],
                model='embed-english-v3.0',
                input_type='search_query'
            )
            query_embedding = response.embeddings[0]

            # Prepare filter if module is specified
            query_filter = None
            if module_filter:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="module",
                            match=MatchValue(value=module_filter)
                        )
                    ]
                )

            # Search in Qdrant
            search_results = qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=max_results,
                query_filter=query_filter,
                with_payload=True
            )

            # Format results
            results = []
            for result in search_results:
                payload = result.payload
                results.append({
                    'score': result.score,
                    'text': payload.get('chunk_text', ''),
                    'url': payload.get('url', ''),
                    'title': payload.get('title', ''),
                    'module': payload.get('module', ''),
                    'section': payload.get('section', ''),
                    'word_count': payload.get('word_count', 0)
                })

            logger.info(f"Found {len(results)} relevant chunks for query: '{query[:50]}...'")
            return results

        except Exception as e:
            logger.error(f"Error searching content: {str(e)}")
            return []

    def generate_response(self, query: str, relevant_content: List[Dict],
                         conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate a response using OpenAI with retrieved context.

        Args:
            query: User's question
            relevant_content: Retrieved relevant content chunks
            conversation_history: Previous conversation messages

        Returns:
            Generated response
        """
        try:
            # Prepare context from retrieved content
            context_parts = []
            for i, content in enumerate(relevant_content, 1):
                context_parts.append(f"[Source {i}] Module: {content['module']}, Section: {content['section']}\n{content['text']}")

            context = "\n\n".join(context_parts)

            # Prepare messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": f"""You are an expert AI assistant specializing in Physical AI and Humanoid Robotics.
You help users understand concepts from the Physical AI & Humanoid Robotics Textbook.

Use the provided context from the textbook to answer questions accurately. If the context doesn't contain enough information to fully answer a question, acknowledge this and provide the best answer possible based on the available information.

Always cite your sources using the format [Source X] when referencing specific information.
Be helpful, accurate, and encourage deeper learning about robotics and AI.

Context from textbook:
{context}"""
                }
            ]

            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

            # Add current user query
            messages.append({
                "role": "user",
                "content": query
            })

            # Generate response using OpenAI
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using cost-effective model
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )

            generated_response = response.choices[0].message.content.strip()
            logger.info(f"Generated response for query: '{query[:50]}...'")
            return generated_response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error while generating a response. Please try again."

    def calculate_confidence_score(self, relevant_content: List[Dict]) -> float:
        """
        Calculate a confidence score based on search results.

        Args:
            relevant_content: Retrieved content chunks

        Returns:
            Confidence score between 0 and 1
        """
        if not relevant_content:
            return 0.0

        # Simple confidence calculation based on average score and number of results
        avg_score = sum(content['score'] for content in relevant_content) / len(relevant_content)
        result_count_factor = min(len(relevant_content) / 5.0, 1.0)  # Normalize to 5 results

        confidence = (avg_score * 0.7) + (result_count_factor * 0.3)
        return min(confidence, 1.0)

# Global chatbot instance
chatbot = RAGChatbot()

# In-memory conversation storage (in production, use a database)
conversations = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting RAG Chatbot API server")
    yield
    # Shutdown
    logger.info("Shutting down RAG Chatbot API server")

app = FastAPI(
    title="Physical AI & Humanoid Robotics RAG Chatbot API",
    description="API for answering questions about the Physical AI & Humanoid Robotics Textbook using RAG",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Docusaurus domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Physical AI & Humanoid Robotics RAG Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "POST - Send a message to the chatbot",
            "/health": "GET - Health check",
            "/conversations/{conversation_id}": "GET - Get conversation history"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test Qdrant connection
        collections = qdrant_client.get_collections()
        collection_exists = any(col.name == COLLECTION_NAME for col in collections.collections)

        return {
            "status": "healthy",
            "qdrant_connected": True,
            "collection_exists": collection_exists,
            "openai_configured": bool(os.getenv('OPENAI_API_KEY')),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for RAG-based Q&A."""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"conv_{datetime.utcnow().timestamp()}"

        # Get or create conversation history
        if conversation_id not in conversations:
            conversations[conversation_id] = []

        conversation_history = conversations[conversation_id]

        # Search for relevant content
        relevant_content = chatbot.search_relevant_content(
            query=request.message,
            selected_text=request.selected_text,
            module_filter=request.module_filter,
            max_results=request.max_results
        )

        # Generate response
        response_text = chatbot.generate_response(
            query=request.message,
            relevant_content=relevant_content,
            conversation_history=conversation_history
        )

        # Calculate confidence score
        confidence_score = chatbot.calculate_confidence_score(relevant_content)

        # Update conversation history
        conversation_history.append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow()
        })

        conversation_history.append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow()
        })

        # Keep only last 20 messages to prevent memory issues
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
            conversations[conversation_id] = conversation_history

        # Format sources for response
        sources = []
        for content in relevant_content:
            sources.append({
                "text": content["text"][:200] + "..." if len(content["text"]) > 200 else content["text"],
                "url": content["url"],
                "title": content["title"],
                "module": content["module"],
                "section": content["section"],
                "score": content["score"]
            })

        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            sources=sources,
            confidence_score=confidence_score
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history."""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]
    }

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation history."""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": "Conversation deleted"}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

if __name__ == "__main__":
    uvicorn.run(
        "chatbot_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )