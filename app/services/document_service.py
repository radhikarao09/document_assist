from pathlib import Path

from pypdf import PdfReader

from app.schemas import DocumentChunk


def load_document(pdf_path: str) -> str:
    """Load machine-readable PDF text while tolerating empty pages."""
    return "\n".join(page_text for _, page_text in load_document_pages(pdf_path))


def load_document_pages(pdf_path: str) -> list[tuple[int, str]]:
    reader = PdfReader(Path(pdf_path))
    return [
        (page_number, page.extract_text() or "")
        for page_number, page in enumerate(reader.pages, start=1)
    ]


def create_chunks(text: str, chunk_size: int = 500) -> list[str]:
    """Preserve the original public helper for existing callers."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    return [text[index:index + chunk_size] for index in range(0, len(text), chunk_size)]


def create_document_chunks(
    pages: list[tuple[int, str]],
    chunk_size: int = 500,
) -> list[DocumentChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    chunks: list[DocumentChunk] = []
    chunk_id = 0
    for page_number, text in pages:
        for index in range(0, len(text), chunk_size):
            chunk_text = text[index:index + chunk_size].strip()
            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        text=chunk_text,
                        page_number=page_number,
                    )
                )
                chunk_id += 1
    return chunks