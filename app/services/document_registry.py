from dataclasses import dataclass
from threading import Lock

from app.schemas import DocumentChunk


@dataclass
class DocumentIndex:
    filename: str
    path: str
    chunks: list[DocumentChunk]
    embeddings: object


class DocumentRegistry:
    def __init__(self):
        self._current: DocumentIndex | None = None
        self._lock = Lock()

    def set_current(self, document: DocumentIndex) -> None:
        with self._lock:
            self._current = document

    def get_current(self) -> DocumentIndex | None:
        with self._lock:
            return self._current

    def clear(self) -> None:
        with self._lock:
            self._current = None
