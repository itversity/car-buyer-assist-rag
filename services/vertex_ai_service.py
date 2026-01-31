"""
Vertex AI service for Google Cloud AI operations.

This module handles all Vertex AI-related operations including embeddings
and LLM model validation.
"""

from typing import Optional
import google.auth
from google.auth.exceptions import DefaultCredentialsError

from config.settings import settings
from config.constants import ModelConfig, ValidationConfig, UIMessages
from models.validation_result import ValidationResult
from utils.logger import get_logger

logger = get_logger(__name__)


class VertexAIService:
    """Service for managing Vertex AI operations."""
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        region: Optional[str] = None
    ):
        """
        Initialize Vertex AI service.
        
        Args:
            project_id: GCP project ID. If None, uses value from settings.
            region: GCP region. If None, uses value from settings.
        """
        self.project_id = project_id or settings.google_project_id
        self.region = region or settings.google_region
        logger.debug(f"Vertex AI service initialized for project={self.project_id}, region={self.region}")
    
    def validate_embeddings(self) -> ValidationResult:
        """
        Validate Vertex AI embeddings model connectivity and functionality.
        
        Returns:
            ValidationResult indicating success or failure with details
        """
        logger.info("Starting Vertex AI embeddings validation")
        
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            
            # Initialize embeddings model
            logger.debug(f"Initializing embeddings model: {ModelConfig.EMBEDDING_MODEL_NAME}")
            embeddings = GoogleGenerativeAIEmbeddings(
                model=ModelConfig.EMBEDDING_MODEL_NAME,
                project=self.project_id,
                location=self.region,
                vertexai=True
            )
            
            # Test embedding generation
            logger.debug(f"Testing embeddings with text: '{ValidationConfig.TEST_EMBEDDING_TEXT}'")
            embedding = embeddings.embed_query(ValidationConfig.TEST_EMBEDDING_TEXT)
            
            # Verify embedding dimensions
            expected_dims = ModelConfig.EMBEDDING_DIMENSIONS
            actual_dims = len(embedding)
            
            if actual_dims != expected_dims:
                error_msg = UIMessages.ERROR_EMBEDDING_DIMENSIONS.format(
                    actual=actual_dims,
                    expected=expected_dims
                )
                logger.error(error_msg)
                return ValidationResult(
                    success=False,
                    message=error_msg,
                    details={
                        'expected_dimensions': expected_dims,
                        'actual_dimensions': actual_dims,
                        'model': ModelConfig.EMBEDDING_MODEL_NAME
                    }
                )
            
            logger.info("Vertex AI embeddings validation successful")
            message = UIMessages.SUCCESS_EMBEDDINGS.format(model=ModelConfig.EMBEDDING_MODEL_NAME)
            return ValidationResult(
                success=True,
                message=f"{message}\nDimensions: {actual_dims}",
                details={
                    'model': ModelConfig.EMBEDDING_MODEL_NAME,
                    'dimensions': actual_dims,
                    'project': self.project_id,
                    'region': self.region
                }
            )
            
        except ImportError as e:
            logger.error(f"Required package not installed: {e}")
            return ValidationResult(
                success=False,
                message=UIMessages.ERROR_VERTEX_IMPORT.format(error=str(e)),
                details={'error': str(e)}
            )
        
        except DefaultCredentialsError as e:
            logger.error(f"GCP authentication failed: {e}")
            return ValidationResult(
                success=False,
                message=UIMessages.ERROR_VERTEX_AUTH,
                details={'error': str(e)}
            )
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Embeddings validation failed: {error_msg}", exc_info=True)
            
            # Categorize error
            if "403" in error_msg or "permission" in error_msg.lower():
                message = UIMessages.ERROR_VERTEX_PERMISSION
            elif "404" in error_msg or "not found" in error_msg.lower():
                message = UIMessages.ERROR_VERTEX_MODEL_NOT_FOUND
            elif "API not enabled" in error_msg:
                message = UIMessages.ERROR_VERTEX_API_NOT_ENABLED
            else:
                message = UIMessages.ERROR_VERTEX_FAILED.format(error=error_msg)
            
            return ValidationResult(
                success=False,
                message=message,
                details={'error': error_msg, 'error_type': type(e).__name__}
            )
    
    def validate_llm(self) -> ValidationResult:
        """
        Validate Vertex AI LLM model connectivity and functionality.
        
        Returns:
            ValidationResult indicating success or failure with details
        """
        logger.info("Starting Vertex AI LLM validation")
        
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            # Initialize chat model
            logger.debug(f"Initializing LLM model: {ModelConfig.LLM_MODEL_NAME}")
            llm = ChatGoogleGenerativeAI(
                model=ModelConfig.LLM_MODEL_NAME,
                project=self.project_id,
                location=self.region,
                temperature=ModelConfig.LLM_TEMPERATURE,
                vertexai=True
            )
            
            # Test model with simple prompt
            test_prompt = ValidationConfig.TEST_LLM_PROMPT
            logger.debug(f"Testing LLM with prompt: '{test_prompt}'")
            response = llm.invoke(test_prompt)
            
            # Verify response
            if not response or not response.content:
                logger.error("No response received from LLM")
                return ValidationResult(
                    success=False,
                    message=UIMessages.ERROR_LLM_NO_RESPONSE,
                    details={'model': ModelConfig.LLM_MODEL_NAME}
                )
            
            logger.info("Vertex AI LLM validation successful")
            response_preview = response.content[:ValidationConfig.TEST_LLM_RESPONSE_MAX_LENGTH]
            message = UIMessages.SUCCESS_LLM.format(model=ModelConfig.LLM_MODEL_NAME)
            
            return ValidationResult(
                success=True,
                message=f"{message}\nResponse: {response_preview}...",
                details={
                    'model': ModelConfig.LLM_MODEL_NAME,
                    'response': response.content,
                    'project': self.project_id,
                    'region': self.region
                }
            )
            
        except ImportError as e:
            logger.error(f"Required package not installed: {e}")
            return ValidationResult(
                success=False,
                message=UIMessages.ERROR_VERTEX_IMPORT.format(error=str(e)),
                details={'error': str(e)}
            )
        
        except DefaultCredentialsError as e:
            logger.error(f"GCP authentication failed: {e}")
            return ValidationResult(
                success=False,
                message=UIMessages.ERROR_VERTEX_AUTH,
                details={'error': str(e)}
            )
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"LLM validation failed: {error_msg}", exc_info=True)
            
            # Categorize error
            if "403" in error_msg or "permission" in error_msg.lower():
                message = UIMessages.ERROR_VERTEX_PERMISSION
            elif "404" in error_msg or "not found" in error_msg.lower():
                message = UIMessages.ERROR_VERTEX_MODEL_NOT_FOUND
            elif "quota" in error_msg.lower():
                message = UIMessages.ERROR_VERTEX_QUOTA
            elif "API not enabled" in error_msg:
                message = UIMessages.ERROR_VERTEX_API_NOT_ENABLED
            else:
                message = UIMessages.ERROR_VERTEX_FAILED.format(error=error_msg)
            
            return ValidationResult(
                success=False,
                message=message,
                details={'error': error_msg, 'error_type': type(e).__name__}
            )
