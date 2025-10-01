"""
Document ingestion script
Run this script to ingest documents into the knowledge base
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ingestion import IngestionService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ingest_sample_documents():
    """
    Ingest sample documents from the data directory
    """
    # This is a placeholder - you'll add actual documents to backend/data/
    data_dir = Path(__file__).parent.parent / "data"

    if not data_dir.exists():
        logger.warning(f"Data directory not found: {data_dir}")
        logger.info("Please add documents to the backend/data/ directory")
        return

    # Get all supported document files
    supported_extensions = ['.pdf', '.docx', '.txt', '.html', '.htm']
    documents = []

    for ext in supported_extensions:
        documents.extend(data_dir.glob(f'*{ext}'))

    if not documents:
        logger.info("No documents found in data directory")
        logger.info("Supported formats: PDF, DOCX, TXT, HTML")
        return

    logger.info(f"Found {len(documents)} documents to ingest")

    # Ingest each document
    for doc_path in documents:
        try:
            logger.info(f"Ingesting: {doc_path.name}")

            result = await IngestionService.ingest_document(
                file_path=str(doc_path),
                title=doc_path.stem,
                metadata={
                    "source": "local",
                    "category": "general"
                }
            )

            logger.info(f"✓ Successfully ingested: {result['title']}")
            logger.info(f"  - Document ID: {result['document_id']}")
            logger.info(f"  - Chunks created: {result['chunks_created']}")

        except Exception as e:
            logger.error(f"✗ Failed to ingest {doc_path.name}: {e}")


async def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("NC-ASK Document Ingestion")
    logger.info("=" * 60)

    await ingest_sample_documents()

    logger.info("=" * 60)
    logger.info("Ingestion complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
