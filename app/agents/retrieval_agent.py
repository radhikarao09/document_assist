from app.core.logging import get_logger
from app.schemas import QueryPlan, RetrievedChunk
from app.services.document_registry import DocumentRegistry
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService

logger = get_logger(__name__)


class RetrievalAgent:
    """Runs independent semantic and lexical retrieval strategies."""

    def __init__(
        self,
        registry: DocumentRegistry,
        embedding_service: EmbeddingService,
        vector_service: VectorService,
    ):
        self.registry = registry
        self.embedding_service = embedding_service
        self.vector_service = vector_service

    def _document(self):
        document = self.registry.get_current()
        if document is None:
            raise ValueError("Please choose a PDF first.")
        return document

    def semantic(self, plan: QueryPlan) -> list[RetrievedChunk]:
        document = self._document()
        query_embedding = self.embedding_service.create_query_embedding(
            plan.normalized_question
        )
        results = self.vector_service.search(
            query_embedding,
            document.embeddings,
            document.chunks,
            top_k=plan.top_k,
            source="semantic",
        )
        logger.info("Semantic Retrieval Agent returned %d chunks", len(results))
        return results

    def keyword(self, plan: QueryPlan) -> list[RetrievedChunk]:
        document = self._document()
        results = self.vector_service.keyword_search(
            plan.normalized_question,
            document.chunks,
            top_k=plan.top_k,
        )
        logger.info("Keyword Retrieval Agent returned %d chunks", len(results))
        return results
