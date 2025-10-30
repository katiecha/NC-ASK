"""
Document ingestion service for uploading and indexing documents
"""
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
from services.supabase_client import SupabaseClient
from services.document_processor import DocumentProcessor, DocumentChunk
from services.embeddings import EmbeddingService

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for ingesting documents into the knowledge base"""

    @staticmethod
    async def upload_file_to_storage(
        file_path: str,
        bucket_name: str = "documents"
    ) -> str:
        """
        Upload a file to Supabase Storage

        Args:
            file_path: Path to the local file
            bucket_name: Name of the storage bucket

        Returns:
            Storage path of the uploaded file
        """
        try:
            supabase = SupabaseClient.get_admin_client()
            file_name = Path(file_path).name

            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Upload to Supabase Storage
            storage_path = f"source_documents/{file_name}"
            supabase.storage.from_(bucket_name).upload(
                storage_path,
                file_data,
                {"content-type": "application/octet-stream"}
            )

            logger.info(f"Uploaded file to storage: {storage_path}")
            return storage_path

        except Exception as e:
            logger.error(f"Error uploading file to storage: {e}")
            raise

    @staticmethod
    def create_document_record(
        title: str,
        source_url: Optional[str],
        content_type: str,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Create a document record in the database

        Args:
            title: Document title
            source_url: Optional source URL
            content_type: Type of content (PDF, DOCX, etc.)
            file_path: Storage path of the file
            metadata: Optional metadata dictionary

        Returns:
            Document ID
        """
        try:
            supabase = SupabaseClient.get_admin_client()

            data = {
                "title": title,
                "source_url": source_url,
                "content_type": content_type,
                "file_path": file_path,
                "metadata": metadata or {}
            }

            result = supabase.table("documents").insert(data).execute()

            if result.data:
                doc_id = result.data[0]['id']
                logger.info(f"Created document record: ID={doc_id}")
                return doc_id
            else:
                raise Exception("Failed to create document record")

        except Exception as e:
            logger.error(f"Error creating document record: {e}")
            raise

    @staticmethod
    def insert_document_chunks(chunks: List[DocumentChunk]) -> None:
        """
        Insert document chunks with embeddings into the database

        Args:
            chunks: List of DocumentChunk objects
        """
        try:
            supabase = SupabaseClient.get_admin_client()

            # Generate embeddings for all chunks
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = EmbeddingService.generate_embeddings(chunk_texts)

            # Prepare data for insertion
            chunk_data = []
            for chunk, embedding in zip(chunks, embeddings):
                chunk_data.append({
                    "document_id": chunk.document_id,
                    "chunk_text": chunk.text,
                    "chunk_index": chunk.chunk_index,
                    "embedding": embedding,
                    "metadata": chunk.metadata
                })

            # Insert chunks in batches
            batch_size = 50
            for i in range(0, len(chunk_data), batch_size):
                batch = chunk_data[i:i + batch_size]
                supabase.table("document_chunks").insert(batch).execute()

            logger.info(f"Inserted {len(chunks)} document chunks")

        except Exception as e:
            logger.error(f"Error inserting document chunks: {e}")
            raise

    @classmethod
    async def ingest_document(
        cls,
        file_path: str,
        title: str,
        source_url: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete ingestion workflow for a document

        Args:
            file_path: Path to the document file
            title: Document title
            source_url: Optional source URL
            content_type: Optional content type (auto-detected if not provided)
            metadata: Optional metadata

        Returns:
            Dictionary with ingestion results
        """
        try:
            # Determine content type if not provided
            if not content_type:
                extension = Path(file_path).suffix.upper()[1:]
                content_type = extension

            # Upload file to storage
            storage_path = await cls.upload_file_to_storage(file_path)

            # Create document record
            document_id = cls.create_document_record(
                title=title,
                source_url=source_url,
                content_type=content_type,
                file_path=storage_path,
                metadata=metadata
            )

            # Process document into chunks
            chunks = DocumentProcessor.process_document(
                file_path=file_path,
                document_id=document_id,
                metadata=metadata
            )

            # Insert chunks with embeddings
            cls.insert_document_chunks(chunks)

            result = {
                "document_id": document_id,
                "title": title,
                "chunks_created": len(chunks),
                "storage_path": storage_path,
                "status": "success"
            }

            logger.info(f"Successfully ingested document: {title}")
            return result

        except Exception as e:
            logger.error(f"Error ingesting document {title}: {e}")
            raise
