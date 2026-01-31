"""
Document Processing Page

This page allows users to upload PDF documents, preview them,
select files for processing, and track the processing pipeline.
"""

import streamlit as st
from datetime import datetime

from config.settings import settings
from config.constants import DocumentProcessingConfig, UIMessages
from models.document_processing import ProcessingStatus
from services.document_processor import DocumentProcessor
from services.chromadb_service import ChromaDBService
from utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Document Processing",
    page_icon="📄",
    layout="wide"
)

# Status constants (for backward compatibility with session state)
STATUS_NOT_PROCESSED = 'not_processed'
STATUS_PROCESSED = ProcessingStatus.SUCCESS.value
STATUS_FAILED = ProcessingStatus.FAILED.value

# ============================================================================
# Initialize Services
# ============================================================================

@st.cache_resource
def get_document_processor():
    """Get or create document processor instance."""
    try:
        return DocumentProcessor()
    except Exception as e:
        logger.error(f"Failed to initialize document processor: {e}")
        st.error(f"❌ Failed to initialize document processor: {e}")
        st.info("Please ensure all services are properly configured on the Connectivity page.")
        return None

@st.cache_resource
def get_chromadb_service():
    """Get or create ChromaDB service instance."""
    return ChromaDBService()


# ============================================================================
# Helper Functions
# ============================================================================

def get_status_badge(status, chunks=None, time=None, error=None):
    """Get status badge text with optional metadata."""
    if status == STATUS_NOT_PROCESSED:
        return 'Not Processed'
    elif status == STATUS_PROCESSED:
        if chunks and time:
            return f'✅ Processed ({chunks} chunks, {time:.1f}s)'
        return '✅ Processed'
    elif status == STATUS_FAILED:
        if error:
            return f'❌ Failed: {error[:30]}...'
        return '❌ Failed'
    return '❓ Unknown'


# ============================================================================
# Session State Initialization
# ============================================================================

if 'file_metadata' not in st.session_state:
    st.session_state.file_metadata = {}  # filename -> {preview_info, status, result}

if 'file_selection' not in st.session_state:
    st.session_state.file_selection = {}

if 'processing_in_progress' not in st.session_state:
    st.session_state.processing_in_progress = False


# ============================================================================
# Page Header
# ============================================================================

st.title("📄 Document Processing")
st.markdown("""
Upload and process Toyota specification PDFs to create the knowledge base for the RAG system.
Documents will be chunked, embedded, and stored in ChromaDB for semantic search.
""")

# ============================================================================
# File Upload Section
# ============================================================================

