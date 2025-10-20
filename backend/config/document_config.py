"""
document_config.py
Document configuration loader for NC ASK
Handles loading and validation of document metadata from JSON config files
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Defines the type of content for retrieval filtering."""
    PROCEDURAL_GUIDE = "ProceduralGuide"
    FAQ = "FAQ"
    LEGAL_RIGHT = "LegalRight"
    CLINICAL_SUMMARY = "ClinicalSummary"
    FORM_TEMPLATE = "FormTemplate"
    RESOURCE_DIRECTORY = "ResourceDirectory"
    GENERAL_INFO = "GeneralInfo"


class DocumentConfigLoader:
    """Loads and manages document metadata configurations."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the document config loader.

        Args:
            config_path: Path to the JSON config file.
                        If None, uses default location (backend/config/documents.json)
        """
        if config_path is None:
            config_path = Path(__file__).parent / "documents.json"

        self.config_path = config_path
        self._documents: Dict = {}
        self._load_config()

    def _load_config(self):
        """Load document configurations from JSON file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found: {self.config_path}")
                self._documents = {}
                return

            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._documents = json.load(f)

            logger.info(f"Loaded {len(self._documents)} document configurations from {self.config_path}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file {self.config_path}: {e}")
            self._documents = {}
        except Exception as e:
            logger.error(f"Error loading config file {self.config_path}: {e}")
            self._documents = {}

    def get_all_documents(self) -> Dict:
        """
        Get all document configurations.

        Returns:
            Dictionary of all document metadata
        """
        return self._documents.copy()

    def get_document(self, key: str) -> Optional[Dict]:
        """
        Get a specific document configuration by key.

        Args:
            key: The document identifier

        Returns:
            Document metadata dictionary or None if not found
        """
        return self._documents.get(key)

    def get_documents_by_topic(self, topic: str) -> Dict:
        """
        Get all documents for a specific topic.

        Args:
            topic: The topic to filter by (e.g., "Education", "Medicaid Programs")

        Returns:
            Dictionary of matching documents
        """
        return {
            key: doc for key, doc in self._documents.items()
            if doc.get("topic") == topic
        }

    def get_documents_by_content_type(self, content_type: str) -> Dict:
        """
        Get all documents of a specific content type.

        Args:
            content_type: The content type to filter by

        Returns:
            Dictionary of matching documents
        """
        return {
            key: doc for key, doc in self._documents.items()
            if doc.get("content_type") == content_type
        }

    def get_documents_by_source_org(self, source_org: str) -> Dict:
        """
        Get all documents from a specific organization.

        Args:
            source_org: The source organization name

        Returns:
            Dictionary of matching documents
        """
        return {
            key: doc for key, doc in self._documents.items()
            if doc.get("source_org") == source_org
        }

    def validate_document(self, key: str, metadata: Dict) -> List[str]:
        """
        Validate a document metadata structure.

        Args:
            key: Document key
            metadata: Document metadata dictionary

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Required fields
        required_fields = ["title", "topic", "audience", "tags", "content_type", "source_org"]
        for field in required_fields:
            if field not in metadata:
                errors.append(f"{key}: Missing required field '{field}'")

        # Validate content_type
        if "content_type" in metadata:
            try:
                ContentType(metadata["content_type"])
            except ValueError:
                valid_types = [ct.value for ct in ContentType]
                errors.append(
                    f"{key}: Invalid content_type '{metadata['content_type']}'. "
                    f"Must be one of: {', '.join(valid_types)}"
                )

        # Validate audience is a list
        if "audience" in metadata and not isinstance(metadata["audience"], list):
            errors.append(f"{key}: 'audience' must be a list")

        # Validate tags is a list
        if "tags" in metadata and not isinstance(metadata["tags"], list):
            errors.append(f"{key}: 'tags' must be a list")

        # Validate authority_level if present
        if "authority_level" in metadata:
            level = metadata["authority_level"]
            if not isinstance(level, int) or level < 1 or level > 3:
                errors.append(f"{key}: 'authority_level' must be 1, 2, or 3")

        return errors

    def validate_all(self) -> bool:
        """
        Validate all documents in the config.

        Returns:
            True if all documents are valid, False otherwise
        """
        all_valid = True
        for key, metadata in self._documents.items():
            errors = self.validate_document(key, metadata)
            if errors:
                all_valid = False
                for error in errors:
                    logger.error(error)

        if all_valid:
            logger.info("All document configurations are valid")

        return all_valid

    def reload(self):
        """Reload the configuration from file."""
        self._load_config()


# Global instance for easy access
_loader = None

def get_document_config() -> DocumentConfigLoader:
    """
    Get the global document config loader instance.

    Returns:
        DocumentConfigLoader instance
    """
    global _loader
    if _loader is None:
        _loader = DocumentConfigLoader()
    return _loader


def reload_document_config():
    """Reload the global document config from file."""
    global _loader
    if _loader is not None:
        _loader.reload()
