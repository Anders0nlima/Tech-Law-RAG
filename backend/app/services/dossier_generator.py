from uuid import UUID

from openai import AsyncOpenAI

from app.repositories.document_chunks import DocumentChunkRepository
from app.schemas.dossier import RiskDossier, RiskFinding
from app.services.analysis_prompt import LLMRiskDossierOutput, build_analysis_prompt
from app.services.embedding_provider import EmbeddingProvider


class DossierGenerationError(Exception):
    """Raised when there is a failure during the generation of the risk dossier."""


async def generate_risk_dossier(
    *,
    document_id: UUID,
    document_name: str,
    repository: DocumentChunkRepository,
    embedding_provider: EmbeddingProvider,
    openai_client: AsyncOpenAI,
    model: str = "gpt-4o-mini",
    limit: int = 15,
) -> RiskDossier:
    """
    Generates a RiskDossier by retrieving relevant document chunks from the repository,
    building an analysis prompt, and calling an LLM via structured outputs.
    """
    # 1. Define the query used to find relevant chunks for the risk dossier
    search_query = (
        "Identify legal, compliance, security, privacy, liability, "
        "and operational risks, indemnification, warranties, limitations of liability, "
        "intellectual property terms, and financial penalties."
    )

    # 2. Embed the query
    try:
        query_embedding = await embedding_provider.embed_text(search_query)
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

    # 5. Call LLM to parse structured output
    try:
        response = await openai_client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=LLMRiskDossierOutput,
            temperature=0.0,
        )
        llm_output = response.choices[0].message.parsed
        if not llm_output:
            raise DossierGenerationError("LLM returned empty parsed output.")
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
