from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# Query Models
class QueryRequest(BaseModel):
    query: str = Field(..., description="User's question or query", min_length=1)
    k: int = Field(default=3, description="Number of similar documents to retrieve", ge=1, le=10)


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[dict] = Field(default_factory=list, description="Source documents used")
    processing_time: Optional[float] = None


# Chat Models
class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message", min_length=1)
    session_id: Optional[str] = Field(None, description="Chat session ID")
    k: int = Field(default=3, description="Number of context documents", ge=1, le=10)


class ChatResponse(BaseModel):
    session_id: str
    message: str
    answer: str
    sources: List[dict] = Field(default_factory=list)
    processing_time: Optional[float] = None


class ChatSession(BaseModel):
    session_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ChatHistory(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime


# Document Models
class DocumentUpload(BaseModel):
    filename: str
    content_type: str = "application/pdf"


class DocumentMetadata(BaseModel):
    id: str
    filename: str
    file_size: int
    page_count: Optional[int] = None
    uploaded_at: datetime
    processed: bool = False


class DocumentList(BaseModel):
    documents: List[DocumentMetadata]
    total: int


class DocumentDeleteResponse(BaseModel):
    success: bool
    message: str
    document_id: str


# Search Models
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query", min_length=1)
    k: int = Field(default=5, description="Number of results", ge=1, le=20)


class SearchResult(BaseModel):
    content: str
    metadata: dict
    score: Optional[float] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int


# System Models
class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    vector_db_size: Optional[str] = None
    last_updated: Optional[datetime] = None


class RebuildRequest(BaseModel):
    force: bool = Field(default=False, description="Force rebuild even if up to date")


class RebuildResponse(BaseModel):
    success: bool
    message: str
    documents_processed: int
    chunks_created: int


# Error Models
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
