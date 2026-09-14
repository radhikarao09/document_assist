from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np
import os

# Load environment variables
load_dotenv()

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load PDF
pdf_path = "documents/healthcare_policy_sample.pdf"
reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    text += page.extract_text()

# Split document into chunks
chunk_size = 500
chunks = []

for i in range(0, len(text), chunk_size):
    chunks.append(text[i:i + chunk_size])

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create embeddings for chunks
chunk_embeddings = model.encode(chunks)

# User question
question = "What documents are required for reimbursement?"

# Create embedding for question
query_embedding = model.encode([question])[0]

# Calculate similarity
similarities = []

for chunk_embedding in chunk_embeddings:
    similarity = np.dot(query_embedding, chunk_embedding) / (
        np.linalg.norm(query_embedding)
        * np.linalg.norm(chunk_embedding)
    )
    similarities.append(similarity)

# Get most relevant chunk
best_index = np.argmax(similarities)
best_chunk = chunks[best_index]

# Send retrieved context to LLM
response = client.responses.create(
    model="gpt-5.6-luna",
    instructions="Answer the user's question using only the provided document context. If the answer is not present in the context, say you cannot find it in the document.",
    input=f"""
Document context:
{best_chunk}

User question:
{question}
"""
)

print("Question:", question)
print("\nRetrieved document section:")
print(best_chunk)
print("\nAnswer:")
print(response.output_text)