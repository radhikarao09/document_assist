from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np

# Read PDF
pdf_path = "documents/healthcare_policy_sample.pdf"
reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    text += page.extract_text()

# Split text into chunks
chunk_size = 500
chunks = []

for i in range(0, len(text), chunk_size):
    chunks.append(text[i:i + chunk_size])

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create embeddings for all chunks
chunk_embeddings = model.encode(chunks)

# User's question
query = "What documents are required for reimbursement?"

# Create embedding for the question
query_embedding = model.encode([query])[0]

# Calculate similarity
similarities = []

for chunk_embedding in chunk_embeddings:
    similarity = np.dot(query_embedding, chunk_embedding) / (
        np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
    )
    similarities.append(similarity)

# Find the most relevant chunk
best_index = np.argmax(similarities)

print("Question:", query)
print("\nMost relevant chunk:")
print(chunks[best_index])
print("\nSimilarity score:", similarities[best_index])