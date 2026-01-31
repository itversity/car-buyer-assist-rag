"""
Operations Monitor Page

This page displays monitoring data and metrics for document processing
and query operations tracked in LangSmith.
"""

import streamlit as st
import pandas as pd

from services.monitor_service import MonitorService
from utils.logger import get_logger

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Operations Monitor",
    page_icon="📊",
    layout="wide"
)

# Page title
st.title("📊 Operations Monitor")
st.markdown("Track document processing and query operations with LangSmith observability")

st.divider()

# ============================================================================
# Refresh Button
# ============================================================================

col1, col2, col3 = st.columns([1, 1, 4])

with col1:
    if st.button("🔄 Refresh Data", type="primary"):
        st.rerun()

with col2:
    st.markdown("*Data from LangSmith*")

st.divider()

# ============================================================================
# Initialize Service and Fetch Data
# ============================================================================

try:
    monitor_service = MonitorService()
    
    # Fetch summary metrics
    with st.spinner("Loading metrics..."):
        summary = monitor_service.get_summary_metrics()
    
    # ========================================================================
    # Section 1: Summary Metrics
    # ========================================================================
    
    st.markdown("### 📈 Summary Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Operations",
            value=summary.total_operations,
            help="Total document processing + query operations"
        )
    
    with col2:
        st.metric(
            label="Average Duration",
            value=summary.avg_duration_formatted,
            help="Average processing time across all operations"
        )
    
    with col3:
        st.metric(
            label="Success Rate",
            value=summary.success_rate_percent,
            help="Percentage of successful operations"
        )
    
    # Additional metrics in a second row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Documents Processed",
            value=summary.total_documents_processed
        )
    
    with col2:
        st.metric(
            label="Queries Executed",
            value=summary.total_queries_executed
        )
    
    with col3:
        st.metric(
            label="Last Operation",
            value=summary.last_operation_formatted
        )
    
    st.divider()
    
    # ========================================================================
    # Main Operation Tabs
    # ========================================================================
    
    # Create 3 main operation tabs
    tab1, tab2, tab3 = st.tabs([
        "📄 Single Document Processing",
        "📦 Batch Processing",
        "💬 Query Operations"
    ])
    
    # ========================================================================
    # Tab 1: Single Document Processing
    # ========================================================================
    
    with tab1:
        st.markdown("### Single Document Processing Operations")
        st.markdown("Recent `process_document` runs")
        
        with st.spinner("Loading document processing runs..."):
            doc_runs = monitor_service.get_document_processing_runs(limit=10)
        
        if doc_runs:
            # Convert to DataFrame
            doc_df = pd.DataFrame([run.to_dict() for run in doc_runs])
            
            # Display table
            st.dataframe(
                doc_df[['timestamp', 'filename', 'model_name', 'chunks_created', 'duration_sec', 'status']],
                use_container_width=True,
                hide_index=True
            )
            
            # Add expandable section for LangSmith links
            with st.expander("🔗 View LangSmith Traces"):
                for run in doc_runs:
                    st.markdown(f"- **{run.filename}**: [View Trace]({run.langsmith_url})")
        else:
            st.info("No document processing runs found. Process some documents to see activity here.")
    
    # ========================================================================
    # Tab 2: Batch Processing
    # ========================================================================
    
    with tab2:
        st.markdown("### Batch Document Processing Operations")
        st.markdown("Recent `process_multiple_documents` runs")
        
        with st.spinner("Loading batch processing runs..."):
            batch_runs = monitor_service.get_batch_processing_runs(limit=10)
        
        if batch_runs:
            # Convert to DataFrame
            batch_df = pd.DataFrame([run.to_dict() for run in batch_runs])
            
            # Display table
            st.dataframe(
                batch_df[['timestamp', 'total_documents', 'successful', 'failed', 'total_chunks', 'duration_sec', 'status']],
                use_container_width=True,
                hide_index=True
            )
            
            # Add expandable section for LangSmith links
            with st.expander("🔗 View LangSmith Traces"):
                for run in batch_runs:
                    st.markdown(f"- **Batch ({run.total_documents} docs)**: [View Trace]({run.langsmith_url})")
        else:
            st.info("No batch processing runs found. Process multiple documents to see activity here.")
    
    # ========================================================================
    # Tab 3: Query Operations
    # ========================================================================
    
    with tab3:
        st.markdown("### Query Operations")
        st.markdown("Recent `rag_query` executions")
        
        with st.spinner("Loading query runs..."):
            query_runs = monitor_service.get_query_runs(limit=10)
        
        if query_runs:
            # Display summary table
            query_df = pd.DataFrame([run.to_dict() for run in query_runs])
            
            st.dataframe(
                query_df[['timestamp', 'question', 'sources', 'chunks', 'duration_sec', 'status']],
                use_container_width=True,
                hide_index=True
            )
            
            # Add expandable sections for full details
            st.markdown("#### 📝 Query Details")
            
            for i, run in enumerate(query_runs[:5], 1):  # Show details for first 5
                with st.expander(f"Query {i}: {run.question_preview}"):
                    st.markdown("**Full Question:**")
                    st.write(run.question)
                    
                    st.markdown("**Answer:**")
                    st.write(run.answer)
                    
                    st.markdown("**Sources:**")
                    if run.sources:
                        for source in run.sources:
                            st.markdown(f"- {source}")
                    else:
                        st.write("No sources")
                    
                    st.markdown("**Metadata:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Chunks Retrieved", run.retrieved_chunks)
                    with col2:
                        st.metric("Duration", f"{run.duration_sec}s")
                    with col3:
                        st.metric("Status", run.status_icon)
                    
                    st.markdown(f"[View in LangSmith]({run.langsmith_url})")
        else:
            st.info("No query runs found. Ask questions in the Interactive Assistant to see activity here.")
    
    st.divider()
    
    # ========================================================================
    # Footer Information
    # ========================================================================
    
    with st.expander("ℹ️ About This Dashboard"):
        st.markdown("""
        This monitoring dashboard displays operational data from LangSmith traces:
        
        **Data Sources:**
        - `process_document` - Individual document processing operations
        - `process_multiple_documents` - Batch document processing operations
        - `rag_query` - Interactive assistant query executions
        
        **Metrics:**
        - Duration times are measured in seconds
        - Success rate is calculated across all operation types
        - Timestamps show when operations started
        
        **Refresh:**
        - Click the "Refresh Data" button to fetch the latest data
        - Data is fetched from LangSmith on each page load
        
        **LangSmith Traces:**
        - Click trace links to view detailed execution information in LangSmith
        - Traces include full request/response data, timing, and token usage
        """)

except Exception as e:
    st.error(f"Error loading monitoring data: {str(e)}")
    logger.error(f"Monitor page error: {e}", exc_info=True)
    
    st.info("""
    **Troubleshooting:**
    - Ensure LangSmith is configured in your environment
    - Check that LANGSMITH_API_KEY is set
    - Verify the project name is correct
    - Process some documents or ask questions to generate data
    """)
