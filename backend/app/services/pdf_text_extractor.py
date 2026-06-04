from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from pypdf import PdfReader
from pypdf.errors import FileNotDecryptedError, PdfReadError


class PdfTextExtractionError(Exception):
    """Raised when text cannot be extracted from a PDF."""


@dataclass(frozen=True)
class PdfPageText:
    page_number: int
    text: str


@dataclass(frozen=True)
class PdfTextExtractionResult:
    total_pages: int
    pages: list[PdfPageText]

    @property
    def text(self) -> str:
        return "\n\n".join(page.text for page in self.pages if page.text)


PdfSource = str | Path | BinaryIO


def extract_text_from_pdf(source: PdfSource) -> PdfTextExtractionResult:
    try:
        reader = PdfReader(source)
    except PdfReadError as exc:
        raise PdfTextExtractionError("The uploaded file is not a readable PDF.") from exc

    if reader.is_encrypted:
        try:
            decrypt_result = reader.decrypt("")
        except (FileNotDecryptedError, PdfReadError) as exc:
            raise PdfTextExtractionError("Encrypted PDFs are not supported yet.") from exc

        if decrypt_result == 0:
            raise PdfTextExtractionError("Encrypted PDFs are not supported yet.")

    pages = [
        PdfPageText(page_number=index, text=(page.extract_text() or "").strip())
        for index, page in enumerate(reader.pages, start=1)
    ]
    result = PdfTextExtractionResult(total_pages=len(reader.pages), pages=pages)

    if not result.text.strip():
        raise PdfTextExtractionError("No extractable text was found in the PDF.")

    return result
