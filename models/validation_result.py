"""
Validation result data model.

This module defines the ValidationResult dataclass used for returning
structured validation results from service operations.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ValidationResult:
    """
    Result of a validation operation.
    
    Attributes:
        success: Whether the validation succeeded
        message: Human-readable message describing the result
        details: Optional dictionary with additional details about the result
    """
    success: bool
    message: str
    details: Optional[dict] = field(default_factory=dict)
    
    def __bool__(self) -> bool:
        """Allow using ValidationResult in boolean context."""
        return self.success
    
    def __str__(self) -> str:
        """String representation of the result."""
        return self.message
