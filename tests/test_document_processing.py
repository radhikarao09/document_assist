from app.services.document_service import create_document_chunks, create_chunks


def test_create_chunks_preserves_existing_helper_behavior():
    assert create_chunks("abcdefgh", chunk_size=3) == ["abc", "def", "gh"]


def test_create_document_chunks_preserves_page_metadata():
    chunks = create_document_chunks([(2, "A policy statement")], chunk_size=8)

    assert chunks
    assert all(chunk.page_number == 2 for chunk in chunks)
    assert all(chunk.text for chunk in chunks)
