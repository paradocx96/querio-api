"""
Dependency injection for API services.
"""
from src.api.services import DocumentService, ChatSessionService, VectorStoreService

# Initialize services (singleton pattern)
document_service = DocumentService()
chat_service = ChatSessionService()
vector_service = VectorStoreService()
