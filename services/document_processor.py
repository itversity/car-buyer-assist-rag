"""
Document Processing Service

This module handles document processing operations including PDF loading,
text chunking, embedding generation, and vector storage using LangChain.
"""

import os
import re
import tempfile
from pathlib import Path
from typing import Callable, Optional, Dict, List, Any
from io import BytesIO

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langsmith import traceable
import pypdf

from config.settings import settings
from config.constants import (
    ModelConfig,
    DocumentProcessingConfig,
    PathConfig
)
from models.document_processing import (
    DocumentPreview,
    ProcessingResult,
    ProcessingStatus,
    BatchProcessingResult
)
from services.chromadb_service import ChromaDBService
from utils.logger import get_logger

logger = get_logger(__name__)

# Configure LangSmith tracing
if settings.langsmith_api_key:
    os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langsmith_tracing).lower()
    os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
    if settings.langsmith_project:
        os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
    logger.info("LangSmith tracing enabled")


class DocumentProcessor:
    """Service for processing documents through the RAG pipeline."""
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        region: Optional[str] = None
    ):
        """
        Initialize document processor.
        
        Args:
            project_id: GCP project ID. If None, uses value from settings.
            region: GCP region. If None, uses value from settings.
        """
        self.project_id = project_id or settings.google_project_id
        self.region = region or settings.google_region
        self.chromadb_service = ChromaDBService()
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=ModelConfig.EMBEDDING_MODEL_NAME,
            project=self.project_id,
            location=self.region,
            vertexai=True
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=DocumentProcessingConfig.CHUNK_SIZE,
            chunk_overlap=DocumentProcessingConfig.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        logger.info("Document processor initialized")
    
    @staticmethod
    def extract_model_name(filename: str) -> str:
        """
        Extract vehicle model name from filename.
        
        Args:
            filename: PDF filename (e.g., "Toyota_Camry_Specifications.pdf")
            
        Returns:
            Extracted model name (e.g., "Camry")
        """
        # Remove .pdf extension
        name = filename.replace('.pdf', '')
        
        # Extract model name (word between Toyota_ and _Specifications)
        # Pattern: Toyota_<MODEL>_Specifications
        match = re.search(r'Toyota[_\s]([A-Za-z0-9]+)', name)
        if match:
            return match.group(1)
        
        # Fallback: return filename without extension
        return name
    
    @staticmethod
    def get_document_preview(file) -> DocumentPreview:
        """
        Get basic preview information about a PDF file.
        
        Args:
            file: Streamlit UploadedFile object
            
        Returns:
            DocumentPreview object with file information
        """
        try:
            # Get filename and size
            filename = file.name
            size_bytes = file.size
            
            # Format size
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
            
            # Get page count
            file.seek(0)
            pdf_reader = pypdf.PdfReader(BytesIO(file.read()))
            page_count = len(pdf_reader.pages)
            file.seek(0)  # Reset file pointer
            
            # Extract model name
            model_name = DocumentProcessor.extract_model_name(filename)
            
            return DocumentPreview(
                filename=filename,
                size=size_str,
                size_bytes=size_bytes,
                pages=page_count,
                model_name=model_name
            )
            
        except Exception as e:
            logger.error(f"Failed to get preview for {file.name}: {e}", exc_info=True)
            return DocumentPreview(
                filename=file.name,
                size='Unknown',
                size_bytes=0,
                pages=0,
                model_name='Unknown',
                error=str(e)
            )
    
    @traceable(name="process_document")
    def process_document(
        self,
        file,
        collection_name: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> ProcessingResult:
        """
        Process a single PDF document through the RAG pipeline.
        
        Args:
            file: Streamlit UploadedFile object
            collection_name: Name of ChromaDB collection to store embeddings
            progress_callback: Optional callback function(progress_pct, message)
            
        Returns:
            ProcessingResult object with processing details
        """
        import time
        start_time = time.time()
        
        filename = file.name
        logger.info(f"Starting processing for {filename}")
        
        try:
            # Step 1: Save uploaded file to temporary location
            if progress_callback:
                progress_callback(0, DocumentProcessingConfig.INFO_EXTRACTING.format(filename=filename))
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(file.read())
                tmp_path = tmp_file.name
            
            try:
                # Step 2: Load PDF and extract text
                logger.debug(f"Loading PDF from {tmp_path}")
                loader = PyPDFLoader(tmp_path)
                documents = loader.load()
                
                logger.info(f"Extracted {len(documents)} pages from {filename}")
                
                if progress_callback:
                    progress_callback(33, DocumentProcessingConfig.INFO_CHUNKING)
                
                # Step 3: Split documents into chunks
                chunks = self.text_splitter.split_documents(documents)
                logger.info(f"Created {len(chunks)} chunks from {filename}")
                
                # Add metadata to chunks
                model_name = self.extract_model_name(filename)
                for i, chunk in enumerate(chunks):
                    chunk.metadata['source'] = filename
                    chunk.metadata['model_name'] = model_name
                    chunk.metadata['chunk_index'] = i
                
                if progress_callback:
                    progress_callback(66, DocumentProcessingConfig.INFO_EMBEDDING)
                
                # Step 4: Generate embeddings and store in ChromaDB
                logger.debug(f"Storing {len(chunks)} chunks in collection: {collection_name}")
                
                # Use LangChain's Chroma wrapper for seamless integration
                vectorstore = Chroma(
                    collection_name=collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=str(PathConfig.CHROMA_DB_PATH)
                )
                
                # Add documents to vector store
                vectorstore.add_documents(chunks)
                
                if progress_callback:
                    progress_callback(100, DocumentProcessingConfig.INFO_STORING)
                
                processing_time = time.time() - start_time
                
                logger.info(f"Successfully processed {filename} in {processing_time:.2f}s")
                
                return ProcessingResult(
                    filename=filename,
                    status=ProcessingStatus.SUCCESS,
                    chunks_created=len(chunks),
                    processing_time=processing_time,
                    model_name=model_name
                )
                
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    logger.debug(f"Cleaned up temporary file: {tmp_path}")
        
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Failed to process {filename}: {error_msg}", exc_info=True)
            
            return ProcessingResult(
                filename=filename,
                status=ProcessingStatus.FAILED,
                chunks_created=0,
                processing_time=processing_time,
                error=error_msg
            )
    
    @traceable(name="process_multiple_documents")
    def process_multiple_documents(
        self,
        files: List,
        collection_name: str,
        clear_existing: bool = False,
        progress_callback: Optional[Callable[[int, str, Optional[ProcessingResult]], None]] = None
    ) -> BatchProcessingResult:
        """
        Process multiple PDF documents.
        
        Args:
            files: List of Streamlit UploadedFile objects
            collection_name: Name of ChromaDB collection
            clear_existing: Whether to clear existing collection before processing
            progress_callback: Optional callback(overall_pct, message, current_doc_result)
            
        Returns:
            BatchProcessingResult with overall processing details
        """
        import time
        start_time = time.time()
        
        logger.info(f"Processing {len(files)} documents")
        
        # Clear collection if requested
        if clear_existing:
            logger.info(f"Clearing existing collection: {collection_name}")
            self.chromadb_service.clear_collection(collection_name)
        
        results: List[ProcessingResult] = []
        
        for idx, file in enumerate(files):
            # Calculate overall progress
            overall_progress = int((idx / len(files)) * 100)
            
            # Process document
            def doc_progress(pct, msg):
                if progress_callback:
                    progress_callback(overall_progress, msg, None)
            
            result = self.process_document(file, collection_name, doc_progress)
            results.append(result)
            
            # Send update with result
            if progress_callback:
                progress_callback(overall_progress, f"Completed {idx + 1}/{len(files)}", result)
        
        total_time = time.time() - start_time
        
        batch_result = BatchProcessingResult(
            results=results,
            total_time=total_time,
            collection_name=collection_name,
            cleared_existing=clear_existing
        )
        
        logger.info(
            f"Batch processing complete: {batch_result.successful} successful, "
            f"{batch_result.failed} failed, {batch_result.total_chunks} chunks"
        )
        
        return batch_result
