import json
from uuid import UUID

from google import genai
from google.genai import types
from langfuse import get_client, observe

from app.repositories.document_chunks import DocumentChunkRepository
from app.schemas.dossier import RiskDossier, RiskFinding
from app.services.analysis_prompt import LLMRiskDossierOutput, build_analysis_prompt
from app.services.embedding_provider import EmbeddingProvider


class DossierGenerationError(Exception):
    """Raised when there is a failure during the generation of the risk dossier."""


@observe(name="generate-risk-dossier", as_type="chain")
async def generate_risk_dossier(
    *,
    document_id: UUID,
    document_name: str,
    repository: DocumentChunkRepository,
    embedding_provider: EmbeddingProvider,
    gemini_client: genai.Client,
    model: str = "gemini-2.5-flash",
    limit: int = 15,
) -> RiskDossier:
    """
    Generates a RiskDossier by retrieving relevant document chunks from the repository,
    building an analysis prompt, and calling Gemini via JSON structured output.

    This function is wrapped with @observe() so the LLM call becomes a child span
    inside the parent 'analysis-workflow' trace in Langfuse.
    """
    langfuse = get_client()
    langfuse.update_current_span(
        metadata={
            "document_id": str(document_id),
            "document_name": document_name,
            "model": model,
            "chunk_limit": limit,
        }
    )

    # 1. Define the query used to find relevant chunks for the risk dossier
    search_query = (
        "Identify legal, compliance, security, privacy, liability, "
        "and operational risks, indemnification, warranties, limitations of liability, "
        "intellectual property terms, and financial penalties."
    )

    # 2. Embed the query
    try:
        embeddings = await embedding_provider.embed_texts([search_query])
        query_embedding = embeddings[0]
    except Exception as e:
        raise DossierGenerationError(f"Failed to generate embedding for query: {e}")

    # 3. Retrieve relevant chunks
    try:
        chunks = await repository.get_relevant_chunks(
            document_id=document_id,
            query_embedding=query_embedding,
            limit=limit,
        )
    except Exception as e:
        raise DossierGenerationError(f"Failed to retrieve chunks: {e}")

    if not chunks:
        raise DossierGenerationError(f"No chunks found for document_id {document_id}.")

    # Combine chunks into a single text block
    combined_text = "\n\n---\n\n".join(chunks)

    # 4. Build prompt
    messages = build_analysis_prompt(combined_text)

    # 5. Call Gemini LLM with JSON structured output
    try:
        system_instruction = messages[0]["content"]
        user_message = messages[1]["content"]

        response = gemini_client.models.generate_content(
            model=model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=LLMRiskDossierOutput,
                temperature=0.0,
            ),
        )

        raw_text = response.text
        if not raw_text:
            raise DossierGenerationError("Gemini returned empty response.")

        parsed_data = json.loads(raw_text)
        llm_output = LLMRiskDossierOutput(**parsed_data)

    except DossierGenerationError:
        raise
    except Exception as e:
        raise DossierGenerationError(f"LLM generation failed: {e}")

    # 6. Map to Domain Entities
    findings = [
        RiskFinding(
            title=f.title,
            category=f.category,
            risk_level=f.risk_level,
            clause_reference=f.clause_reference,
            excerpt=f.excerpt,
            rationale=f.rationale,
            suggested_rewrite=f.suggested_rewrite,
            legal_basis=f.legal_basis,
            confidence_score=f.confidence_score,
        )
        for f in llm_output.findings
    ]

    return RiskDossier(
        document_id=document_id,
        document_name=document_name,
        executive_summary=llm_output.executive_summary,
        overall_risk_level=llm_output.overall_risk_level,
        findings=findings,
        technical_recommendations=llm_output.technical_recommendations,
    )
