"""
Connectivity validator orchestrator.

This module orchestrates all connectivity validation checks across
ChromaDB, Vertex AI, and LangSmith services.
"""

from typing import Dict, List, Tuple

from config.settings import settings
from models.validation_result import ValidationResult
from utils.logger import get_logger
from .chromadb_service import ChromaDBService
from .vertex_ai_service import VertexAIService
from .langsmith_service import LangSmithService

logger = get_logger(__name__)


class ConnectivityValidator:
    """
    Orchestrates connectivity validation for all external services.
    
    This class coordinates validation checks across ChromaDB, Vertex AI
    (embeddings and LLM), and LangSmith services.
    """
    
    def __init__(self):
        """Initialize connectivity validator with service instances."""
        logger.debug("Initializing ConnectivityValidator")
        self.chromadb_service = ChromaDBService()
        self.vertex_ai_service = VertexAIService()
        self.langsmith_service = LangSmithService()
    
    def validate_environment(self) -> Tuple[bool, Dict[str, str], List[str]]:
        """
        Check if required environment variables are set.
        
        Returns:
            Tuple of (all_configured, config_dict, missing_vars)
        """
        logger.info("Validating environment configuration")
        
        config = settings.get_required_env_vars()
        missing = settings.get_missing_required_vars()
        all_configured = len(missing) == 0
        
        if all_configured:
            logger.info("All required environment variables are configured")
        else:
            logger.warning(f"Missing environment variables: {', '.join(missing)}")
        
        return all_configured, config, missing
    
    def validate_chromadb(self) -> ValidationResult:
        """
        Validate ChromaDB connectivity.
        
        Returns:
            ValidationResult with success status and details
        """
        logger.info("Validating ChromaDB connectivity")
        result = self.chromadb_service.validate_connection()
        
        if result.success:
            logger.info("ChromaDB validation successful")
        else:
            logger.error(f"ChromaDB validation failed: {result.message}")
        
        return result
    
    def validate_vertex_ai_embeddings(self) -> ValidationResult:
        """
        Validate Vertex AI embeddings model.
        
        Returns:
            ValidationResult with success status and details
        """
        logger.info("Validating Vertex AI embeddings")
        result = self.vertex_ai_service.validate_embeddings()
        
        if result.success:
            logger.info("Vertex AI embeddings validation successful")
        else:
            logger.error(f"Vertex AI embeddings validation failed: {result.message}")
        
        return result
    
    def validate_vertex_ai_llm(self) -> ValidationResult:
        """
        Validate Vertex AI LLM model.
        
        Returns:
            ValidationResult with success status and details
        """
        logger.info("Validating Vertex AI LLM")
        result = self.vertex_ai_service.validate_llm()
        
        if result.success:
            logger.info("Vertex AI LLM validation successful")
        else:
            logger.error(f"Vertex AI LLM validation failed: {result.message}")
        
        return result
    
    def validate_langsmith(self) -> ValidationResult:
        """
        Validate LangSmith connectivity.
        
        Returns:
            ValidationResult with success status and details
        """
        logger.info("Validating LangSmith connectivity")
        result = self.langsmith_service.validate_connection()
        
        if result.success:
            logger.info("LangSmith validation successful")
        else:
            logger.error(f"LangSmith validation failed: {result.message}")
        
        return result
    
    def validate_all(self) -> Dict[str, ValidationResult]:
        """
        Validate all services and return aggregated results.
        
        Returns:
            Dictionary with service names as keys and ValidationResult as values
        """
        logger.info("Starting validation for all services")
        
        results = {
            'chromadb': self.validate_chromadb(),
            'vertex_ai_embeddings': self.validate_vertex_ai_embeddings(),
            'vertex_ai_llm': self.validate_vertex_ai_llm(),
            'langsmith': self.validate_langsmith()
        }
        
        # Log summary
        successful = sum(1 for result in results.values() if result.success)
        total = len(results)
        logger.info(f"Validation complete: {successful}/{total} services passed")
        
        return results
    
    def get_validation_summary(self, results: Dict[str, ValidationResult]) -> Tuple[int, int, bool]:
        """
        Get summary statistics from validation results.
        
        Args:
            results: Dictionary of validation results
            
        Returns:
            Tuple of (successful_count, total_count, all_passed)
        """
        successful = sum(1 for result in results.values() if result.success)
        total = len(results)
        all_passed = successful == total
        
        return successful, total, all_passed
