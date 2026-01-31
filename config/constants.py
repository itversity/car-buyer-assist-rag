"""
Application constants for Car Buyer Assist RAG Application.

This module contains all magic strings, numbers, and configuration values
that are used throughout the application.
"""

from pathlib import Path


class ModelConfig:
    """Configuration for AI models."""
    
    # Embedding model
    EMBEDDING_MODEL_NAME = "text-embedding-004"
    EMBEDDING_DIMENSIONS = 768
    
    # LLM model
    LLM_MODEL_NAME = "gemini-2.0-flash-exp"
    LLM_TEMPERATURE = 0.0
    
    # Model response settings
    LLM_MAX_OUTPUT_TOKENS = 1024


class PathConfig:
    """Configuration for file paths."""
    
    # Database paths
    CHROMA_DB_PATH = Path("./chroma_db")
    
    # Credential paths
    CREDENTIALS_DIR = Path("./credentials")
    
    # Data paths
    DATA_DIR = Path("./data")
    
    # Log paths
    LOG_DIR = Path("./logs")
    LOG_FILE = LOG_DIR / "app.log"


class ValidationConfig:
    """Configuration for validation operations."""
    
    # Test collection name for connectivity testing
    TEST_COLLECTION_NAME = "connectivity_test"
    
    # Test document for validation
    TEST_DOCUMENT = "Test document for connectivity validation"
    TEST_DOCUMENT_ID = "test_id_1"
    TEST_METADATA = {"type": "test"}
    
    # Test text for embeddings
    TEST_EMBEDDING_TEXT = "Toyota Corolla sedan"
    
    # Test prompt for LLM
    TEST_LLM_PROMPT = "Say 'OK' if you can respond"
    TEST_LLM_RESPONSE_MAX_LENGTH = 50


class DocumentProcessingConfig:
    """Configuration for document processing operations."""
    
    # Chunking parameters
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Collection settings
    DEFAULT_COLLECTION_NAME = "toyota_specs"
    
    # Processing settings
    BATCH_SIZE = 10  # For batch embedding
    
    # UI Messages
    SUCCESS_PROCESSING = "✅ Successfully processed {count} documents"
    ERROR_PROCESSING = "❌ Failed to process {filename}: {error}"
    INFO_EXTRACTING = "📄 Extracting text from {filename}..."
    INFO_CHUNKING = "✂️ Chunking text into segments..."
    INFO_EMBEDDING = "🔢 Generating embeddings..."
    INFO_STORING = "💾 Storing vectors in ChromaDB..."


class RAGConfig:
    """Configuration for RAG (Retrieval-Augmented Generation) operations."""
    
    # Retrieval settings
    TOP_K_CHUNKS = 5
    
    # Context settings
    MAX_HISTORY_TURNS = 5
    
    # LLM settings for RAG
    TEMPERATURE = 0.3
    MAX_OUTPUT_TOKENS = 1024
    
    # Collection name
    DEFAULT_COLLECTION = "toyota_specs"
    
    # System prompt for RAG
    SYSTEM_PROMPT = """You are a helpful Toyota car sales assistant. Answer questions based ONLY on the provided context from Toyota specification documents and the conversation history. 

If the information is not in the context, say "I don't have that information in the available Toyota specifications." 

Always cite the source document when providing answers. Use the conversation history to resolve references like "it", "that car", "the vehicle", etc. to the specific car model mentioned earlier in the conversation.

Format your response clearly and professionally."""
    
    # Conversation starters
    EXAMPLE_QUERIES = [
        "What are the safety features of the Corolla?",
        "Compare fuel efficiency between RAV4 and Highlander",
        "What is the towing capacity of the Tacoma?",
        "Which Toyota hybrid has the longest electric range?"
    ]


class UIMessages:
    """UI messages and labels."""
    
    # Success messages
    SUCCESS_ENV_VARS = "✅ All required environment variables are set"
    SUCCESS_CHROMADB = "✅ ChromaDB connected successfully"
    SUCCESS_EMBEDDINGS = "✅ Embeddings model ({model}) connected"
    SUCCESS_LLM = "✅ LLM model ({model}) connected"
    SUCCESS_LANGSMITH = "✅ LangSmith connected successfully"
    SUCCESS_ALL_SERVICES = "✅ All services connected successfully ({successful}/{total})"
    
    # Error messages
    ERROR_ENV_VARS = "❌ Missing required environment variables: {missing}"
    ERROR_CHROMADB_IMPORT = "❌ ChromaDB not installed. Run: pip install chromadb"
    ERROR_CHROMADB_PERMISSION = "❌ Permission denied: {error}"
    ERROR_CHROMADB_FAILED = "❌ ChromaDB validation failed: {error}"
    ERROR_VERTEX_IMPORT = "❌ Required package not installed: {error}"
    ERROR_VERTEX_AUTH = "❌ Authentication failed: Invalid or missing GCP credentials"
    ERROR_VERTEX_PERMISSION = "❌ Permission denied: Check IAM roles (aiplatform.user required)"
    ERROR_VERTEX_MODEL_NOT_FOUND = "❌ Model not found: Verify model name and region"
    ERROR_VERTEX_API_NOT_ENABLED = "❌ Vertex AI API not enabled: Enable it in GCP Console"
    ERROR_VERTEX_QUOTA = "❌ Quota exceeded: Check GCP quota limits"
    ERROR_VERTEX_FAILED = "❌ Vertex AI validation failed: {error}"
    ERROR_EMBEDDING_DIMENSIONS = "❌ Unexpected embedding dimensions: {actual} (expected {expected})"
    ERROR_LLM_NO_RESPONSE = "❌ No response received from LLM"
    ERROR_LANGSMITH_IMPORT = "❌ LangSmith not installed. Run: pip install langsmith"
    ERROR_LANGSMITH_AUTH = "❌ Invalid API key: Check LANGSMITH_API_KEY"
    ERROR_LANGSMITH_NETWORK = "❌ Network error: Check internet connection"
    ERROR_LANGSMITH_LIST_PROJECTS = "❌ Failed to list projects: {error}"
    ERROR_LANGSMITH_FAILED = "❌ LangSmith validation failed: {error}"
    
    # Warning messages
    WARNING_PROJECT_NOT_FOUND = "⚠️ Project '{project}' not found (will be created on first use)"
    WARNING_PARTIAL_SUCCESS = "⚠️ {successful}/{total} services connected successfully"
    
    # Info messages
    INFO_ENV_CONFIG_PROMPT = "👆 Please configure the required environment variables before testing connections."
    INFO_TEST_PROMPT = "👆 Click the button above to test all connections."
    INFO_REVIEW_ERRORS = "Review the error messages above and check your configuration."
