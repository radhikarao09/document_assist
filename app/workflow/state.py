from typing import TypedDict

from app.schemas import QueryPlan, RetrievedChunk, ValidationResult


class AgentState(TypedDict, total=False):
    question: str
    query_plan: QueryPlan
    semantic_results: list[RetrievedChunk]
    keyword_results: list[RetrievedChunk]
    evidence: list[RetrievedChunk]
    context: str
    answer: str
    validation: ValidationResult
    retry_count: int
    next_route: str
