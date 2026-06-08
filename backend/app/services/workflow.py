import logging
from uuid import UUID

from google import genai
from langfuse import get_client, observe

from app.repositories.document_chunks import DocumentChunkRepository
from app.repositories.documents import DocumentRepository
from app.repositories.risk_dossiers import RiskDossierRepository
from app.schemas.dossier import AnalysisStatus
from app.services.contract_text_chunker import ChunkingConfig, chunk_contract_text
from app.services.document_chunk_persistence import (
    PersistDocumentChunksCommand,
    persist_document_chunks,
)
from app.services.dossier_generator import generate_risk_dossier
from app.services.embedding_provider import EmbeddingProvider
from app.services.pdf_text_extractor import extract_text_from_pdf

logger = logging.getLogger(__name__)


@observe(name="analysis-workflow", as_type="agent")
async def run_analysis_workflow(
    *,
    document_id: UUID,
    original_filename: str,
    file_bytes: bytes,
    document_repo: DocumentRepository,
    chunk_repo: DocumentChunkRepository,
    dossier_repo: RiskDossierRepository,
    embedding_provider: EmbeddingProvider,
    gemini_client: genai.Client,
) -> None:
    """
    Background task to orchestrate the entire RAG and analysis pipeline.
    The @observe decorator creates a top-level Langfuse trace for each run.
    """
    langfuse = get_client()

    # Tag the trace with metadata visible in the Langfuse dashboard
    langfuse.update_current_span(
        metadata={
            "document_id": str(document_id),
            "document_name": original_filename,
        }
    )

    try:
        # 1. Mark as processing
        await document_repo.update_status(document_id, AnalysisStatus.PROCESSING)
        logger.info(f"Document {document_id}: Status set to PROCESSING.")

        # 2. Extract text
        import io
        pdf_extraction = extract_text_from_pdf(io.BytesIO(file_bytes))
        if not pdf_extraction.text.strip():
            raise ValueError("Extracted text is empty.")
        logger.info(f"Document {document_id}: Text extracted, {pdf_extraction.total_pages} pages.")

        # 3. Chunk text
        chunks = chunk_contract_text(
            pdf_extraction.text,
            ChunkingConfig(max_chunk_size=1000, overlap_size=200),
        )
        if not chunks:
            raise ValueError("Failed to create chunks from the extracted text.")
        logger.info(f"Document {document_id}: Text chunked into {len(chunks)} chunks.")

        # 4. Generate embeddings for each chunk
        texts_to_embed = [chunk.text for chunk in chunks]
        embeddings = await embedding_provider.embed_texts(texts_to_embed)
        logger.info(f"Document {document_id}: Generated {len(embeddings)} embeddings.")

        # 5. Persist chunks
        command = PersistDocumentChunksCommand(
            document_id=document_id,
            total_pages=pdf_extraction.total_pages,
            chunks=chunks,
            embeddings=embeddings,
        )
        await persist_document_chunks(command, chunk_repo)
        logger.info(f"Document {document_id}: Chunks persisted successfully.")

        # 6. Generate Risk Dossier (LLM call — instrumented inside generate_risk_dossier)
        dossier = await generate_risk_dossier(
            document_id=document_id,
            document_name=original_filename,
            repository=chunk_repo,
            embedding_provider=embedding_provider,
            gemini_client=gemini_client,
        )
        logger.info(f"Document {document_id}: Risk dossier generated.")

        # 7. Save Dossier
        await dossier_repo.save_dossier(dossier)
        logger.info(f"Document {document_id}: Risk dossier saved.")

        # 8. Mark as completed
        await document_repo.update_status(document_id, AnalysisStatus.COMPLETED)
        logger.info(f"Document {document_id}: Status set to COMPLETED.")

    except Exception as e:
        logger.exception(f"Analysis workflow failed for document {document_id}: {e}")
        langfuse.update_current_span(metadata={"error": str(e)})
        await document_repo.update_status(
            document_id, AnalysisStatus.FAILED, error_message=str(e)
        )
    finally:
        # Ensure all buffered events reach Langfuse before the background task exits
        langfuse.flush()
