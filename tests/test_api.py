import asyncio
from io import BytesIO

from app.api import routes


class FakeService:
    def upload(self, filename, source):
        return {"success": True, "filename": filename}

    def ask(self, question):
        return "Answer from the document."


def test_api_routes_delegate_to_application_service(monkeypatch):
    monkeypatch.setattr(routes, "get_document_assistant_service", lambda: FakeService())

    upload = asyncio.run(routes.upload_pdf(type("Upload", (), {"filename": "test.pdf", "file": BytesIO(b"pdf")})()))
    answer = asyncio.run(routes.ask(routes.QuestionRequest(question="What is this?")))

    assert upload["success"] is True
    assert answer["answer"] == "Answer from the document."
