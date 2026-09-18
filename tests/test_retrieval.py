import numpy as np

from app.schemas import DocumentChunk
from app.services.vector_service import VectorService


def test_vector_search_returns_highest_scoring_chunk():
    service = VectorService()
    chunks = [
        DocumentChunk(chunk_id=0, text="leave policy", page_number=1),
        DocumentChunk(chunk_id=1, text="reimbursement receipts", page_number=2),
    ]
    embeddings = np.array([[1.0, 0.0], [0.0, 1.0]])

    results = service.search(np.array([0.0, 1.0]), embeddings, chunks, top_k=1)

    assert [result.chunk_id for result in results] == [1]


def test_keyword_search_finds_exact_document_terms():
    service = VectorService()
    chunks = [
        DocumentChunk(chunk_id=0, text="annual leave entitlement"),
        DocumentChunk(chunk_id=1, text="hospital payment receipts"),
    ]

    results = service.keyword_search("payment receipts", chunks, top_k=1)

    assert results[0].chunk_id == 1


def test_legacy_string_chunks_remain_supported():
    service = VectorService()
    embeddings = np.array([[1.0, 0.0], [0.0, 1.0]])

    results = service.find_relevant_chunks(
        np.array([1.0, 0.0]), embeddings, ["first chunk", "second chunk"], top_k=1
    )

    assert results == ["first chunk"]
