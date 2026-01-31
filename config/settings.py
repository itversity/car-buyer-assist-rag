"""
Application settings for Car Buyer Assist RAG Application.

This module manages all environment variables using Pydantic for validation
and type safety.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseModel):
    """
    Application settings loaded from environment variables.
    
    All settings are validated using Pydantic for type safety and
    to ensure required values are present.
    """
    
    # Google Cloud Platform Settings
    google_application_credentials: Optional[str] = Field(
        default=None,
        description="Path to GCP service account JSON key file"
    )
    
    google_project_id: Optional[str] = Field(
        default=None,
        description="GCP project ID for Vertex AI access"
    )
    
    google_region: str = Field(
        default="us-central1",
        description="GCP region for Vertex AI services"
    )
    
    # LangSmith Settings
    langsmith_api_key: Optional[str] = Field(
        default=None,
        description="LangSmith API key for observability"
    )
    
    langsmith_project: Optional[str] = Field(
        default=None,
        description="LangSmith project name"
    )
    
    langsmith_tracing: bool = Field(
        default=True,
        description="Enable LangSmith tracing"
    )
    
    # Application Settings
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    @field_validator('google_application_credentials')
    @classmethod
    def validate_credentials_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate that credentials file exists if path is provided."""
        if v and not Path(v).exists():
            # Don't raise error, just warn - will be caught in connectivity validation
            pass
        return v
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()
    
    def get_required_env_vars(self) -> dict[str, Optional[str]]:
        """
        Get dictionary of required environment variables and their values.
        
        Returns:
            Dictionary with variable names as keys and their values
        """
        return {
            'GOOGLE_APPLICATION_CREDENTIALS': self.google_application_credentials,
            'GOOGLE_PROJECT_ID': self.google_project_id,
            'GOOGLE_REGION': self.google_region,
            'LANGSMITH_API_KEY': self.langsmith_api_key,
            'LANGSMITH_PROJECT': self.langsmith_project,
            'LANGSMITH_TRACING': str(self.langsmith_tracing).lower()
        }
    
    def get_missing_required_vars(self) -> list[str]:
        """
        Get list of required environment variables that are not set.
        
        Returns:
            List of missing variable names
        """
        optional_vars = ['GOOGLE_REGION', 'LANGSMITH_TRACING']
        required_vars = self.get_required_env_vars()
        
        missing = [
            key for key, value in required_vars.items()
            if not value and key not in optional_vars
        ]
        
        return missing
    
    def is_fully_configured(self) -> bool:
        """
        Check if all required environment variables are configured.
        
        Returns:
            True if all required variables are set, False otherwise
        """
        return len(self.get_missing_required_vars()) == 0
    
    class Config:
        """Pydantic configuration."""
        # Allow loading from environment variables
        case_sensitive = False
        
        # Map environment variable names to field names
        fields = {
            'google_application_credentials': {'env': 'GOOGLE_APPLICATION_CREDENTIALS'},
            'google_project_id': {'env': 'GOOGLE_PROJECT_ID'},
            'google_region': {'env': 'GOOGLE_REGION'},
            'langsmith_api_key': {'env': 'LANGSMITH_API_KEY'},
            'langsmith_project': {'env': 'LANGSMITH_PROJECT'},
            'langsmith_tracing': {'env': 'LANGSMITH_TRACING'},
            'log_level': {'env': 'LOG_LEVEL'}
        }


# Create singleton instance
settings = Settings(
    google_application_credentials=os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
    google_project_id=os.getenv('GOOGLE_PROJECT_ID'),
    google_region=os.getenv('GOOGLE_REGION', 'us-central1'),
    langsmith_api_key=os.getenv('LANGSMITH_API_KEY'),
    langsmith_project=os.getenv('LANGSMITH_PROJECT'),
    langsmith_tracing=os.getenv('LANGSMITH_TRACING', 'true').lower() == 'true',
    log_level=os.getenv('LOG_LEVEL', 'INFO')
)
