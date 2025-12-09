import os
import sys
import warnings
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Disable ChromaDB telemetry before any imports
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Filter out Python version warnings from Google AI
warnings.filterwarnings("ignore", category=FutureWarning, module="google.api_core")

from config import settings
from rag_pipeline import configure_llm
from api.routes import query, chat, documents, search, system


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events for the application.
    """
    # Startup: Initialize LLM
    try:
        configure_llm(settings.GENAI_API_KEY)
        print("✓ LLM configured successfully")
    except Exception as e:
        print(f"✗ Failed to configure LLM: {e}")
        sys.exit(1)

    # Check if vector store exists
    from api.dependencies import vector_service
    if vector_service.vectordb is None:
        print("⚠ Warning: Vector store not initialized. Upload documents and run /api/documents/process")
    else:
        print("✓ Vector store loaded successfully")

    yield

    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Querio - RAG API",
    description="""
    A powerful PDF-based Retrieval Augmented Generation (RAG) API.

    ## Features

    1. Query: Ask questions about your PDF documents
    2. Chat: Have conversations with context from your documents
    3. Documents: Upload, manage, and process PDF documents
    4. Search: Semantic search through your document collection
    5. Real-time: Fast responses with vector similarity search

    ## Getting Started

    1. Upload PDF documents using `/api/documents/upload`
    2. Process documents with `/api/documents/process`
    3. Start querying with `/api/query` or `/api/chat`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(query.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(system.router)


@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": "Querio RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
