"""
Document processing and chunking service
"""
import logging
from pathlib import Path
from typing import Any

import PyPDF2
from bs4 import BeautifulSoup
from docx import Document

from services.config import settings

logger = logging.getLogger(__name__)


class DocumentChunk:
    """Represents a chunk of a document"""

    def __init__(
        self,
        text: str,
        chunk_index: int,
        document_id: int = None,
        metadata: dict[str, Any] = None
    ):
        self.text = text
        self.chunk_index = chunk_index
        self.document_id = document_id
        self.metadata = metadata or {}


class DocumentProcessor:
    """Service for processing and chunking documents"""

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise

    @staticmethod
    def extract_text_from_html(file_path: str) -> str:
        """Extract text from HTML file"""
        try:
            with open(file_path, encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), 'lxml')
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text()
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                return text
        except Exception as e:
            logger.error(f"Error extracting text from HTML: {e}")
            raise

    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extract text from a file based on its extension

        Args:
            file_path: Path to the file

        Returns:
            Extracted text content
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == '.pdf':
            return DocumentProcessor.extract_text_from_pdf(file_path)
        elif extension == '.docx':
            return DocumentProcessor.extract_text_from_docx(file_path)
        elif extension in ['.html', '.htm']:
            return DocumentProcessor.extract_text_from_html(file_path)
        elif extension == '.txt':
            with open(file_path, encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file type: {extension}")

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> list[str]:
        """
        Split text into semantic chunks with overlap

        Args:
            text: Input text to chunk
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks

        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or settings.CHUNK_SIZE
        chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            # Get chunk
            end = start + chunk_size

            # If not the last chunk, try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                sentence_ends = ['. ', '! ', '? ', '\n\n']
                best_break = end

                # Search backwards from end for a good break point
                for i in range(end, max(start + chunk_size // 2, start), -1):
                    for ending in sentence_ends:
                        if text[i:i+len(ending)] == ending:
                            best_break = i + len(ending)
                            break
                    if best_break != end:
                        break

                end = best_break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = end - chunk_overlap

        return chunks

    @staticmethod
    def process_document(
        file_path: str,
        document_id: int = None,
        metadata: dict[str, Any] = None
    ) -> list[DocumentChunk]:
        """
        Process a document: extract text and create chunks

        Args:
            file_path: Path to the document
            document_id: Optional document ID
            metadata: Optional metadata dictionary

        Returns:
            List of DocumentChunk objects
        """
        try:
            # Extract text
            text = DocumentProcessor.extract_text(file_path)

            # Create chunks
            text_chunks = DocumentProcessor.chunk_text(text)

            # Create DocumentChunk objects
            chunks = []
            for i, chunk_text in enumerate(text_chunks):
                chunk = DocumentChunk(
                    text=chunk_text,
                    chunk_index=i,
                    document_id=document_id,
                    metadata=metadata
                )
                chunks.append(chunk)

            logger.info(f"Processed document: {file_path} -> {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            raise
