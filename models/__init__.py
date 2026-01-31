"""
Data models for Car Buyer Assist RAG Application.

This package contains data classes and models used throughout the application
for type-safe data handling.
"""

from .validation_result import ValidationResult
from .document_processing import (
    ProcessingStatus,
    DocumentMetadata,
    DocumentPreview,
    ProcessingResult,
    BatchProcessingResult
)

__all__ = [
    'ValidationResult',
    'ProcessingStatus',
    'DocumentMetadata',
    'DocumentPreview',
    'ProcessingResult',
    'BatchProcessingResult'
]
