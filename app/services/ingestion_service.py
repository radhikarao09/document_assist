import os
import shutil
from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.core.logging import get_logger
from app.services.document_registry import DocumentIndex, DocumentRegistry
from app.services.document_service import create_document_chunks, load_document_pages
from app.services.embedding_service import EmbeddingService

logger = get_logger(__name__)


class IngestionService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        registry: DocumentRegistry,
        upload_folder: str | None = None,
    ):
        self.embedding_service = embedding_service
        self.registry = registry
        self.upload_folder = Path(upload_folder or settings.upload_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)

    def ingest(self, filename: str, source) -> DocumentIndex:
        if not filename.lower().endswith(".pdf"):
            raise ValueError("Please select a PDF file.")

        safe_name = Path(filename).name
        destination = self.upload_folder / f"{uuid4().hex}_{safe_name}"
        try:
            with destination.open("wb") as buffer:
                shutil.copyfileobj(source, buffer)

            pages = load_document_pages(str(destination))
            chunks = create_document_chunks(pages)
            if not chunks:
                raise ValueError("The PDF did not contain extractable text.")

            embeddings = self.embedding_service.create_embeddings(
                [chunk.text for chunk in chunks]
            )
            document = DocumentIndex(
                filename=safe_name,
                path=os.fspath(destination),
                chunks=chunks,
                embeddings=embeddings,
            )
            self.registry.set_current(document)
            logger.info("Indexed document %s with %d chunks", safe_name, len(chunks))
            return document
        except Exception:
            destination.unlink(missing_ok=True)
            logger.exception("Document ingestion failed for %s", safe_name)
            raise
