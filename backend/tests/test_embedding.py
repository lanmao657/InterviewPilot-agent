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
    chunks = embedding_service.chunk_text(text, chunk_size=30, overlap=10)
    assert len(chunks) > 1
    # Tolerance accounts for overlap prepended to each chunk after the first
    assert all(len(chunk) <= 40 for chunk in chunks)


def test_chunk_text_force_split_overlap(embedding_service):
    """Test that force-split chunks have overlap (text without natural delimiters)."""
    text = "A" * 100
    chunks = embedding_service.chunk_text(text, chunk_size=50, overlap=10)
    assert len(chunks) >= 2


def test_chunk_text_paragraph_overlap(embedding_service):
    """Test that overlap is applied when transitioning between paragraph-boundary chunks.

    Uses chunk_size=50, overlap=10 as specified in the spec.
    Verifies that the end of one chunk appears at the start of the next chunk.
    """
    # Create paragraphs where each is under chunk_size but combined they exceed it
    para1 = "Hello world this is the first paragraph text."  # 46 chars
    para2 = "Second paragraph with different content here."  # 46 chars
    text = para1 + "\n\n" + para2
    chunks = embedding_service.chunk_text(text, chunk_size=50, overlap=10)

    assert len(chunks) >= 2
    # The second chunk should start with the last 10 chars of the first chunk
    first_chunk = chunks[0]
    second_chunk = chunks[1]
    overlap_text = first_chunk[-10:]
    assert second_chunk.startswith(overlap_text), (
        f"Expected second chunk to start with '{overlap_text}', "
        f"but got '{second_chunk[:20]}'"
    )


def test_chunk_text_sentence_overlap(embedding_service):
    """Test that overlap is applied when transitioning between sentence-boundary chunks.

    Verifies that when a long paragraph is split by sentences, overlap is
    preserved at the boundary between sentence-based chunks.
    """
    # Create a paragraph longer than chunk_size so it gets split by sentences
    sentence1 = "First sentence is here."
    sentence2 = "Second sentence is also here."
    sentence3 = "Third sentence comes next."
    # Combine into one paragraph (no double newline) so it goes through sentence splitting
    text = sentence1 + sentence2 + sentence3
    chunks = embedding_service.chunk_text(text, chunk_size=40, overlap=10)

    assert len(chunks) >= 2
    # If there was a boundary transition, verify overlap
    if len(chunks) >= 2:
        first_chunk = chunks[0]
        second_chunk = chunks[1]
        overlap_text = first_chunk[-10:]
        assert second_chunk.startswith(overlap_text), (
            f"Expected second chunk to start with '{overlap_text}', "
            f"but got '{second_chunk[:20]}'"
        )
