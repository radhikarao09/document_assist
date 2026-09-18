import hashlib
import re
from typing import TYPE_CHECKING, Any

import numpy as np

from app.core.config import settings

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


class _FallbackEmbeddingModel:
    """Small deterministic fallback for environments without model wheels."""

    def encode(self, texts: list[str]):
        vectors = []
        for text in texts:
            vector = np.zeros(256, dtype=float)
            for term in re.findall(r"[a-z0-9]{2,}", text.lower()):
                index = int(hashlib.sha256(term.encode()).hexdigest(), 16) % len(vector)
                vector[index] += 1.0
            norm = np.linalg.norm(vector)
            vectors.append(vector / norm if norm else vector)
        return np.array(vectors)


class EmbeddingService:
    def __init__(self, model: Any | None = None):
        self.model = model

    def _get_model(self):
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                self.model = _FallbackEmbeddingModel()
            else:
                self.model = SentenceTransformer(settings.embedding_model)
        return self.model

    def create_embeddings(self, texts: list[str]):
        return self._get_model().encode(texts)

    def create_query_embedding(self, query: str):
        return self._get_model().encode([query])[0]