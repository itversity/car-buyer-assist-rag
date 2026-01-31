"""
Car Buyer Assist RAG Application - Landing Page
"""

import streamlit as st
from services.chromadb_service import ChromaDBService
from services.monitor_service import MonitorService
from config.constants import RAGConfig
from utils.logger import get_logger

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Car Buyer Assist RAG",
    page_icon="🚗",
    layout="wide"
)

# Application title
st.title("🚗 Car Buyer Assist RAG Application")

# Brief description
st.markdown("""
A conversational AI system that helps prospective car buyers get instant, accurate answers 
about Toyota vehicles using Retrieval-Augmented Generation (RAG) technology.
""")

st.divider()

# ============================================================================
# System Health Status
# ============================================================================

# Fetch data from services with error handling
try:
    chromadb_service = ChromaDBService()
    collection_stats = chromadb_service.get_collection_stats(RAGConfig.DEFAULT_COLLECTION)
    collection_exists = collection_stats.get('exists', False)
    chunk_count = collection_stats.get('count', 0)
except Exception as e:
    logger.error(f"Error fetching ChromaDB stats: {e}")
    collection_exists = False
    chunk_count = 0

try:
    monitor_service = MonitorService()
    summary = monitor_service.get_summary_metrics()
    has_operations = summary.total_operations > 0
except Exception as e:
    logger.error(f"Error fetching monitoring summary: {e}")
    summary = None
    has_operations = False

# Determine system health
if collection_exists and chunk_count > 0 and has_operations:
    health_status = "🟢 System Healthy"
    health_color = "green"
elif collection_exists and chunk_count > 0:
    health_status = "🟡 Ready (No queries yet)"
    health_color = "orange"
elif has_operations:
    health_status = "🟡 Active (No documents)"
    health_color = "orange"
else:
    health_status = "⚪ Not Initialized"
    health_color = "gray"

st.markdown(f"**System Status:** :{health_color}[{health_status}]")

st.divider()

# ============================================================================
# Enhanced Metrics Dashboard
# ============================================================================

st.markdown("### 📊 System Metrics")

# Row 1: Primary metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Vector Database Chunks",
        value=f"{chunk_count:,}" if chunk_count > 0 else "0",
        help="Total chunks stored in ChromaDB"
    )

with col2:
    if summary:
        st.metric(
            label="Total Queries Executed",
            value=summary.total_queries_executed,
            help="Total number of queries processed by the RAG system"
        )
    else:
        st.metric(label="Total Queries Executed", value="N/A")

with col3:
    if summary and summary.avg_duration_sec > 0:
        st.metric(
            label="Avg Query Duration",
            value=summary.avg_duration_formatted,
            help="Average time to process a query"
        )
    else:
        st.metric(label="Avg Query Duration", value="N/A")

# Row 2: Secondary metrics
col1, col2, col3 = st.columns(3)

with col1:
    if summary and summary.total_operations > 0:
        st.metric(
            label="Success Rate",
            value=summary.success_rate_percent,
            help="Percentage of successful operations"
        )
    else:
        st.metric(label="Success Rate", value="N/A")

with col2:
    if summary:
        st.metric(
            label="Documents Processed",
            value=summary.total_documents_processed,
            help="Total documents processed and stored"
        )
    else:
        st.metric(label="Documents Processed", value="N/A")

with col3:
    if summary and summary.last_operation_time:
        st.metric(
            label="Last Operation",
            value=summary.last_operation_formatted,
            help="Timestamp of the most recent operation"
        )
    else:
        st.metric(label="Last Operation", value="Never")

st.divider()

# ============================================================================
# Recent Activity
# ============================================================================

st.markdown("### 📋 Recent Activity")

