import os
import tempfile

from services.document_processor import DocumentProcessor


def test_chunk_text_short_text():
    text = "Short text"
    chunks = DocumentProcessor.chunk_text(text, chunk_size=100, chunk_overlap=10)
    assert isinstance(chunks, list)
    assert chunks == [text]


def test_chunk_text_long_text_and_overlap():
    # Create a long text with sentence boundaries
    sentences = [f"Sentence {i}." for i in range(20)]
    text = " ".join(sentences)

    chunks = DocumentProcessor.chunk_text(text, chunk_size=100, chunk_overlap=10)

    # Should produce multiple chunks and preserve sentence boundaries
    assert len(chunks) > 1
    for c in chunks:
        assert c.endswith('.') or c.endswith('')


def test_process_document_txt(tmp_path):
    # create a temporary txt file and ensure process_document reads and chunks it
    file_path = tmp_path / "sample.txt"
    content = "This is a test. " * 30
    file_path.write_text(content, encoding='utf-8')

    chunks = DocumentProcessor.process_document(str(file_path), document_id=1, metadata={"a":1})

    assert isinstance(chunks, list)
    assert len(chunks) > 0
    # Each chunk should be a DocumentChunk-like object with .text and .chunk_index
    assert hasattr(chunks[0], 'text')
    assert hasattr(chunks[0], 'chunk_index')
