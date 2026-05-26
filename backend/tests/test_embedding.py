import pytest
from app.services.embedding import EmbeddingService


@pytest.fixture
def embedding_service():
    return EmbeddingService()


def test_chunk_text_short_text(embedding_service):
    """Test that short text doesn't need chunking."""
    text = "This is a short text"
    chunks = embedding_service.chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_long_text(embedding_service):
    """Test that long text is correctly chunked."""
    text = "This is the first paragraph.\n\nThis is the second paragraph.\n\nThis is the third paragraph."
    chunks = embedding_service.chunk_text(text, chunk_size=30)
    assert len(chunks) > 1
    assert all(len(chunk) <= 40 for chunk in chunks)  # Allow some tolerance


def test_chunk_text_overlap(embedding_service):
    """Test that chunks have overlap."""
    text = "A" * 100
    chunks = embedding_service.chunk_text(text, chunk_size=50, overlap=10)
    assert len(chunks) >= 2
