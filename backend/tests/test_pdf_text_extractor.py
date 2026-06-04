from io import BytesIO

import pytest
from pypdf import PdfWriter

from app.services.pdf_text_extractor import (
    PdfTextExtractionError,
    extract_text_from_pdf,
)


def make_pdf_bytes_with_text(lines: list[str]) -> bytes:
    content = "BT /F1 18 Tf 72 720 Td "
    content += " 0 -24 Td ".join(f"({line}) Tj" for line in lines)
    content += " ET"
    content_bytes = content.encode("ascii")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content_bytes)).encode("ascii") + b" >>\nstream\n"
        + content_bytes
        + b"\nendstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)


def test_extract_text_from_pdf_returns_pages_and_joined_text() -> None:
    pdf_file = BytesIO(
        make_pdf_bytes_with_text([
            "Contrato de API",
            "Clausula de retencao de dados",
        ])
    )

    result = extract_text_from_pdf(pdf_file)

    assert result.total_pages == 1
    assert result.pages[0].page_number == 1
    assert "Contrato de API" in result.text
    assert "Clausula de retencao de dados" in result.text


def test_extract_text_from_pdf_rejects_invalid_pdf() -> None:
    with pytest.raises(PdfTextExtractionError, match="not a readable PDF"):
        extract_text_from_pdf(BytesIO(b"not a pdf"))


def test_extract_text_from_pdf_rejects_pdf_without_text() -> None:
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.write(output)
    output.seek(0)

    with pytest.raises(PdfTextExtractionError, match="No extractable text"):
        extract_text_from_pdf(output)
