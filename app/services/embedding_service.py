from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def create_embeddings(self, texts):
        return self.model.encode(texts)

    def create_query_embedding(self, query):
        return self.model.encode([query])[0]