import hashlib
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from google import genai

from app.core.config import settings
from app.repositories import (
    PostgresDocumentChunkRepository,
    PostgresDocumentRepository,
    PostgresRiskDossierRepository,
)
from app.schemas.dossier import DocumentAnalysis
from app.services import create_embedding_provider, run_analysis_workflow

router = APIRouter(prefix="/analysis", tags=["analysis"])


def get_document_repo() -> PostgresDocumentRepository:
    if not settings.database_url:
        raise HTTPException(status_code=500, detail="Database URL is not configured.")
    return PostgresDocumentRepository(database_url=settings.database_url)


def get_chunk_repo() -> PostgresDocumentChunkRepository:
    if not settings.database_url:
        raise HTTPException(status_code=500, detail="Database URL is not configured.")
    return PostgresDocumentChunkRepository(database_url=settings.database_url)


def get_dossier_repo() -> PostgresRiskDossierRepository:
    if not settings.database_url:
        raise HTTPException(status_code=500, detail="Database URL is not configured.")
    return PostgresRiskDossierRepository(database_url=settings.database_url)


def get_gemini_client() -> genai.Client:
    if not settings.gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key is not configured.")
    return genai.Client(api_key=settings.gemini_api_key)


@router.post("/", response_model=DocumentAnalysis, status_code=status.HTTP_202_ACCEPTED)
async def upload_document_for_analysis(
    file: Annotated[UploadFile, File(...)],
    background_tasks: BackgroundTasks,
    document_repo: PostgresDocumentRepository = Depends(get_document_repo),
    chunk_repo: PostgresDocumentChunkRepository = Depends(get_chunk_repo),
    dossier_repo: PostgresRiskDossierRepository = Depends(get_dossier_repo),
    gemini_client: genai.Client = Depends(get_gemini_client),
):
    """
    Upload a contract PDF and start the async risk analysis workflow.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="File is empty.")

    content_sha256 = hashlib.sha256(file_bytes).hexdigest()

    # Create document tracking record synchronously
    document_id = await document_repo.create_document(
        original_filename=file.filename,
        content_sha256=content_sha256,
    )

    # Schedule background task to run the RAG and LLM pipeline
    embedding_provider = create_embedding_provider()

    background_tasks.add_task(
        run_analysis_workflow,
        document_id=document_id,
        original_filename=file.filename,
        file_bytes=file_bytes,
        document_repo=document_repo,
        chunk_repo=chunk_repo,
        dossier_repo=dossier_repo,
        embedding_provider=embedding_provider,
        gemini_client=gemini_client,
    )

    # Return pending status immediately
    analysis = await document_repo.get_document_analysis(document_id)
    if not analysis:
        raise HTTPException(
            status_code=500, detail="Failed to retrieve newly created document."
        )
    return analysis


@router.get("/{analysis_id}", response_model=DocumentAnalysis)
async def get_analysis_status(
    analysis_id: UUID,
    document_repo: PostgresDocumentRepository = Depends(get_document_repo),
):
    """
    Poll the status of an analysis.
    If completed, the returned object will contain the generated `dossier`.
    """
    analysis = await document_repo.get_document_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return analysis


@router.get("/", response_model=list[DocumentAnalysis])
async def list_analyses(
    document_repo: PostgresDocumentRepository = Depends(get_document_repo),
):
    """
    Fetch the history of all analysis jobs.
    """
    return await document_repo.get_all_documents()
