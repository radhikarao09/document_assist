from openai import OpenAI

from app.core.config import settings


class LLMService:

    def __init__(self, client: OpenAI | None = None):
        self.client = client

    def _get_client(self) -> OpenAI:
        if self.client is None:
            if not settings.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY is not configured")
            self.client = OpenAI(api_key=settings.openai_api_key)
        return self.client

    def generate_answer(self, question: str, context: str) -> str:

        response = self._get_client().responses.create(
            model=settings.openai_model,
            instructions=(
                "You are a document question-answering assistant. "
                "Answer ONLY from the provided document context. "
                "Do not guess or use outside knowledge. "
                "If the answer is not present, say: "
                "'I could not find that information in the document.' "
                "Give a simple, direct answer."
            ),
            input=f"""
Document:

{context}

User question:

{question}
"""
        )

        return response.output_text.strip()