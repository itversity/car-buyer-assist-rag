"""
Monitoring data models.

This module defines data classes for monitoring operations tracked in LangSmith,
ensuring type safety and consistent data structures.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class DocumentProcessingRun:
    """
    Single document processing operation trace from LangSmith.
    
    Attributes:
        run_id: Unique identifier for the LangSmith run
        timestamp: When the processing started
        filename: Name of the processed document
        model_name: Extracted vehicle model name
        chunks_created: Number of chunks created
        duration_sec: Processing duration in seconds
        status: Run status (success, error, etc.)
        langsmith_url: Direct link to LangSmith trace
    """
    run_id: str
    timestamp: datetime
    filename: str
    model_name: str
    chunks_created: int
    duration_sec: float
    status: str
    langsmith_url: str
    
    @property
    def timestamp_formatted(self) -> str:
        """Format timestamp for display."""
        return self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    @property
    def status_icon(self) -> str:
        """Get status icon."""
        return "✅" if self.status == "success" else "❌"
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary for Streamlit display.
        
        Returns:
            Dictionary representation of the run
        """
        return {
            'timestamp': self.timestamp_formatted,
            'filename': self.filename,
            'model_name': self.model_name,
            'chunks_created': self.chunks_created,
            'duration_sec': self.duration_sec,
            'status': self.status_icon,
            'run_id': self.run_id,
            'langsmith_url': self.langsmith_url
        }


@dataclass
class BatchProcessingRun:
    """
    Batch document processing operation trace from LangSmith.
    
    Attributes:
        run_id: Unique identifier for the LangSmith run
        timestamp: When the batch processing started
        total_documents: Total number of documents in batch
        successful_documents: Number of successfully processed documents
        failed_documents: Number of failed documents
        total_chunks: Total chunks created across all documents
        duration_sec: Processing duration in seconds
        status: Run status (success, error, etc.)
        langsmith_url: Direct link to LangSmith trace
    """
    run_id: str
    timestamp: datetime
    total_documents: int
    successful_documents: int
    failed_documents: int
    total_chunks: int
    duration_sec: float
    status: str
    langsmith_url: str
    
    @property
    def timestamp_formatted(self) -> str:
        """Format timestamp for display."""
        return self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    @property
    def status_icon(self) -> str:
        """Get status icon."""
        return "✅" if self.status == "success" else "❌"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_documents == 0:
            return 0.0
        return self.successful_documents / self.total_documents
    
    @property
    def success_rate_percent(self) -> str:
        """Format success rate as percentage."""
        return f"{self.success_rate * 100:.1f}%"
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary for Streamlit display.
        
        Returns:
            Dictionary representation of the run
        """
        return {
            'timestamp': self.timestamp_formatted,
            'total_documents': self.total_documents,
            'successful': self.successful_documents,
            'failed': self.failed_documents,
            'total_chunks': self.total_chunks,
            'duration_sec': self.duration_sec,
            'status': self.status_icon,
            'run_id': self.run_id,
            'langsmith_url': self.langsmith_url
        }


@dataclass
class QueryRun:
    """
    RAG query operation trace from LangSmith.
    
    Attributes:
        run_id: Unique identifier for the LangSmith run
        timestamp: When the query was executed
        question: User's question
        answer: Generated answer
        sources: List of source documents used
        retrieved_chunks: Number of chunks retrieved
        duration_sec: Query processing duration in seconds
        status: Run status (success, error, etc.)
        langsmith_url: Direct link to LangSmith trace
    """
    run_id: str
    timestamp: datetime
    question: str
    answer: str
    sources: List[str]
    retrieved_chunks: int
    duration_sec: float
    status: str
    langsmith_url: str
    
    @property
    def timestamp_formatted(self) -> str:
        """Format timestamp for display."""
        return self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    @property
    def question_preview(self) -> str:
        """Truncate question for table display."""
        return (self.question[:60] + '...') if len(self.question) > 60 else self.question
    
    @property
    def answer_preview(self) -> str:
        """Truncate answer for table display."""
        return (self.answer[:100] + '...') if len(self.answer) > 100 else self.answer
    
    @property
    def sources_formatted(self) -> str:
        """Format sources as comma-separated string."""
        return ', '.join(self.sources) if self.sources else 'No sources'
    
    @property
    def status_icon(self) -> str:
        """Get status icon."""
        return "✅" if self.status == "success" else "❌"
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary for Streamlit display.
        
        Returns:
            Dictionary representation of the run
        """
        return {
            'timestamp': self.timestamp_formatted,
            'question': self.question_preview,
            'sources': self.sources_formatted,
            'chunks': self.retrieved_chunks,
            'duration_sec': self.duration_sec,
            'status': self.status_icon,
            'run_id': self.run_id,
            'langsmith_url': self.langsmith_url
        }


@dataclass
class MonitoringSummary:
    """
    Aggregate monitoring metrics across all operations.
    
    Attributes:
        total_operations: Total number of operations (docs + queries)
        total_documents_processed: Total documents processed
        total_queries_executed: Total queries executed
        avg_duration_sec: Average operation duration in seconds
        success_rate: Success rate as decimal (0.0 to 1.0)
        last_operation_time: Timestamp of most recent operation
    """
    total_operations: int
    total_documents_processed: int
    total_queries_executed: int
    avg_duration_sec: float
    success_rate: float  # 0.0 to 1.0
    last_operation_time: Optional[datetime] = None
    
    @property
    def success_rate_percent(self) -> str:
        """Format success rate as percentage."""
        return f"{self.success_rate * 100:.1f}%"
    
    @property
    def avg_duration_formatted(self) -> str:
        """Format average duration."""
        return f"{self.avg_duration_sec:.2f}s"
    
    @property
    def last_operation_formatted(self) -> str:
        """Format last operation time."""
        if self.last_operation_time:
            return self.last_operation_time.strftime('%Y-%m-%d %H:%M:%S')
        return "N/A"
