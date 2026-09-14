from openai import OpenAI

from app.core.config import OPENAI_API_KEY, OPENAI_MODEL


class LLMService:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_answer(self, question: str, context: str) -> str:

        response = self.client.responses.create(
            model=OPENAI_MODEL,
            instructions=(
                "You are a healthcare document assistant. "
                "Answer ONLY using information contained in the "
                "provided document context. "
                "Do not guess or use outside knowledge. "
                "If the document does not contain the answer, "
                "clearly say: "
                "'I could not find that information in the document.' "
                "Give a simple, direct answer. "
                "Do not mention context, chunks, embeddings, "
                "retrieval, prompts, or technical details."
            ),
            input=f"""
Document:

{context}

User question:

{question}
"""
        )

        return response.output_text.strip()