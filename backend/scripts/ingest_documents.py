"""
ingest_documents.py
Enhanced Document Ingestion Script for NC ASK
Bridges existing ingestion service with NC ASK metadata requirements
"""
import asyncio
import sys
import aiohttp
from pathlib import Path
import logging
from dotenv import load_dotenv

load_dotenv()

# --- Setup and Initialization ---

# Add parent directory to path (assuming this script is in a subdirectory)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import services
from services.ingestion import IngestionService
from services.downloader import download_remote_file, cleanup_temp_downloads, TEMP_DOWNLOAD_DIR
from config import get_document_config, ContentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Helper Functions ---

def get_document_metadata(doc_path: Path) -> dict:
    """
    Get metadata for a local document file.
    Checks for accompanying JSON metadata file.

    Args:
        doc_path: Path to the document file

    Returns:
        Dictionary of metadata
    """
    metadata_path = doc_path.parent / f"{doc_path.stem}_metadata.json"

    if metadata_path.exists():
        import json
        with open(metadata_path, 'r') as f:
            return json.load(f)

    # Return basic metadata if no metadata file exists
    return {
        "title": doc_path.stem.replace('_', ' ').title(),
        "topic": "General Resources",
        "audience": ["families"],
        "tags": [],
        "content_type": "GeneralInfo",
        "source_org": "Local File",
        "authority_level": 3
    }


def create_sample_documents():
    """Create sample documents directory if it doesn't exist."""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    logger.info(f"Created data directory at: {data_dir}")


# --- Main Ingestion Logic ---

async def ingest_nc_ask_documents():
    """
    Ingest NC ASK documents with enhanced metadata.
    Handles both local files and remote URLs via the downloader service.
    """
    data_dir = Path(__file__).parent.parent / "data"

    if not data_dir.exists():
        logger.info("Creating data directory...")
        create_sample_documents()

    # Load document configuration
    doc_config = get_document_config()
    NC_ASK_DOCUMENTS = doc_config.get_all_documents()

    logger.info(f"Loaded {len(NC_ASK_DOCUMENTS)} document configurations")

    # Validate all documents
    if not doc_config.validate_all():
        logger.warning("Some document configurations have validation errors")

    # 1. Prepare list of all unique documents to ingest
    ingestion_targets = []
    ingested_urls = set()
    supported_extensions = ['.pdf', '.docx', '.txt', '.html', '.htm']
    local_documents = []

    for ext in supported_extensions:
        local_documents.extend(data_dir.glob(f'*{ext}'))

    # Process local documents
    for doc_path in local_documents:
        if '_metadata' in doc_path.stem or doc_path.parent == TEMP_DOWNLOAD_DIR:
            continue

        metadata = get_document_metadata(doc_path)
        source_url = metadata.get("source_url")

        if source_url and source_url in ingested_urls:
            continue

        ingestion_targets.append({
            "path": str(doc_path),
            "title": metadata.get("title", doc_path.stem),
            "metadata": metadata,
            "is_remote": False
        })

        if source_url:
            ingested_urls.add(source_url)

    # Process remote documents from configuration
    for key, metadata_template in NC_ASK_DOCUMENTS.items():
        source_url = metadata_template.get("source_url")

        if source_url and source_url not in ingested_urls:
            metadata = metadata_template.copy()

            # Convert ContentType enum value if needed
            if isinstance(metadata.get('content_type'), str):
                # Already a string, keep as is
                pass
            else:
                # Convert enum to string
                metadata['content_type'] = metadata['content_type'].value if hasattr(metadata['content_type'], 'value') else str(metadata['content_type'])

            ingestion_targets.append({
                "path": None,  # Will be updated with the local temporary path
                "title": metadata.get("title", key),
                "metadata": metadata,
                "is_remote": True,
                "key": key
            })
            ingested_urls.add(source_url)

    logger.info(f"Found {len(ingestion_targets)} total resources to process.")

    # 2. Ingest documents using an aiohttp session for concurrent downloads
    async with aiohttp.ClientSession() as session:
        for target in ingestion_targets:
            doc_path_str = target['path']
            metadata = target['metadata'].copy()
            source_url = metadata.get("source_url")

            if target['is_remote']:
                # DOWNLOAD STEP: Fetch remote file and get local path
                key = target.get("key", source_url)
                local_path_obj = await download_remote_file(session, source_url, key)

                if not local_path_obj:
                    logger.error(f"✗ Failed to download remote resource: {source_url}. Skipping ingestion.")
                    continue

                doc_path_str = str(local_path_obj)

            # Final checks and ingestion call
            try:
                logger.info(f"Ingesting: {target['title']} ({'Local' if not target['is_remote'] else 'Remote'})")

                # Extract explicit arguments for the IngestionService signature
                content_type = metadata.pop("content_type", None)

                if metadata.get("escalation_flag") == "crisis" or "drowning" in target['title'].lower():
                    metadata["priority"] = "high"
                    logger.warning(f"Crisis content detected in {target['title']}")

                # Call the IngestionService
                result = await IngestionService.ingest_document(
                    file_path=doc_path_str,
                    title=target['title'],
                    source_url=source_url,
                    content_type=content_type,
                    metadata=metadata  # Remaining metadata is passed here
                )

                logger.info(f"✓ Successfully ingested: {result['title']}")
                logger.info(f"  - Document ID: {result['document_id']}")
                logger.info(f"  - Chunks created: {result['chunks_created']}")
                logger.info(f"  - Content type: {content_type}")
                if metadata.get("escalation_flag"):
                    logger.info(f"  - Escalation flag: {metadata['escalation_flag']}")

            except Exception as e:
                logger.error(f"✗ Failed to ingest {target['title']}: {e}")
                import traceback
                logger.debug(traceback.format_exc())

    # 3. Cleanup temporary files
    cleanup_temp_downloads()


async def main():
    """Main function"""

    # Load .env file from project root
    project_root = Path(__file__).parent.parent.parent
    dotenv_path = project_root / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    logger.info("=" * 60)
    logger.info("NC ASK Enhanced Document Ingestion")
    logger.info("=" * 60)

    await ingest_nc_ask_documents()

    logger.info("=" * 60)
    logger.info("Ingestion complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
