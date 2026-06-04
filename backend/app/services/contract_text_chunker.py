from dataclasses import dataclass


class TextChunkingError(ValueError):
    """Raised when contract text cannot be chunked."""


@dataclass(frozen=True)
class ChunkingConfig:
    max_chunk_size: int = 1200
    overlap_size: int = 200
    min_chunk_size: int = 400

    def __post_init__(self) -> None:
        if self.max_chunk_size <= 0:
            raise TextChunkingError("max_chunk_size must be greater than zero.")
        if self.overlap_size < 0:
            raise TextChunkingError("overlap_size cannot be negative.")
        if self.overlap_size >= self.max_chunk_size:
            raise TextChunkingError("overlap_size must be smaller than max_chunk_size.")
        if self.min_chunk_size <= 0:
            raise TextChunkingError("min_chunk_size must be greater than zero.")
        if self.min_chunk_size > self.max_chunk_size:
            raise TextChunkingError("min_chunk_size cannot exceed max_chunk_size.")


@dataclass(frozen=True)
class TextChunk:
    index: int
    text: str
    start_char: int
    end_char: int


def chunk_contract_text(
    text: str,
    config: ChunkingConfig | None = None,
) -> list[TextChunk]:
    config = config or ChunkingConfig()
    normalized_text = normalize_contract_text(text)

    if not normalized_text:
        raise TextChunkingError("Cannot chunk empty contract text.")

    chunks: list[TextChunk] = []
    start = 0
    text_length = len(normalized_text)

    while start < text_length:
        target_end = min(start + config.max_chunk_size, text_length)
        end = _find_chunk_boundary(
            text=normalized_text,
            start=start,
            target_end=target_end,
            min_chunk_size=config.min_chunk_size,
        )
        chunk_text = normalized_text[start:end].strip()

        if chunk_text:
            chunks.append(
                TextChunk(
                    index=len(chunks),
                    text=chunk_text,
                    start_char=start,
                    end_char=end,
                )
            )

        if end >= text_length:
            break

        next_start = max(end - config.overlap_size, 0)
        if next_start <= start:
            next_start = end
        start = next_start

    return chunks


def normalize_contract_text(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    normalized_lines: list[str] = []
    previous_blank = False

    for line in lines:
        normalized_line = " ".join(line.strip().split())

        if not normalized_line:
            if not previous_blank:
                normalized_lines.append("")
            previous_blank = True
            continue

        normalized_lines.append(normalized_line)
        previous_blank = False

    return "\n".join(normalized_lines).strip()


def _find_chunk_boundary(
    text: str,
    start: int,
    target_end: int,
    min_chunk_size: int,
) -> int:
    if target_end >= len(text):
        return target_end

    min_end = min(start + min_chunk_size, target_end)
    search_area = text[min_end:target_end]

    for marker in ("\n\n", ". ", "; ", "\n", " "):
        relative_index = search_area.rfind(marker)
        if relative_index != -1:
            return min_end + relative_index + len(marker)

    return target_end
