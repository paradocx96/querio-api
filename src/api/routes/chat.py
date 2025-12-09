import time
from typing import List

from fastapi import APIRouter, HTTPException, Depends

from src.api.models import (ChatRequest, ChatResponse, ChatSession, ChatHistory, ErrorResponse)
from src.api.services import ChatSessionService, VectorStoreService

router = APIRouter(prefix="/api/chat", tags=["Chat"])


# Dependencies
def get_chat_service():
    from src.api.dependencies import chat_service
    return chat_service


def get_vector_service():
    from src.api.dependencies import vector_service
    return vector_service


@router.post("", response_model=ChatResponse, responses={500: {"model": ErrorResponse}})
async def chat(request: ChatRequest, chat_service: ChatSessionService = Depends(get_chat_service),
               vector_service: VectorStoreService = Depends(get_vector_service)):
    """
    Send a message in a chat session.

    - **message**: User's message
    - **session_id**: Optional session ID (creates new if not provided)
    - **k**: Number of context documents to use (default: 3)
    """
    try:
        start_time = time.time()

        # Create or get a session
        session_id = request.session_id
        if not session_id:
            session_id = chat_service.create_session()
        elif not chat_service.get_session(session_id):
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Add a user message to the history
        chat_service.add_message(session_id, "user", request.message)

        # Get answer from vector store
        answer = vector_service.query(request.message, k=request.k)

        # Add assistant response to history
        chat_service.add_message(session_id, "assistant", answer)

        # Get source documents
        sources = vector_service.search(request.message, k=request.k)

        processing_time = time.time() - start_time

        return ChatResponse(
            session_id=session_id,
            message=request.message,
            answer=answer,
            sources=sources,
            processing_time=processing_time
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/sessions", response_model=List[ChatSession])
async def list_sessions(chat_service: ChatSessionService = Depends(get_chat_service)):
    """
    List all chat sessions
    """
    return chat_service.list_sessions()


@router.post("/sessions", response_model=ChatSession)
async def create_session(chat_service: ChatSessionService = Depends(get_chat_service)):
    """
    Create a new chat session
    """

    session_id = chat_service.create_session()
    session = chat_service.get_session(session_id)

    return ChatSession(
        session_id=session["session_id"],
        created_at=session["created_at"],
        updated_at=session["updated_at"],
        message_count=session["message_count"]
    )


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(session_id: str, chat_service: ChatSessionService = Depends(get_chat_service)):
    """
    Get a specific chat session
    """
    session = chat_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return ChatSession(
        session_id=session["session_id"],
        created_at=session["created_at"],
        updated_at=session["updated_at"],
        message_count=session["message_count"]
    )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, chat_service: ChatSessionService = Depends(get_chat_service)):
    """
    Delete a chat session
    """
    success = chat_service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return {"success": True, "message": f"Session {session_id} deleted"}


@router.get("/sessions/{session_id}/history", response_model=ChatHistory)
async def get_session_history(session_id: str, chat_service: ChatSessionService = Depends(get_chat_service)):
    """
    Get conversation history for a session
    """
    history = chat_service.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return ChatHistory(**history)
