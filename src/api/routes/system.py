from datetime import datetime

from fastapi import APIRouter, Depends

from src.api.models import HealthResponse, StatsResponse
from src.api.services import DocumentService, VectorStoreService

router = APIRouter(prefix="/api", tags=["System"])


# Dependencies
def get_document_service():
    from src.api.dependencies import document_service
    return document_service


def get_vector_service():
    from src.api.dependencies import vector_service
    return vector_service


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns the system status and version information.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow()
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(document_service: DocumentService = Depends(get_document_service),
                    vector_service: VectorStoreService = Depends(get_vector_service)):
    """
    Get system statistics.

    Returns information about documents, vector store, and system state.
    """
    documents = document_service.list_documents()
    vector_stats = vector_service.get_stats()

    return StatsResponse(
        total_documents=len(documents),
        total_chunks=vector_stats.get("total_chunks", 0),
        vector_db_size=vector_stats.get("db_size"),
        last_updated=vector_stats.get("last_updated")
    )
