"""
Chat models for interactive assistant.

This module contains data structures for chat operations including
messages, responses, and conversation management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class ChatMessage:
    """Represents a single message in the conversation."""
    
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    sources: Optional[List[str]] = None
    
    def to_dict(self) -> dict:
        """Convert message to dictionary."""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'sources': self.sources
        }


@dataclass
class RAGResponse:
    """Response from RAG query processing."""
    
    answer: str
    sources: List[str]
    retrieved_chunks: int
    processing_time: float
    context_used: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Check if response was successful."""
        return bool(self.answer)
    
    def to_dict(self) -> dict:
        """Convert response to dictionary."""
        return {
            'answer': self.answer,
            'sources': self.sources,
            'retrieved_chunks': self.retrieved_chunks,
            'processing_time': self.processing_time,
            'context_used': self.context_used
        }
