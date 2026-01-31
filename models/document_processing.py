"""
Document Processing data models.

This module defines data classes for document processing operations
to ensure type safety and consistent data structures.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ProcessingStatus(Enum):
    """Status of document processing operation."""
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"


@dataclass
class DocumentMetadata:
    """
    Metadata about a document.
    
    Attributes:
        filename: Name of the document file
        size_bytes: File size in bytes
        pages: Number of pages in document
        model_name: Extracted vehicle model name
        upload_time: When the document was uploaded
    """
    filename: str
    size_bytes: int
    pages: int
    model_name: str
    upload_time: datetime = field(default_factory=datetime.now)
    
    @property
    def size_formatted(self) -> str:
        """Return formatted file size."""
        if self.size_bytes < 1024:
            return f"{self.size_bytes} B"
        elif self.size_bytes < 1024 * 1024:
            return f"{self.size_bytes / 1024:.1f} KB"
        else:
            return f"{self.size_bytes / (1024 * 1024):.1f} MB"


@dataclass
class DocumentPreview:
    """
    Preview information about a document.
    
    Attributes:
        filename: Document filename
        size: Formatted file size
        size_bytes: Raw size in bytes
        pages: Number of pages
        model_name: Extracted model name
        error: Error message if preview failed
    """
    filename: str
    size: str
    size_bytes: int
    pages: int
    model_name: str
    error: Optional[str] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if preview is valid."""
        return self.error is None and self.pages > 0


@dataclass
class ProcessingResult:
    """
    Result of processing a single document.
    
    Attributes:
        filename: Name of the processed document
        status: Processing status
        chunks_created: Number of chunks created
        processing_time: Time taken to process (seconds)
        model_name: Extracted vehicle model name
        error: Error message if processing failed
        metadata: Additional processing metadata
    """
    filename: str
    status: ProcessingStatus
    chunks_created: int
    processing_time: float
    model_name: Optional[str] = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    
    @property
    def success(self) -> bool:
        """Check if processing was successful."""
        return self.status == ProcessingStatus.SUCCESS
    
    def __bool__(self) -> bool:
        """Allow using in boolean context."""
        return self.success
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary for backward compatibility.
        
        Returns:
            Dictionary representation of the result
        """
        return {
            'success': self.success,
            'filename': self.filename,
            'status': self.status.value,
            'chunks_created': self.chunks_created,
            'processing_time': self.processing_time,
            'model_name': self.model_name,
            'error': self.error,
            **self.metadata
        }


@dataclass
class BatchProcessingResult:
    """
    Result of processing multiple documents.
    
    Attributes:
        results: List of individual processing results
        total_time: Total time for batch processing
        collection_name: ChromaDB collection used
        cleared_existing: Whether existing data was cleared
    """
    results: List[ProcessingResult]
    total_time: float
    collection_name: str
    cleared_existing: bool = False
    
    @property
    def total_documents(self) -> int:
        """Total number of documents processed."""
        return len(self.results)
    
    @property
    def successful(self) -> int:
        """Number of successfully processed documents."""
        return sum(1 for r in self.results if r.success)
    
    @property
    def failed(self) -> int:
        """Number of failed documents."""
        return sum(1 for r in self.results if not r.success)
    
    @property
    def total_chunks(self) -> int:
        """Total chunks created across all documents."""
        return sum(r.chunks_created for r in self.results if r.success)
    
    @property
    def all_successful(self) -> bool:
        """Check if all documents were processed successfully."""
        return self.failed == 0
    
    def __bool__(self) -> bool:
        """Allow using in boolean context."""
        return self.all_successful
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary for backward compatibility.
        
        Returns:
            Dictionary representation of the batch result
        """
        return {
            'total_documents': self.total_documents,
            'successful': self.successful,
            'failed': self.failed,
            'total_chunks': self.total_chunks,
            'total_time': self.total_time,
            'collection_name': self.collection_name,
            'cleared_existing': self.cleared_existing,
            'results': [r.to_dict() for r in self.results]
        }
    
    def get_summary(self) -> str:
        """
        Get human-readable summary of batch processing.
        
        Returns:
            Summary string
        """
        if self.all_successful:
            return (
                f"✅ Successfully processed {self.successful} documents: "
                f"{self.total_chunks} chunks in {self.total_time:.1f}s"
            )
        else:
            return (
                f"⚠️ {self.successful} succeeded, {self.failed} failed | "
                f"{self.total_chunks} chunks in {self.total_time:.1f}s"
            )
