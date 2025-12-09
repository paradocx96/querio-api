from fastapi import APIRouter, HTTPException, Depends

from src.api.models import SearchRequest, SearchResponse, SearchResult, ErrorResponse
from src.api.services import VectorStoreService

router = APIRouter(prefix="/api/search", tags=["Search"])


# Dependency
def get_vector_service():
    from src.api.dependencies import vector_service
    return vector_service


@router.post("", response_model=SearchResponse, responses={500: {"model": ErrorResponse}})
async def search_documents(request: SearchRequest, vector_service: VectorStoreService = Depends(get_vector_service)):
    """
    Semantic search through documents without generating an answer.

    - **query**: Search query
    - **k**: Number of results to return (default: 5)
    """
    try:
        results = vector_service.search(request.query, k=request.k)

        return SearchResponse(
            query=request.query,
            results=[SearchResult(**r) for r in results],
            total=len(results)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/similar", response_model=SearchResponse)
async def find_similar(request: SearchRequest, vector_service: VectorStoreService = Depends(get_vector_service)):
    """
    Find similar content to the given query.

    - **query**: Reference text to find similar content
    - **k**: Number of similar results (default: 5)
    """
    try:
        results = vector_service.search(request.query, k=request.k)

        return SearchResponse(
            query=request.query,
            results=[SearchResult(**r) for r in results],
            total=len(results)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity search failed: {str(e)}")
