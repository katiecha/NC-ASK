"""
services/downloader.py

Asynchronous utility functions for safely downloading remote documents
to a local, temporary directory for ingestion.
"""
import logging
import mimetypes
from pathlib import Path
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

# Create a temporary directory for downloaded files within the project's data folder
TEMP_DOWNLOAD_DIR = Path(__file__).parent.parent / "data" / "temp_downloads"
TEMP_DOWNLOAD_DIR.mkdir(exist_ok=True)


def get_file_extension_from_url(url: str, content_type: str | None = None) -> str:
    """Infers the file extension from the URL path or Content-Type header."""

    path = urlparse(url).path
    if '.' in path:
        return Path(path).suffix.lower()

    if content_type:
        ext = mimetypes.guess_extension(content_type)
        if ext:
            return ext.replace('.jpe', '.jpg')

    return ".html"

async def download_remote_file(client: httpx.AsyncClient, url: str, key: str) -> Path | None:
    """
    Downloads a remote file asynchronously and saves it to a temporary location.

    Args:
        client: httpx.AsyncClient instance
        url: URL to download from
        key: Unique key for naming the downloaded file

    Returns:
        Path to downloaded file or None on failure
    """
    temp_file_path = None

    # Add User-Agent header to bypass 403 Forbidden errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }

    try:
        logger.info(f"Attempting to download: {url}")

        # Use httpx to download with timeout
        async with client.stream('GET', url, timeout=30.0, headers=headers, follow_redirects=True) as response:

            response.raise_for_status()

            content_type = response.headers.get('Content-Type')
            ext = get_file_extension_from_url(url, content_type)

            # Create the unique local path
            temp_file_name = f"{key}_{response.status_code}{ext}"
            temp_file_path = TEMP_DOWNLOAD_DIR / temp_file_name

            # Read and write content in chunks
            with open(temp_file_path, 'wb') as f:
                async for chunk in response.aiter_bytes(chunk_size=1024):
                    f.write(chunk)

            logger.info(f"Successfully downloaded {url} to {temp_file_path.name}")
            return temp_file_path

    except httpx.HTTPError as e:
        logger.error(f"HTTP error downloading {url}: {e}")
    except TimeoutError:
        logger.error(f"Timeout error downloading {url}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during download of {url}: {e}")

    return None

def cleanup_temp_downloads():
    """Removes all files in the temporary download directory."""
    logger.info(f"Cleaning up temporary directory: {TEMP_DOWNLOAD_DIR}")
    for item in TEMP_DOWNLOAD_DIR.iterdir():
        try:
            if item.is_file():
                item.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete {item.name} during cleanup: {e}")
    if any(TEMP_DOWNLOAD_DIR.iterdir()):
         logger.warning("Cleanup completed, but some items may remain.")
    else:
        logger.info("Temporary directory cleaned.")
