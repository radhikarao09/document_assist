from app.core.logging import get_logger
from app.schemas import RetrievedChunk

logger = get_logger(__name__)


class EvidenceAgent:
    """Independently merges and re-ranks evidence from retrieval branches."""

    def evaluate(
        self,
        semantic_results: list[RetrievedChunk],
        keyword_results: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        merged: dict[int, RetrievedChunk] = {}
        for result in semantic_results + keyword_results:
            existing = merged.get(result.chunk_id)
            if existing is None or result.score > existing.score:
                merged[result.chunk_id] = result

        evidence = sorted(merged.values(), key=lambda result: result.score, reverse=True)
        logger.info("Evidence Agent selected %d unique chunks", len(evidence))
        return evidence
