import numpy as np


class VectorService:

    def find_relevant_chunks(
        self,
        query_embedding,
        chunk_embeddings,
        chunks,
        top_k=3
    ):

        similarities = []

        for chunk_embedding in chunk_embeddings:

            similarity = np.dot(
                query_embedding,
                chunk_embedding
            ) / (
                np.linalg.norm(query_embedding)
                * np.linalg.norm(chunk_embedding)
            )

            similarities.append(similarity)

        top_indices = np.argsort(similarities)[-top_k:][::-1]

        relevant_chunks = [
            chunks[index]
            for index in top_indices
        ]

        return relevant_chunks