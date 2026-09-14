from fastapi import APIRouter
from pydantic import BaseModel

from app.workflow.rag_workflow import ask_question


router = APIRouter()


class QuestionRequest(BaseModel):
    question: str


@router.post("/ask")
def ask(request: QuestionRequest):

    answer = ask_question(request.question)

    return {
        "question": request.question,
        "answer": answer
    }