import re

import numpy as np

from app.schemas import DocumentChunk, RetrievedChunk


class VectorService:
    def find_relevant_chunks(
        self,
        query_embedding,
        chunk_embeddings,
        chunks,
        top_k=3,
    ):
        return [
            result.text
            for result in self.search(query_embedding, chunk_embeddings, chunks, top_k)
        ]

    def search(
        self,
        query_embedding,
        chunk_embeddings,
        chunks: list[DocumentChunk] | list[str],
        top_k: int = 3,
        source: str = "semantic",
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []
        normalized_chunks = [
            chunk
            if isinstance(chunk, DocumentChunk)
            else DocumentChunk(chunk_id=index, text=chunk)
            for index, chunk in enumerate(chunks)
        ]
        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            return []

        scores = []
        for chunk_embedding in chunk_embeddings:
            chunk_norm = np.linalg.norm(chunk_embedding)
            scores.append(
                float(np.dot(query_embedding, chunk_embedding) / (query_norm * chunk_norm))
                if chunk_norm else 0.0
            )

        top_indices = np.argsort(scores)[-top_k:][::-1]
        return [
            RetrievedChunk(
                chunk_id=normalized_chunks[index].chunk_id,
                text=normalized_chunks[index].text,
                score=scores[index],
                source=source,
                page_number=normalized_chunks[index].page_number,
            )
            for index in top_indices
        ]

    def keyword_search(
        self,
        query: str,
        chunks: list[DocumentChunk],
        top_k: int = 3,
    ) -> list[RetrievedChunk]:
        terms = set(re.findall(r"[a-z0-9]{3,}", query.lower()))
        scored = []
        for chunk in chunks:
            chunk_terms = set(re.findall(r"[a-z0-9]{3,}", chunk.text.lower()))
            score = len(terms & chunk_terms) / max(len(terms), 1)
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            RetrievedChunk(
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                score=float(score),
                source="keyword",
                page_number=chunk.page_number,
            )
            for score, chunk in scored[:top_k]
        ]