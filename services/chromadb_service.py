"""
ChromaDB service for vector database operations.

This module handles all ChromaDB-related operations including connectivity
validation, client management, and database operations.
"""

from pathlib import Path
from typing import Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from config.constants import PathConfig, ValidationConfig, UIMessages
from models.validation_result import ValidationResult
from utils.logger import get_logger

logger = get_logger(__name__)


class ChromaDBService:
    """Service for managing ChromaDB operations."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize ChromaDB service.
        
        Args:
            db_path: Path to ChromaDB storage directory. If None, uses default from config.
        """
        self.db_path = db_path or PathConfig.CHROMA_DB_PATH
        self._client: Optional[chromadb.PersistentClient] = None
        logger.debug(f"ChromaDB service initialized with path: {self.db_path}")
    
    def get_or_create_client(self) -> chromadb.PersistentClient:
        """
        Get existing client or create a new one.
        
        Returns:
            ChromaDB persistent client instance
        """
        if self._client is None:
            logger.info(f"Creating ChromaDB client at {self.db_path}")
            
            # Ensure directory exists
            self.db_path.mkdir(parents=True, exist_ok=True)
            
            # Create persistent client
            self._client = chromadb.PersistentClient(path=str(self.db_path))
            logger.info("ChromaDB client created successfully")
        
        return self._client
    
    def validate_connection(self) -> ValidationResult:
        """
        Validate ChromaDB connectivity and perform read/write tests.
        
        Returns:
            ValidationResult indicating success or failure with details
        """
        logger.info("Starting ChromaDB connectivity validation")
        
        try:
            # Check if directory exists, create if needed
            if not self.db_path.exists():
                logger.info(f"Creating ChromaDB directory at {self.db_path.absolute()}")
                self.db_path.mkdir(parents=True, exist_ok=True)
                status_msg = f"Created ChromaDB directory at {self.db_path.absolute()}"
            else:
                status_msg = f"Using existing ChromaDB at {self.db_path.absolute()}"
            
            # Get or create client
            client = self.get_or_create_client()
            
            # Test write access - create a test collection
            test_collection_name = ValidationConfig.TEST_COLLECTION_NAME
            
            # Delete test collection if it exists
            try:
                client.delete_collection(name=test_collection_name)
                logger.debug(f"Deleted existing test collection: {test_collection_name}")
            except Exception:
                # Collection doesn't exist, which is fine
                pass
            
            # Create test collection
            logger.debug(f"Creating test collection: {test_collection_name}")
            collection = client.create_collection(name=test_collection_name)
            
            # Test write operation
            collection.add(
                documents=[ValidationConfig.TEST_DOCUMENT],
                ids=[ValidationConfig.TEST_DOCUMENT_ID],
                metadatas=[ValidationConfig.TEST_METADATA]
            )
            logger.debug("Test document written successfully")
            
            # Test read operation
            count = collection.count()
            if count != 1:
                error_msg = f"Write test failed: expected 1 document, got {count}"
                logger.error(error_msg)
                return ValidationResult(
                    success=False,
                    message=error_msg,
                    details={'expected_count': 1, 'actual_count': count}
                )
            
            logger.debug("Test document read successfully")
            
            # Clean up test collection
            client.delete_collection(name=test_collection_name)
            logger.debug("Test collection deleted successfully")
            
            logger.info("ChromaDB validation successful")
            return ValidationResult(
                success=True,
                message=f"{UIMessages.SUCCESS_CHROMADB}\n{status_msg}",
                details={
                    'path': str(self.db_path.absolute()),
                    'test_collection': test_collection_name,
                    'write_test': 'passed',
                    'read_test': 'passed'
                }
            )
            
        except ImportError as e:
            logger.error(f"ChromaDB import error: {e}")
            return ValidationResult(
                success=False,
                message=UIMessages.ERROR_CHROMADB_IMPORT,
                details={'error': str(e)}
            )
        
        except PermissionError as e:
            logger.error(f"ChromaDB permission error: {e}")
            return ValidationResult(
                success=False,
                message=UIMessages.ERROR_CHROMADB_PERMISSION.format(error=str(e)),
                details={'error': str(e), 'path': str(self.db_path)}
            )
        
        except Exception as e:
            logger.error(f"ChromaDB validation failed: {e}", exc_info=True)
            return ValidationResult(
                success=False,
                message=UIMessages.ERROR_CHROMADB_FAILED.format(error=str(e)),
                details={'error': str(e), 'error_type': type(e).__name__}
            )
    
    def get_or_create_collection(self, name: str, embedding_function=None):
        """
        Get existing collection or create a new one.
        
        Args:
            name: Collection name
            embedding_function: Optional embedding function for the collection
            
        Returns:
            ChromaDB collection instance
        """
        logger.info(f"Getting or creating collection: {name}")
        client = self.get_or_create_client()
        
        try:
            # Try to get existing collection
            collection = client.get_collection(
                name=name,
                embedding_function=embedding_function
            )
            logger.debug(f"Retrieved existing collection: {name}")
        except Exception:
            # Collection doesn't exist, create it
            logger.info(f"Creating new collection: {name}")
            collection = client.create_collection(
                name=name,
                embedding_function=embedding_function
            )
        
        return collection
    
    def clear_collection(self, name: str) -> bool:
        """
        Delete and recreate a collection (clears all data).
        
        Args:
            name: Collection name to clear
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Clearing collection: {name}")
        client = self.get_or_create_client()
        
        try:
            # Delete if exists
            try:
                client.delete_collection(name=name)
                logger.debug(f"Deleted collection: {name}")
            except Exception:
                logger.debug(f"Collection {name} didn't exist, nothing to delete")
            
            # Create fresh collection
            client.create_collection(name=name)
            logger.info(f"Created fresh collection: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear collection {name}: {e}", exc_info=True)
            return False
    
    def get_collection_stats(self, name: str) -> dict:
        """
        Get statistics about a collection.
        
        Args:
            name: Collection name
            
        Returns:
            Dictionary with collection stats (count, metadata)
        """
        logger.debug(f"Getting stats for collection: {name}")
        client = self.get_or_create_client()
        
        try:
            collection = client.get_collection(name=name)
            count = collection.count()
            
            return {
                'name': name,
                'count': count,
                'exists': True
            }
        except Exception as e:
            logger.warning(f"Collection {name} not found: {e}")
            return {
                'name': name,
                'count': 0,
                'exists': False
            }
    
    def list_collections(self) -> list:
        """
        List all available collections.
        
        Returns:
            List of collection names
        """
        logger.debug("Listing all collections")
        client = self.get_or_create_client()
        
        try:
            collections = client.list_collections()
            collection_names = [col.name for col in collections]
            logger.info(f"Found {len(collection_names)} collections")
            return collection_names
        except Exception as e:
            logger.error(f"Failed to list collections: {e}", exc_info=True)
            return []