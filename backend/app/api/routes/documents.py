from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.dependencies import ServiceContainer, get_container
from app.schemas import DocumentDetail

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentDetail])
async def list_documents(container: ServiceContainer = Depends(get_container)) -> list[DocumentDetail]:
    return container.document_repository.list_documents()


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: str,
    container: ServiceContainer = Depends(get_container),
) -> DocumentDetail:
    document = container.document_repository.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return document


@router.post("/upload", response_model=DocumentDetail, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    container: ServiceContainer = Depends(get_container),
) -> DocumentDetail:
    try:
        return await container.ingestion_service.ingest_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
