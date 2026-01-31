"""
Interactive Assistant Page

This page provides a chat interface for asking questions about Toyota vehicles
using the RAG (Retrieval-Augmented Generation) system with conversation context.
"""

import streamlit as st
from datetime import datetime

from config.settings import settings
from config.constants import RAGConfig
from models.chat import ChatMessage
from services.rag_service import RAGService
from utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Interactive Assistant",
    page_icon="💬",
    layout="wide"
)

# ============================================================================
# Initialize Services
# ============================================================================

@st.cache_resource
def get_rag_service():
    """Get or create RAG service instance."""
    try:
        return RAGService()
    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {e}")
        st.error(f"❌ Failed to initialize RAG service: {e}")
        st.info("Please ensure all services are properly configured on the Connectivity page.")
        return None

# ============================================================================
# Session State Initialization
# ============================================================================

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

if 'processing' not in st.session_state:
    st.session_state.processing = False

# ============================================================================
# Page Header
# ============================================================================

st.title("💬 Interactive Assistant")
st.markdown("""
Ask questions about Toyota vehicles and get instant answers powered by RAG technology. 
The assistant maintains conversation context, so you can ask follow-up questions naturally.
""")

# ============================================================================
# Check Service Status
# ============================================================================

rag_service = get_rag_service()

if rag_service is None:
    st.stop()

# Check if collection has data
collection_stats = rag_service.get_collection_stats()

if not collection_stats['exists'] or collection_stats['document_count'] == 0:
    st.warning("⚠️ No documents found in the knowledge base.")
    st.info("""
    **Getting Started:**
    1. Go to the Document Processing page
    2. Upload Toyota specification PDFs
    3. Process the documents
    4. Return here to start asking questions
    """)
    st.stop()

st.success(f"✅ Knowledge base ready with {collection_stats['document_count']} document chunks")

st.divider()

# ============================================================================
# Conversation Starters
# ============================================================================

if len(st.session_state.chat_messages) == 0:
    st.markdown("### 💡 Try These Example Questions")
    
    cols = st.columns(2)
    
    for idx, example_query in enumerate(RAGConfig.EXAMPLE_QUERIES):
        col = cols[idx % 2]
        with col:
            if st.button(
                example_query,
                key=f"example_{idx}",
                use_container_width=True
            ):
                # Set pending starter query to be processed before form
                st.session_state.pending_starter_query = example_query
                st.rerun()
    
    st.divider()

# ============================================================================
# Chat Interface
# ============================================================================

