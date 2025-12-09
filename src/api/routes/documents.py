from typing import List

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File

from src.api.models import (DocumentMetadata, DocumentList, DocumentDeleteResponse, RebuildRequest, RebuildResponse,
                            ErrorResponse)
from src.api.services import DocumentService, VectorStoreService
from src.pdf_handler import load_pdfs
from src.text_splitter import split_text

router = APIRouter(prefix="/api/documents", tags=["Documents"])


# Dependencies
def get_document_service():
    from src.api.dependencies import document_service
    return document_service


def get_vector_service():
    from src.api.dependencies import vector_service
    return vector_service


@router.post("/upload", response_model=DocumentMetadata, responses={500: {"model": ErrorResponse}})
async def upload_document(file: UploadFile = File(...),
                          document_service: DocumentService = Depends(get_document_service)):
    """
    Upload a PDF document.

    - **file**: PDF file to upload
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Read file content
        content = await file.read()

        # Upload document
        metadata = document_service.upload_document(file.filename, content)

        return DocumentMetadata(**metadata)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/bulk-upload", response_model=List[DocumentMetadata])
async def bulk_upload_documents(files: List[UploadFile] = File(...),
                                document_service: DocumentService = Depends(get_document_service)):
    """
    Upload multiple PDF documents.

    - **files**: List of PDF files to upload
    """
    uploaded_docs = []
    errors = []

    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            errors.append(f"{file.filename}: Not a PDF file")
            continue

        try:
            content = await file.read()
            metadata = document_service.upload_document(file.filename, content)
            uploaded_docs.append(DocumentMetadata(**metadata))
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    if errors and not uploaded_docs:
        raise HTTPException(status_code=500, detail=f"All uploads failed: {', '.join(errors)}")

    return uploaded_docs


@router.get("", response_model=DocumentList)
async def list_documents(document_service: DocumentService = Depends(get_document_service)):
    """
    List all uploaded documents
    """
    documents = document_service.list_documents()

    return DocumentList(
        documents=[DocumentMetadata(**doc) for doc in documents],
        total=len(documents)
    )


@router.get("/{document_id}", response_model=DocumentMetadata)
async def get_document(document_id: str, document_service: DocumentService = Depends(get_document_service)):
    """
    Get document metadata by ID
    """
    document = document_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

    return DocumentMetadata(**document)


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: str, document_service: DocumentService = Depends(get_document_service)):
    """
    Delete a document
    """
    success = document_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

    return DocumentDeleteResponse(
        success=True,
        message=f"Document {document_id} deleted successfully",
        document_id=document_id
    )


@router.post("/process", response_model=RebuildResponse)
async def process_documents(request: RebuildRequest = RebuildRequest(),
                            document_service: DocumentService = Depends(get_document_service),
                            vector_service: VectorStoreService = Depends(get_vector_service)):
    """
    Process all documents and rebuild the vector database.

    - **force**: Force rebuild even if already processed
    """
    try:
        # Process documents
        doc_count, chunk_count = document_service.process_documents()

        if chunk_count == 0:
            raise HTTPException(status_code=400, detail="No documents to process")

        # Rebuild vector store
        from src.config import settings
        text = load_pdfs(settings.PDF_FOLDER)
        chunks = split_text(text)
        success = vector_service.rebuild(chunks)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to rebuild vector store")

        return RebuildResponse(
            success=True,
            message="Documents processed and vector store rebuilt successfully",
            documents_processed=doc_count,
            chunks_created=len(chunks)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
