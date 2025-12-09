import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import fitz

from src.config import settings
from src.pdf_handler import load_pdfs
from src.rag_pipeline import answer_query
from src.text_splitter import split_text
from src.vector_store import create_vectorstore


class DocumentService:
    """
    Service for managing PDF documents
    """

    def __init__(self):
        self.data_folder = Path(settings.PDF_FOLDER)
        self.data_folder.mkdir(exist_ok=True)
        self._documents_metadata: Dict[str, dict] = {}
        self._load_existing_documents()

    def _load_existing_documents(self):
        """
        Load metadata for existing documents
        """
        if not self.data_folder.exists():
            return

        for pdf_file in self.data_folder.glob("*.pdf"):
            doc_id = pdf_file.stem
            self._documents_metadata[doc_id] = {
                "id": doc_id,
                "filename": pdf_file.name,
                "file_size": pdf_file.stat().st_size,
                "uploaded_at": datetime.fromtimestamp(pdf_file.stat().st_ctime),
                "processed": True,
            }

    def upload_document(self, filename: str, content: bytes) -> dict:
        """
        Upload a new PDF document
        """
        # Generate unique ID
        doc_id = str(uuid.uuid4())

        # Save file
        file_path = self.data_folder / f"{doc_id}.pdf"
        with open(file_path, "wb") as f:
            f.write(content)

        # Extract metadata
        try:
            with fitz.open(file_path) as doc:
                page_count = len(doc)
        except Exception:
            page_count = None

        # Store metadata
        metadata = {
            "id": doc_id,
            "filename": filename,
            "file_size": len(content),
            "page_count": page_count,
            "uploaded_at": datetime.utcnow(),
            "processed": False,
        }
        self._documents_metadata[doc_id] = metadata

        return metadata

    def list_documents(self) -> List[dict]:
        """
        List all documents
        """
        return list(self._documents_metadata.values())

    def get_document(self, doc_id: str) -> Optional[dict]:
        """
        Get document metadata by ID
        """
        return self._documents_metadata.get(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document
        """
        if doc_id not in self._documents_metadata:
            return False

        # Delete file
        file_path = self.data_folder / f"{doc_id}.pdf"
        if file_path.exists():
            file_path.unlink()

        # Remove metadata
        del self._documents_metadata[doc_id]
        return True

    def process_documents(self) -> tuple:
        """
        Process all documents and create a vector store
        """
        text = load_pdfs(str(self.data_folder))
        chunks = split_text(text)

        # Mark all as processed
        for doc_id in self._documents_metadata:
            self._documents_metadata[doc_id]["processed"] = True

        return len(self._documents_metadata), len(chunks)


class ChatSessionService:
    """
    Service for managing chat sessions
    """

    def __init__(self):
        self._sessions: Dict[str, dict] = {}

    def create_session(self) -> str:
        """
        Create a new chat session
        """
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            "session_id": session_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "messages": [],
            "message_count": 0,
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        """
        Get session by ID
        """
        return self._sessions.get(session_id)

    def list_sessions(self) -> List[dict]:
        """
        List all sessions
        """
        return [
            {
                "session_id": s["session_id"],
                "created_at": s["created_at"],
                "updated_at": s["updated_at"],
                "message_count": s["message_count"],
            }
            for s in self._sessions.values()
        ]

    def add_message(self, session_id: str, role: str, content: str):
        """
        Add a message to a session
        """
        if session_id not in self._sessions:
            return False

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow(),
        }

        self._sessions[session_id]["messages"].append(message)
        self._sessions[session_id]["message_count"] += 1
        self._sessions[session_id]["updated_at"] = datetime.utcnow()

        return True

    def get_history(self, session_id: str) -> Optional[dict]:
        """
        Get chat history for the session
        """
        session = self._sessions.get(session_id)
        if not session:
            return None

        return {
            "session_id": session_id,
            "messages": session["messages"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
        }

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False


class VectorStoreService:
    """
    Service for managing vector store
    """

    def __init__(self):
        self.vectordb = None
        self._initialize()

    def _initialize(self):
        """
        Initialize or load vector store
        """
        db_path = Path(settings.CHROMA_DB)

        if db_path.exists() and any(db_path.iterdir()):
            # Load the existing vector store
            try:
                from langchain_chroma import Chroma
                from langchain_huggingface import HuggingFaceEmbeddings

                embedding_model = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )

                self.vectordb = Chroma(
                    embedding_function=embedding_model,
                    persist_directory=str(db_path)
                )
            except Exception:
                self.vectordb = None

    def rebuild(self, chunks: List[str]) -> bool:
        """
        Rebuild vector store with new chunks
        """
        try:
            self.vectordb = create_vectorstore(chunks, settings.CHROMA_DB)
            return True
        except Exception:
            return False

    def query(self, query_text: str, k: int = 3) -> str:
        """
        Query the vector store
        """
        if not self.vectordb:
            raise ValueError("Vector store not initialized")

        return answer_query(self.vectordb, query_text)

    def search(self, query_text: str, k: int = 5) -> List[dict]:
        """
        Semantic search without LLM
        """
        if not self.vectordb:
            raise ValueError("Vector store not initialized")

        docs = self.vectordb.similarity_search(query_text, k=k)

        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata if hasattr(doc, 'metadata') else {},
            }
            for doc in docs
        ]

    def get_stats(self) -> dict:
        """
        Get vector store statistics
        """
        db_path = Path(settings.CHROMA_DB)

        stats = {
            "total_chunks": 0,
            "db_size": "0 MB",
            "last_updated": None,
        }

        if db_path.exists():
            # Calculate directory size
            total_size = sum(f.stat().st_size for f in db_path.rglob('*') if f.is_file())
            stats["db_size"] = f"{total_size / (1024 * 1024):.2f} MB"

            # Get last modified time
            try:
                stats["last_updated"] = datetime.fromtimestamp(
                    max(f.stat().st_mtime for f in db_path.rglob('*') if f.is_file())
                )
            except Exception:
                pass

        return stats
