from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)


class UploadResponse(BaseModel):
    success: bool
    filename: str


class DocumentChunk(BaseModel):
    chunk_id: int
    text: str
    page_number: int | None = None


class RetrievedChunk(BaseModel):
    chunk_id: int
    text: str
    score: float
    source: str
    page_number: int | None = None


class QueryPlan(BaseModel):
    normalized_question: str
    question_type: str
    top_k: int = 3


class ValidationResult(BaseModel):
    supported: bool
    reason: str
    retryable: bool = False