if summary and has_operations:
    try:
        # Fetch recent operations (mix of doc processing and queries)
        doc_runs = monitor_service.get_document_processing_runs(limit=3)
        query_runs = monitor_service.get_query_runs(limit=3)
        
        # Combine and sort by timestamp
        recent_operations = []
        
        for run in doc_runs:
            recent_operations.append({
                'timestamp': run.timestamp,
                'type': 'Document',
                'description': f"Processed {run.filename} ({run.chunks_created} chunks)",
                'status': run.status_icon
            })
        
        for run in query_runs:
            recent_operations.append({
                'timestamp': run.timestamp,
                'type': 'Query',
                'description': run.question_preview,
                'status': run.status_icon
            })
        
        # Sort by timestamp (most recent first) and take top 5
        recent_operations.sort(key=lambda x: x['timestamp'], reverse=True)
        recent_operations = recent_operations[:5]
        
        if recent_operations:
            # Display as a simple table
            for op in recent_operations:
                col1, col2, col3, col4 = st.columns([2, 1.5, 5, 0.8])
                with col1:
                    st.text(op['timestamp'].strftime('%m-%d %H:%M'))
                with col2:
                    st.text(op['type'])
                with col3:
                    st.text(op['description'])
                with col4:
                    st.text(op['status'])
            
            st.markdown("*View more details on the [Operations Monitor](monitor) page*")
        else:
            st.info("No recent operations found. Process documents or ask questions to see activity here.")
    
    except Exception as e:
        logger.error(f"Error fetching recent activity: {e}")
        st.info("Unable to load recent activity. Check the Operations Monitor page for details.")
else:
    st.info("No operations recorded yet. Process documents and ask questions to see activity here.")

st.divider()

# ============================================================================
# Navigation Cards
# ============================================================================

st.markdown("### 🧭 Quick Navigation")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 🔌 1. Connectivity Validation
    Verify connections to all external services:
    - ChromaDB (Vector Database)
    - Google Vertex AI (Embeddings & LLM)
    - LangSmith (Observability)
    
    **Start here** if this is your first time using the application.
    """)

with col2:
    st.markdown("""
    #### 📄 2. Document Processing
    Upload and process Toyota specification PDFs:
    - Extract text from PDFs
    - Generate embeddings
    - Store in vector database
    
    **Process documents** before using the assistant.
    """)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 💬 3. Interactive Assistant
    Ask questions about Toyota vehicles:
    - Natural language queries
    - Multi-turn conversations
    - Context-aware responses
    - Source citations
    
    **Chat with the AI** to get vehicle information.
    """)

with col2:
    st.markdown("""
    #### 📊 4. Operations Monitor
    View system metrics and recent activity:
    - Document processing operations
    - Query execution traces
    - Performance metrics
    - LangSmith integration
    
    **Monitor** the system's operations and performance.
    """)

st.divider()

# ============================================================================
# Getting Started
# ============================================================================

st.markdown("### 🚀 Getting Started")

st.markdown("""
Follow these steps to use the Car Buyer Assist RAG Application:

1. **Connectivity Validation** - Go to the Connectivity page and test all service connections
2. **Document Processing** - Upload and process Toyota specification PDFs on the Document Processing page
3. **Interactive Assistant** - Start asking questions about Toyota vehicles on the Interactive Assistant page
4. **Operations Monitor** - View system performance and trace data on the Monitor page

**Example Conversation:**
- **You:** "What are the safety features of the Corolla?"
- **Assistant:** *Provides detailed safety features with citations*
- **You:** "What is the base price of it?"
- **Assistant:** *Understands "it" refers to Corolla and provides pricing*
""")

st.divider()

# ============================================================================
# Technology Stack
# ============================================================================

with st.expander("🛠️ Technology Stack"):
    st.markdown("""
    - **Frontend**: Streamlit
    - **Orchestration**: LangChain
    - **Vector Database**: ChromaDB
    - **LLM & Embeddings**: Google Vertex AI (Gemini 2.0 Flash, text-embedding-004)
    - **Observability**: LangSmith
    - **Language**: Python 3.11+
    """)
