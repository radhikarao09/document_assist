from app.core.config import settings
from app.core.logging import get_logger
from app.schemas import QueryPlan

logger = get_logger(__name__)


class QueryAgent:
    """Classifies a question and creates a retrieval plan."""

    def analyze(self, question: str, retry_count: int = 0) -> QueryPlan:
        normalized = " ".join(question.split())
        lowered = normalized.lower()
        if any(word in lowered for word in ("summarize", "summary", "overview", "main")):
            question_type = "summary"
        elif "difference" in lowered or "compare" in lowered:
            question_type = "comparison"
        elif any(word in lowered for word in ("explain", "why", "how")):
            question_type = "explanation"
        else:
            question_type = "lookup"

        top_k = settings.retrieval_top_k + (2 if retry_count else 0)
        logger.info("Query Agent classified question as %s", question_type)
        return QueryPlan(
            normalized_question=normalized,
            question_type=question_type,
            top_k=top_k,
        )