uploaded_files = st.file_uploader(
    "Choose PDF files to upload",
    type=['pdf'],
    accept_multiple_files=True,
    help="Upload one or more Toyota specification PDF files"
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
    
    # Get document processor
    doc_processor = get_document_processor()
    
    if doc_processor:
        # ============================================================================
        # Process and Display Document Table
        # ============================================================================
        
        # Generate preview data and initialize metadata
        preview_data = {}
        with st.spinner("Analyzing uploaded documents..."):
            for file in uploaded_files:
                if file.name not in st.session_state.file_metadata:
                    # First time seeing this file - get preview and initialize
                    preview = doc_processor.get_document_preview(file)
                    st.session_state.file_metadata[file.name] = {
                        'preview': preview,
                        'status': STATUS_NOT_PROCESSED,
                        'chunks': None,
                        'time': None,
                        'error': None
                    }
                    st.session_state.file_selection[file.name] = True  # Selected by default
                
                preview_data[file.name] = st.session_state.file_metadata[file.name]
        
        # Display unified table with selection and status
        st.markdown("#### Documents")
        
        # Table header
        col1, col2, col3, col4, col5, col6 = st.columns([0.8, 3, 1.5, 1, 1.5, 2.5])
        
        with col1:
            st.markdown("**Select**")
        with col2:
            st.markdown("**Filename**")
        with col3:
            st.markdown("**Size**")
        with col4:
            st.markdown("**Pages**")
        with col5:
            st.markdown("**Model**")
        with col6:
            st.markdown("**Status**")
        
        # Table rows
        for idx, file in enumerate(uploaded_files):
            metadata = st.session_state.file_metadata[file.name]
            preview = metadata['preview']
            
            col1, col2, col3, col4, col5, col6 = st.columns([0.8, 3, 1.5, 1, 1.5, 2.5])
            
            with col1:
                selected = st.checkbox(
                    "Select",
                    value=st.session_state.file_selection.get(file.name, True),
                    key=f"select_{idx}_{file.name}",
                    label_visibility="collapsed"
                )
                st.session_state.file_selection[file.name] = selected
            
            with col2:
                st.text(preview.filename)
            
            with col3:
                st.text(preview.size)
            
            with col4:
                st.text(str(preview.pages))
            
            with col5:
                st.text(preview.model_name)
            
            with col6:
                status_text = get_status_badge(
                    metadata['status'],
                    metadata.get('chunks'),
                    metadata.get('time'),
                    metadata.get('error')
                )
                st.text(status_text)
        
        # ============================================================================
        # Configuration Section (in expander)
        # ============================================================================
        
        with st.expander("⚙️ Configuration"):
            col1, col2 = st.columns(2)
            
            with col1:
                collection_name = st.text_input(
                    "Collection Name",
                    value=DocumentProcessingConfig.DEFAULT_COLLECTION_NAME,
                    help="Name of the ChromaDB collection to store vectors"
                )
            
            with col2:
                clear_existing = st.checkbox(
                    "Clear existing collection before processing",
                    value=False,
                    help="Delete all existing data in the collection before adding new documents"
                )
            
            # Check collection status
            chromadb_service = get_chromadb_service()
            collection_stats = chromadb_service.get_collection_stats(collection_name)
            
            if collection_stats['exists']:
                st.info(f"ℹ️ Collection '{collection_name}' exists with {collection_stats['count']} vectors")
            else:
                st.info(f"ℹ️ Collection '{collection_name}' will be created")
        
        # ============================================================================
        # Process Button and Progress Display
        # ============================================================================
        
        # Count selected files
        selected_files = [
            file for file in uploaded_files 
            if st.session_state.file_selection.get(file.name, False)
        ]
        
        # Process button
        process_disabled = len(selected_files) == 0 or st.session_state.processing_in_progress
        
        if len(selected_files) == 0:
            st.warning("⚠️ Please select at least one document to process")
        
        if st.button(
            f"🚀 Process {len(selected_files)} Selected Document(s)",
            disabled=process_disabled,
            type="primary"
        ):
            st.session_state.processing_in_progress = True
            
            logger.info(f"User initiated processing of {len(selected_files)} documents")
            
            # Create progress containers
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_expander = st.expander("📋 Processing Log", expanded=True)
            log_container = log_expander.empty()
            
            logs = []
            
            def add_log(message):
                """Add message to log display."""
                timestamp = datetime.now().strftime("%H:%M:%S")
                logs.append(f"[{timestamp}] {message}")
                log_container.text("\n".join(logs[-20:]))  # Show last 20 logs
            
            # Progress callback
            def progress_callback(overall_pct, message, doc_result):
                progress_bar.progress(min(overall_pct, 99))  # Cap at 99 until complete
                status_text.text(message)
                add_log(message)
                
                if doc_result:
                    if doc_result.success:
                        add_log(
                            f"✅ {doc_result.filename}: "
                            f"{doc_result.chunks_created} chunks in "
                            f"{doc_result.processing_time:.2f}s"
                        )
                    else:
                        add_log(f"❌ {doc_result.filename}: {doc_result.error}")
            
            # Process documents
            try:
                add_log(f"Starting processing of {len(selected_files)} documents")
                
                if clear_existing:
                    add_log(f"Clearing collection: {collection_name}")
                
                results = doc_processor.process_multiple_documents(
                    files=selected_files,
                    collection_name=collection_name,
                    clear_existing=clear_existing,
                    progress_callback=progress_callback
                )
                
                # Update session state with results
                for result in results.results:
                    filename = result.filename
                    if result.success:
                        st.session_state.file_metadata[filename]['status'] = STATUS_PROCESSED
                        st.session_state.file_metadata[filename]['chunks'] = result.chunks_created
                        st.session_state.file_metadata[filename]['time'] = result.processing_time
                    else:
                        st.session_state.file_metadata[filename]['status'] = STATUS_FAILED
                        st.session_state.file_metadata[filename]['error'] = result.error or 'Unknown error'
                
                # Complete progress
                progress_bar.progress(100)
                status_text.text("✅ Processing complete!")
                add_log("Processing complete!")
                
                # Show summary
                if results.failed == 0:
                    st.success(
                        f"✅ Processed {results.successful} documents: "
                        f"{results.total_chunks} chunks in {results.total_time:.1f}s"
                    )
                else:
                    st.warning(
                        f"⚠️ {results.successful} succeeded, {results.failed} failed | "
                        f"{results.total_chunks} chunks in {results.total_time:.1f}s"
                    )
                
                # LangSmith link
                st.info(
                    f"🔍 View detailed traces in [LangSmith]"
                    f"(https://smith.langchain.com/projects/{settings.langsmith_project})"
                )
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Processing failed: {error_msg}", exc_info=True)
                status_text.text(f"❌ Processing failed: {error_msg}")
                add_log(f"❌ Error: {error_msg}")
                st.error(f"❌ Processing failed: {error_msg}")
            
            finally:
                st.session_state.processing_in_progress = False
            
            # Trigger rerun to update the table with new statuses
            st.rerun()

else:
    st.info("👆 Upload PDF files above to get started")

# ============================================================================
# Help Section
# ============================================================================

with st.expander("ℹ️ Help & Information"):
    st.markdown("""
    ### How Document Processing Works
    
    1. **Upload**: Select one or more PDF files to upload
    2. **Select**: Choose which documents to process using checkboxes
    3. **Configure**: Set collection name and options (in Configuration section)
    4. **Process**: Click the process button to start the pipeline
    5. **Monitor**: Watch progress and check status in the documents table
    
    ### Processing Pipeline
    
    The system processes documents through these steps:
    
    1. **Text Extraction**: PyPDFLoader extracts text from PDF pages
    2. **Chunking**: RecursiveCharacterTextSplitter splits text into 1000-character chunks with 200-character overlap
    3. **Embeddings**: Vertex AI generates 768-dimension embeddings for each chunk
    4. **Storage**: Embeddings stored in ChromaDB with metadata (source, page, model name)
    
    ### Status Indicators
    
    - **Not Processed**: File uploaded but not yet processed
    - **✅ Processed**: Successfully processed with chunk and time information
    - **❌ Failed**: Processing failed (error message shown)
    
    ### Tips
    
    - Process multiple files at once for efficiency
    - Clear existing collection if you want to start fresh
    - Check the Processing Log for detailed progress
    - View LangSmith traces for observability and debugging
    - Status persists across page interactions until you upload new files
    
    ### Troubleshooting
    
    - **Connection Issues**: Verify services on the Connectivity page
    - **Processing Errors**: Check file format (must be valid PDF)
    - **Storage Issues**: Ensure sufficient disk space for ChromaDB
    """)
