from app.core.logging import get_logger
from app.services.llm_service import LLMService

logger = get_logger(__name__)


class AnswerGenerationAgent:
    """Generates an answer exclusively from evidence approved by the graph."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def generate(self, question: str, evidence: str) -> str:
        logger.info("Answer Generation Agent generating response")
        return self.llm_service.generate_answer(question, evidence)
