import re

from app.core.logging import get_logger
from app.schemas import ValidationResult

logger = get_logger(__name__)


class ValidationAgent:
    """Checks that an answer has meaningful lexical support in the evidence."""

    not_found_message = "I could not find that information in the document."

    def validate(self, answer: str, evidence: str) -> ValidationResult:
        if not evidence.strip():
            return ValidationResult(
                supported=False,
                reason="No evidence was retrieved.",
                retryable=True,
            )
        if not answer.strip() or self.not_found_message.lower() in answer.lower():
            return ValidationResult(
                supported=False,
                reason="The answer reports that the evidence is insufficient.",
                retryable=True,
            )

        evidence_terms = set(re.findall(r"[a-z0-9]{4,}", evidence.lower()))
        answer_terms = set(re.findall(r"[a-z0-9]{4,}", answer.lower()))
        overlap = evidence_terms & answer_terms
        supported = len(overlap) >= 2
        result = ValidationResult(
            supported=supported,
            reason="Answer terms overlap retrieved evidence." if supported else "Answer lacks evidence support.",
            retryable=not supported,
        )
        logger.info("Validation Agent supported=%s", result.supported)
        return result
