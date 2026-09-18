from app.core.logging import get_logger
from app.services.document_registry import DocumentIndex
from app.services.ingestion_service import IngestionService

logger = get_logger(__name__)


class DocumentProcessingAgent:
    """Owns document validation, extraction, chunking, and indexing."""

    def __init__(self, ingestion_service: IngestionService):
        self.ingestion_service = ingestion_service

    def process(self, filename: str, source) -> DocumentIndex:
        logger.info("Document Processing Agent processing %s", filename)
        return self.ingestion_service.ingest(filename, source)
