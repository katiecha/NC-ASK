"""
services/downloader.py

Asynchronous utility functions for safely downloading remote documents 
to a local, temporary directory for ingestion.
"""
import aiohttp
import asyncio
import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import mimetypes
import os # Added for path manipulation

logger = logging.getLogger(__name__)

# Create a temporary directory for downloaded files within the project's data folder
TEMP_DOWNLOAD_DIR = Path(__file__).parent.parent / "data" / "temp_downloads"
TEMP_DOWNLOAD_DIR.mkdir(exist_ok=True)


def get_file_extension_from_url(url: str, content_type: Optional[str] = None) -> str:
    """Infers the file extension from the URL path or Content-Type header."""
    
    path = urlparse(url).path
    if '.' in path:
        return Path(path).suffix.lower()

    if content_type:
        ext = mimetypes.guess_extension(content_type)
        if ext:
            return ext.replace('.jpe', '.jpg')
            
    return ".html"

async def download_remote_file(session: aiohttp.ClientSession, url: str, key: str) -> Optional[Path]:
    """
    Downloads a remote file asynchronously and saves it to a temporary location.
    """
    temp_file_path = None
    
    # CRITICAL FIX: Add User-Agent header to bypass 403 Forbidden errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }
    
    try:
        logger.info(f"Attempting to download: {url}")
        
        # Pass the headers to the session.get call
        async with session.get(url, timeout=30, headers=headers) as response:
            
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type')
            ext = get_file_extension_from_url(url, content_type)
            
            # Create the unique local path
            temp_file_name = f"{key}_{response.status}{ext}"
            temp_file_path = TEMP_DOWNLOAD_DIR / temp_file_name
            
            # Read and write content in chunks
            with open(temp_file_path, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)

            logger.info(f"Successfully downloaded {url} to {temp_file_path.name}")
            return temp_file_path

    except aiohttp.ClientError as e:
        logger.error(f"HTTP/Client error downloading {url}: {e}")
    except asyncio.TimeoutError:
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