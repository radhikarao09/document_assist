from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.container import get_document_assistant_service
from app.schemas import QuestionRequest


router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Please select a PDF file.")
    try:
        return get_document_assistant_service().upload(file.filename, file.file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not process PDF: {exc}") from exc


@router.post("/ask")
async def ask(request: QuestionRequest):
    try:
        answer = get_document_assistant_service().ask(request.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not answer the question: {exc}") from exc

    return {
        "question": request.question,
        "answer": answer
    }