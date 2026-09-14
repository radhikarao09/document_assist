from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

question = "What documents are required for reimbursement?"

context = """
A reimbursement claim requires hospital bills, payment receipts,
discharge summary, prescriptions, diagnostic reports, and other
documents requested by the insurer.
"""

response = client.responses.create(
    model="gpt-5.6-luna",
    instructions="Answer the question using only the provided context.",
    input=f"""
Context:
{context}

Question:
{question}
"""
)

print("Answer:")
print(response.output_text)