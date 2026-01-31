"""
Connectivity Validation Page

This page validates connectivity to all external services required by the
Car Buyer Assist RAG application:
- ChromaDB (Vector Database)
- Google Vertex AI (Embeddings and LLM)
- LangSmith (Observability)
"""

import streamlit as st

from config.settings import settings
from config.constants import UIMessages
from services.connectivity_validator import ConnectivityValidator
from utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Connectivity Validation",
    page_icon="🔌",
    layout="centered"
)

# Page header
st.title("🔌 Connectivity Validation")
st.markdown("""
Verify all external service connections before processing documents or running queries.
This page will test connectivity to ChromaDB, Google Vertex AI, and LangSmith.
""")

st.divider()


# ============================================================================
# Environment Variable Validation UI
# ============================================================================

def display_environment_status() -> bool:
    """
    Display environment variable status in the UI.
    
    Returns:
        True if all required environment variables are set, False otherwise
    """
    st.subheader("Environment Configuration")
    
    # Create validator instance
    validator = ConnectivityValidator()
    
    # Check environment configuration
    all_set, config, missing = validator.validate_environment()
    
    if all_set:
        st.success(UIMessages.SUCCESS_ENV_VARS)
        
        with st.expander("View Configuration"):
            st.write("**Google Cloud Platform:**")
            st.code(f"""
Project ID: {config['GOOGLE_PROJECT_ID']}
Region: {config['GOOGLE_REGION']}
Credentials: {config['GOOGLE_APPLICATION_CREDENTIALS']}
            """)
            
            st.write("**LangSmith:**")
            api_key = config['LANGSMITH_API_KEY']
            masked_key = '*' * 20 + api_key[-4:] if api_key and len(api_key) >= 4 else 'Not Set'
            st.code(f"""
Project: {config['LANGSMITH_PROJECT']}
Tracing: {config['LANGSMITH_TRACING']}
API Key: {masked_key}
            """)
    else:
        st.error(UIMessages.ERROR_ENV_VARS.format(missing=', '.join(missing)))
        st.info("""
        **Setup Instructions:**
        1. Create a `.env` file in the project root
        2. Add the missing environment variables
        3. For GCP setup, run: `python scripts/setup/setup_gcp_sa.py`
        4. For LangSmith, get your API key from: https://smith.langchain.com/settings
        """)
    
    return all_set


# ============================================================================
# Main UI
# ============================================================================

# Display environment status first
env_configured = display_environment_status()

st.divider()

# Initialize session state for results if not exists
if 'validation_results' not in st.session_state:
    st.session_state.validation_results = None

# Test button (only enabled if environment is configured)
if st.button("🔍 Test All Connections", disabled=not env_configured, type="primary"):
    logger.info("User initiated connectivity validation")
    
    st.subheader("Validation Results")
    
    # Create validator instance
    validator = ConnectivityValidator()
    
    # Test ChromaDB
    with st.spinner("Testing ChromaDB..."):
        chroma_result = validator.validate_chromadb()
    
    if chroma_result.success:
        st.success(chroma_result.message)
    else:
        st.error(chroma_result.message)
    
    st.divider()
    
    # Test Vertex AI Embeddings
    with st.spinner("Testing Vertex AI Embeddings..."):
        embed_result = validator.validate_vertex_ai_embeddings()
    
    if embed_result.success:
        st.success(embed_result.message)
    else:
        st.error(embed_result.message)
    
    st.divider()
    
    # Test Vertex AI LLM
    with st.spinner("Testing Vertex AI LLM..."):
        llm_result = validator.validate_vertex_ai_llm()
    
    if llm_result.success:
        st.success(llm_result.message)
    else:
        st.error(llm_result.message)
    
    st.divider()
    
    # Test LangSmith
    with st.spinner("Testing LangSmith..."):
        langsmith_result = validator.validate_langsmith()
    
    if langsmith_result.success:
        st.success(langsmith_result.message)
    else:
        st.error(langsmith_result.message)
    
    st.divider()
    
    # Summary
    st.subheader("Summary")
    
    all_services = [
        ("ChromaDB", chroma_result.success),
        ("Vertex AI Embeddings", embed_result.success),
        ("Vertex AI LLM", llm_result.success),
        ("LangSmith", langsmith_result.success)
    ]
    
    successful = sum(1 for _, success in all_services if success)
    total = len(all_services)
    
    if successful == total:
        message = UIMessages.SUCCESS_ALL_SERVICES.format(
            successful=successful,
            total=total
        )
        st.success(message)
        st.balloons()
        logger.info(f"All connectivity validations passed ({successful}/{total})")
    else:
        message = UIMessages.WARNING_PARTIAL_SUCCESS.format(
            successful=successful,
            total=total
        )
        st.warning(message)
        st.info(UIMessages.INFO_REVIEW_ERRORS)
        logger.warning(f"Partial connectivity validation ({successful}/{total} passed)")

else:
    if not env_configured:
        st.info(UIMessages.INFO_ENV_CONFIG_PROMPT)
    else:
        st.info(UIMessages.INFO_TEST_PROMPT)

# Help section
st.divider()
with st.expander("ℹ️ Help & Troubleshooting"):
    st.markdown("""
    ### Common Issues
    
    **ChromaDB Issues:**
    - Ensure write permissions in the project directory
    - Check available disk space
    
    **Vertex AI Issues:**
    - Verify `GOOGLE_APPLICATION_CREDENTIALS` points to valid service account key
    - Ensure Vertex AI API is enabled in GCP Console
    - Check IAM roles: `roles/aiplatform.user` required
    - Verify project ID and region are correct
    
    **LangSmith Issues:**
    - Get API key from: https://smith.langchain.com/settings
    - Verify API key is valid and not expired
    - Check internet connectivity
    
    ### Setup Scripts
    - GCP Service Account: `python scripts/setup/setup_gcp_sa.py`
    - LangSmith Validation: `python scripts/setup/langsmith_validate.py`
    
    ### Required Environment Variables
    ```
    GOOGLE_APPLICATION_CREDENTIALS=./credentials/gcp-service-account-key.json
    GOOGLE_PROJECT_ID=your-project-id
    GOOGLE_REGION=us-central1
    LANGSMITH_API_KEY=your-api-key
    LANGSMITH_PROJECT=your-project-name
    LANGSMITH_TRACING=true
    ```
    """)
