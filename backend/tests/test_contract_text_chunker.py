import pytest

from app.services import (
    ChunkingConfig,
    TextChunkingError,
    chunk_contract_text,
)
from app.services.contract_text_chunker import normalize_contract_text


def test_chunk_contract_text_returns_single_chunk_for_short_text() -> None:
    text = "Clausula 1. O fornecedor deve proteger os dados pessoais."

    chunks = chunk_contract_text(
        text,
        ChunkingConfig(max_chunk_size=200, overlap_size=40, min_chunk_size=80),
    )

    assert len(chunks) == 1
    assert chunks[0].index == 0
    assert chunks[0].text == text


def test_chunk_contract_text_splits_text_with_overlap() -> None:
    text = " ".join(f"palavra{i:03d}" for i in range(80))

    chunks = chunk_contract_text(
        text,
        ChunkingConfig(max_chunk_size=180, overlap_size=45, min_chunk_size=90),
    )

    assert len(chunks) > 1
    assert chunks[1].start_char < chunks[0].end_char
    assert chunks[0].end_char - chunks[1].start_char == 45
    assert all(len(chunk.text) <= 180 for chunk in chunks)


def test_chunk_contract_text_prefers_paragraph_boundary() -> None:
    first_paragraph = "A" * 80
    second_paragraph = "B" * 80
    text = f"{first_paragraph}\n\n{second_paragraph}"

    chunks = chunk_contract_text(
        text,
        ChunkingConfig(max_chunk_size=100, overlap_size=10, min_chunk_size=40),
    )

    assert chunks[0].text == first_paragraph


def test_normalize_contract_text_collapses_spaces_and_blank_lines() -> None:
    text = "  Clausula   1  \r\n\r\n\r\n  Dados    pessoais   "

    assert normalize_contract_text(text) == "Clausula 1\n\nDados pessoais"


def test_chunk_contract_text_rejects_empty_text() -> None:
    with pytest.raises(TextChunkingError, match="empty contract text"):
        chunk_contract_text("   \n\n   ")


def test_chunking_config_rejects_overlap_greater_than_chunk_size() -> None:
    with pytest.raises(TextChunkingError, match="smaller than max_chunk_size"):
        ChunkingConfig(max_chunk_size=100, overlap_size=100)
