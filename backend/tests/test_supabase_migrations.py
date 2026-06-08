from pathlib import Path


MIGRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "supabase"
    / "migrations"
    / "202606040001_create_rag_schema.sql"
)


def test_rag_schema_migration_defines_pgvector_tables() -> None:
    sql = MIGRATION_PATH.read_text(encoding="utf-8").lower()

    assert "create extension if not exists vector" in sql
    assert "create table public.documents" in sql
    assert "create table public.document_chunks" in sql
    assert "create table public.risk_dossiers" in sql
    assert "embedding extensions.vector(768) not null" in sql


def test_rag_schema_migration_adds_vector_similarity_index() -> None:
    sql = MIGRATION_PATH.read_text(encoding="utf-8").lower()

    assert "using ivfflat" in sql
    assert "extensions.vector_cosine_ops" in sql


def test_rag_schema_migration_enforces_dossier_json_arrays() -> None:
    sql = MIGRATION_PATH.read_text(encoding="utf-8").lower()

    assert "jsonb_typeof(findings) = 'array'" in sql
    assert "jsonb_typeof(technical_recommendations) = 'array'" in sql
