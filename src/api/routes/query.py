import time

from fastapi import APIRouter, HTTPException, Depends

from src.api.models import QueryRequest, QueryResponse, ErrorResponse
from src.api.services import VectorStoreService

router = APIRouter(prefix="/api", tags=["Query"])


# Dependency
def get_vector_service():
    from src.api.dependencies import vector_service
    return vector_service


@router.post("/query", response_model=QueryResponse, responses={500: {"model": ErrorResponse}})
async def query_documents(request: QueryRequest, vector_service: VectorStoreService = Depends(get_vector_service)):
    """
    Query the document knowledge base with a question.

    - **query**: The question to ask
    - **k**: Number of similar document chunks to use for context (default: 3)
    """
    try:
        start_time = time.time()

        # Get answer from vector store
        answer = vector_service.query(request.query, k=request.k)

        # Get source documents
        sources = vector_service.search(request.query, k=request.k)

        processing_time = time.time() - start_time

        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            processing_time=processing_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
