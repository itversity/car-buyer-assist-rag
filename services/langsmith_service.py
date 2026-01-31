"""
LangSmith service for observability operations.

This module handles all LangSmith-related operations including connectivity
validation and project management.
"""

from typing import Optional

from config.settings import settings
from config.constants import UIMessages
from models.validation_result import ValidationResult
from utils.logger import get_logger

logger = get_logger(__name__)


class LangSmithService:
    """Service for managing LangSmith operations."""
    
    def __init__(self, project_name: Optional[str] = None):
        """
        Initialize LangSmith service.
        
        Args:
            project_name: LangSmith project name. If None, uses value from settings.
        """
        self.project_name = project_name or settings.langsmith_project
        logger.debug(f"LangSmith service initialized for project: {self.project_name}")
    
    def validate_connection(self) -> ValidationResult:
        """
        Validate LangSmith connectivity and project access.
        
        Returns:
            ValidationResult indicating success or failure with details
        """
        logger.info("Starting LangSmith connectivity validation")
        
        try:
            from langsmith import Client
            
            # Initialize LangSmith client
            logger.debug("Creating LangSmith client")
            client = Client()
            
            # Test 1: List projects to verify connectivity
            try:
                logger.debug("Listing LangSmith projects")
                projects = list(client.list_projects())
                project_names = [p.name for p in projects]
                logger.debug(f"Found {len(project_names)} projects")
            except Exception as e:
                error_msg = UIMessages.ERROR_LANGSMITH_LIST_PROJECTS.format(error=str(e))
                logger.error(error_msg)
                return ValidationResult(
                    success=False,
                    message=error_msg,
                    details={'error': str(e)}
                )
            
            # Test 2: Verify configured project exists
            if self.project_name:
                if self.project_name in project_names:
                    project_status = f"Project '{self.project_name}' found"
                    logger.info(project_status)
                else:
                    project_status = UIMessages.WARNING_PROJECT_NOT_FOUND.format(
                        project=self.project_name
                    )
                    logger.warning(project_status)
            else:
                project_status = "No project configured"
                logger.warning(project_status)
            
            # Test 3: API key is valid (if we got here, it's valid)
            logger.info("LangSmith validation successful")
            message = f"{UIMessages.SUCCESS_LANGSMITH}\n{project_status}\nAvailable projects: {len(project_names)}"
            
            return ValidationResult(
                success=True,
                message=message,
                details={
                    'configured_project': self.project_name,
                    'available_projects': len(project_names),
                    'project_names': project_names[:5]  # First 5 projects
                }
            )
            
        except ImportError as e:
            logger.error(f"LangSmith not installed: {e}")
            return ValidationResult(
                success=False,
                message=UIMessages.ERROR_LANGSMITH_IMPORT,
                details={'error': str(e)}
            )
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"LangSmith validation failed: {error_msg}", exc_info=True)
            
            # Categorize error
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                message = UIMessages.ERROR_LANGSMITH_AUTH
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                message = UIMessages.ERROR_LANGSMITH_NETWORK
            else:
                message = UIMessages.ERROR_LANGSMITH_FAILED.format(error=error_msg)
            
            return ValidationResult(
                success=False,
                message=message,
                details={'error': error_msg, 'error_type': type(e).__name__}
            )