# Custom CSS for chat interface
st.markdown("""
<style>
    .user-message {
        background-color: #e3f2fd;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        margin-left: 20%;
        text-align: left;
    }
    .assistant-message {
        background-color: #f5f5f5;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        margin-right: 20%;
        text-align: left;
    }
    .message-timestamp {
        font-size: 0.75em;
        color: #666;
        margin-top: 4px;
    }
    .message-sources {
        font-size: 0.85em;
        color: #1976d2;
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# Display chat history
chat_container = st.container()

with chat_container:
    if len(st.session_state.chat_messages) == 0:
        st.info("👋 Start a conversation by typing a question below or clicking an example above!")
    else:
        for message in st.session_state.chat_messages:
            if message.role == "user":
                st.markdown(
                    f'<div class="user-message">'
                    f'<strong>You:</strong><br>{message.content}'
                    f'<div class="message-timestamp">{message.timestamp.strftime("%H:%M:%S")}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            elif message.role == "assistant":
                sources_html = ""
                if message.sources:
                    sources_text = ", ".join(message.sources)
                    sources_html = f'<div class="message-sources">📄 Sources: {sources_text}</div>'
                
                st.markdown(
                    f'<div class="assistant-message">'
                    f'<strong>Assistant:</strong><br>{message.content}'
                    f'{sources_html}'
                    f'<div class="message-timestamp">{message.timestamp.strftime("%H:%M:%S")}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

st.divider()

# ============================================================================
# Input Section
# ============================================================================

# Check if there's a pending starter query to process BEFORE form is created
if 'pending_starter_query' in st.session_state:
    starter_query = st.session_state.pending_starter_query
    del st.session_state.pending_starter_query
    
    # Process the starter query immediately
    if not st.session_state.processing:
        st.session_state.processing = True
        
        logger.info(f"User query (from starter): {starter_query}")
        
        # Add user message to history
        user_message = ChatMessage(
            role="user",
            content=starter_query,
            timestamp=datetime.now()
        )
        st.session_state.chat_messages.append(user_message)
        
        # Show processing indicator
        with st.spinner("🤔 Thinking..."):
            try:
                # Get response from RAG service
                response = rag_service.query(
                    question=starter_query,
                    conversation_history=st.session_state.chat_messages[:-1]
                )
                
                logger.info(f"Response generated in {response.processing_time:.2f}s")
                
                # Add assistant response to history
                assistant_message = ChatMessage(
                    role="assistant",
                    content=response.answer,
                    timestamp=datetime.now(),
                    sources=response.sources
                )
                st.session_state.chat_messages.append(assistant_message)
                
            except Exception as e:
                error_msg = f"Error processing query: {str(e)}"
                logger.error(error_msg, exc_info=True)
                
                # Add error message
                error_message = ChatMessage(
                    role="assistant",
                    content=f"I encountered an error: {str(e)}",
                    timestamp=datetime.now()
                )
                st.session_state.chat_messages.append(error_message)
        
        st.session_state.processing = False
        st.rerun()

# Form for manual input (handles Enter key + auto-clear)
with st.form(key="query_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([6, 1, 1])
    
    with col1:
        user_query = st.text_input(
            "Ask a question about Toyota vehicles:",
            placeholder="e.g., What are the safety features of the Corolla?",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.form_submit_button("Send", type="primary", use_container_width=True)
    
    with col3:
        # Placeholder for layout consistency
        st.empty()

# Clear Chat button outside form
if st.button("Clear Chat", use_container_width=True):
    st.session_state.chat_messages = []
    logger.info("User cleared chat history")
    st.rerun()

# Process query from form submission
if send_button and user_query and user_query.strip() and not st.session_state.processing:
    st.session_state.processing = True
    
    logger.info(f"User query: {user_query}")
    
    # Add user message to history
    user_message = ChatMessage(
        role="user",
        content=user_query,
        timestamp=datetime.now()
    )
    st.session_state.chat_messages.append(user_message)
    
    # Show processing indicator
    with st.spinner("🤔 Thinking..."):
        try:
            # Get response from RAG service
            response = rag_service.query(
                question=user_query,
                conversation_history=st.session_state.chat_messages[:-1]  # Exclude current message
            )
            
            logger.info(f"Response generated in {response.processing_time:.2f}s")
            
            # Add assistant response to history
            assistant_message = ChatMessage(
                role="assistant",
                content=response.answer,
                timestamp=datetime.now(),
                sources=response.sources
            )
            st.session_state.chat_messages.append(assistant_message)
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Add error message
            error_message = ChatMessage(
                role="assistant",
                content=f"I encountered an error: {str(e)}",
                timestamp=datetime.now()
            )
            st.session_state.chat_messages.append(error_message)
    
    st.session_state.processing = False
    st.rerun()

# ============================================================================
# Help Section
# ============================================================================

with st.expander("ℹ️ Help & Tips"):
    st.markdown("""
    ### How to Use the Assistant
    
    1. **Ask Questions**: Type your question in the input box and click Send or press Enter
    2. **Follow-up Questions**: The assistant remembers context, so you can ask follow-up questions
    3. **Example**: 
       - "What are the safety features of the Corolla?"
       - "What is the base price of it?" (The assistant understands "it" refers to Corolla)
    4. **Clear Chat**: Click the "Clear Chat" button to start a new conversation
    
    ### What the Assistant Can Answer
    
    - **Specifications**: Fuel efficiency, horsepower, dimensions, etc.
    - **Comparisons**: Compare features across different Toyota models
    - **Features**: Safety systems, technology, comfort features
    - **Pricing**: Starting prices and trim levels
    - **Recommendations**: Best vehicle for specific needs
    
    ### Tips for Best Results
    
    - Be specific in your questions
    - Mention the vehicle model name in your first question
    - Use follow-up questions to dive deeper into topics
    - Check the sources cited to verify information
    
    ### Context Management
    
    The assistant maintains the last 5 conversation turns to understand context while keeping 
    responses relevant. If you want to change topics, consider clearing the chat to start fresh.
    
    ### Observability
    
    All interactions are tracked in [LangSmith](https://smith.langchain.com/projects/{}) 
    for monitoring and debugging.
    """.format(settings.langsmith_project))

# ============================================================================
# Footer
# ============================================================================

st.divider()
st.caption(f"Powered by Vertex AI • Knowledge Base: {collection_stats['document_count']} chunks")
