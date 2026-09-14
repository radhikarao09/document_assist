from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [
    "Employees are entitled to 20 days of annual leave.",
    "Room rent is covered up to the limit specified in the policy.",
    "A reimbursement claim requires hospital bills and payment receipts."
]

embeddings = model.encode(texts)

print("Number of embeddings:", len(embeddings))
print("Embedding size:", len(embeddings[0]))
print("First embedding:")
print(embeddings[0])