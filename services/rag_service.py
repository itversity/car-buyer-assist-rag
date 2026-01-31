"""
RAG Service for Interactive Assistant.

This module handles RAG (Retrieval-Augmented Generation) operations including
query processing, context retrieval, and response generation with conversation
history management.
"""

import os
import time
from typing import List, Optional

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langsmith import traceable

from config.settings import settings
from config.constants import ModelConfig, RAGConfig, PathConfig
from models.chat import ChatMessage, RAGResponse
from utils.logger import get_logger

logger = get_logger(__name__)

# Configure LangSmith tracing
if settings.langsmith_api_key:
    os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langsmith_tracing).lower()
    os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
    if settings.langsmith_project:
        os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project


class RAGService:
    """Service for RAG operations with conversation context management."""
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        region: Optional[str] = None,
        collection_name: Optional[str] = None
    ):
        """
        Initialize RAG service.
        
        Args:
            project_id: GCP project ID. If None, uses value from settings.
            region: GCP region. If None, uses value from settings.
            collection_name: ChromaDB collection name. If None, uses default.
        """
        self.project_id = project_id or settings.google_project_id
        self.region = region or settings.google_region
        self.collection_name = collection_name or RAGConfig.DEFAULT_COLLECTION
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=ModelConfig.EMBEDDING_MODEL_NAME,
            project=self.project_id,
            location=self.region,
            vertexai=True
        )
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=ModelConfig.LLM_MODEL_NAME,
            project=self.project_id,
            location=self.region,
            temperature=RAGConfig.TEMPERATURE,
            max_output_tokens=RAGConfig.MAX_OUTPUT_TOKENS,
            vertexai=True
        )
        
        # Initialize vector store
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(PathConfig.CHROMA_DB_PATH)
        )
        
        logger.info(f"RAG service initialized with collection: {self.collection_name}")
    
    def _format_conversation_history(self, history: List[ChatMessage]) -> str:
        """
        Format conversation history for prompt.
        
        Args:
            history: List of chat messages
            
        Returns:
            Formatted conversation history string
        """
        if not history:
            return "No previous conversation."
        
        formatted = []
        for msg in history[-RAGConfig.MAX_HISTORY_TURNS:]:
            if msg.role == "user":
                formatted.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                formatted.append(f"Assistant: {msg.content}")
        
        return "\n".join(formatted)
    
    def _rewrite_query_with_llm(
        self,
        query: str,
        conversation_history: List[ChatMessage]
    ) -> str:
        """
        Use LLM to rewrite query with full context understanding.
        
        Resolves references like "it", "that", "the same" by analyzing
        conversation history semantically.
        
        Args:
            query: User's current question
            conversation_history: Previous conversation messages
            
        Returns:
            Standalone query with context incorporated
        """
        if not conversation_history or len(conversation_history) == 0:
            return query
        
        # Format recent conversation (last 3 exchanges = 6 messages)
        history_text = []
        for msg in conversation_history[-6:]:
            if msg.role == "user":
                history_text.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                # Include first 100 chars to save tokens
                content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                history_text.append(f"Assistant: {content}")
        
        history_str = "\n".join(history_text)
        
        # Create rewriting prompt
        rewrite_prompt = f"""Given the conversation history below, rewrite the user's current question to be standalone and clear by resolving any references (like "it", "that", "the same", etc.) to their actual subjects.

Conversation History:
{history_str}

Current Question: {query}

Rules:
- If the question is already clear and standalone, return it unchanged
- Only rewrite if there are unclear references that need resolution
- Keep the rewritten question natural and conversational
- Don't add information not implied by the context
- Maintain the original question's intent

Rewritten Question (just the question, nothing else):"""

        try:
            messages = [HumanMessage(content=rewrite_prompt)]
            response = self.llm.invoke(messages)
            rewritten = response.content.strip()
            
            # Sanity check: rewritten query shouldn't be dramatically longer
            if len(rewritten) > len(query) * 3:
                logger.warning(f"Rewritten query too long, using original: {rewritten[:100]}...")
                return query
            
            # Log only if actually changed
            if rewritten.lower() != query.lower():
                logger.info(f"Query rewritten: '{query}' -> '{rewritten}'")
                return rewritten
            else:
                logger.debug("Query already clear, no rewriting needed")
                return query
                
        except Exception as e:
            logger.error(f"Query rewriting failed: {e}, using original query")
            return query  # Graceful fallback
    
    def _format_retrieved_context(self, documents) -> tuple[str, List[str]]:
        """
        Format retrieved documents into context string.
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Tuple of (formatted context string, list of source filenames)
        """
        if not documents:
            return "No relevant context found.", []
        
        contexts = []
        sources = set()
        
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('source', 'Unknown')
            model_name = doc.metadata.get('model_name', 'Unknown')
            page = doc.metadata.get('page', 'Unknown')
            
            contexts.append(
                f"[Context {i} - Source: {source}, Model: {model_name}, Page: {page}]\n"
                f"{doc.page_content}\n"
            )
            sources.add(source)
        
        return "\n".join(contexts), sorted(list(sources))
    
    def _build_messages(
        self,
        query: str,
        conversation_history: str,
        retrieved_context: str
    ) -> List:
        """
        Build messages for LLM.
        
        Args:
            query: User query
            conversation_history: Formatted conversation history
            retrieved_context: Formatted retrieved context
            
        Returns:
            List of messages for LLM
        """
        messages = [
            SystemMessage(content=RAGConfig.SYSTEM_PROMPT),
            HumanMessage(content=f"""Conversation History:
{conversation_history}

Retrieved Context from Toyota Specifications:
{retrieved_context}

Current Question: {query}

Please provide a helpful answer based on the context and conversation history. Remember to cite sources and resolve any references to previous topics in the conversation.""")
        ]
        
        return messages
    
    @traceable(name="rag_query")
    def query(
        self,
        question: str,
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> RAGResponse:
        """
        Process a query using RAG with conversation context.
        
        Args:
            question: User question
            conversation_history: Optional list of previous messages for context
            
        Returns:
            RAGResponse with answer and metadata
        """
        start_time = time.time()
        conversation_history = conversation_history or []
        
        try:
            logger.info(f"Processing query: {question[:50]}...")
            
            # Step 1: Rewrite query with LLM for context resolution
            rewritten_question = self._rewrite_query_with_llm(
                question,
                conversation_history
            )
            
            # Step 2: Retrieve relevant chunks using rewritten query
            logger.debug(f"Retrieving top {RAGConfig.TOP_K_CHUNKS} chunks")
            documents = self.vectorstore.similarity_search(
                rewritten_question,
                k=RAGConfig.TOP_K_CHUNKS
            )
            
            logger.info(f"Retrieved {len(documents)} documents")
            
            # Step 3: Format conversation history
            formatted_history = self._format_conversation_history(conversation_history)
            
            # Step 4: Format retrieved context
            formatted_context, sources = self._format_retrieved_context(documents)
            
            # Step 5: Build messages
            messages = self._build_messages(
                query=question,
                conversation_history=formatted_history,
                retrieved_context=formatted_context
            )
            
            # Step 6: Generate response
            logger.debug("Generating response with LLM")
            response = self.llm.invoke(messages)
            answer = response.content
            
            processing_time = time.time() - start_time
            
            logger.info(f"Query processed successfully in {processing_time:.2f}s")
            
            return RAGResponse(
                answer=answer,
                sources=sources,
                retrieved_chunks=len(documents),
                processing_time=processing_time,
                context_used=formatted_context[:500] + "..." if len(formatted_context) > 500 else formatted_context
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Error processing query: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return RAGResponse(
                answer=f"I encountered an error processing your question: {str(e)}",
                sources=[],
                retrieved_chunks=0,
                processing_time=processing_time
            )
    
    def check_collection_exists(self) -> bool:
        """
        Check if the collection exists and has data.
        
        Returns:
            True if collection exists and has documents, False otherwise
        """
        try:
            # Try to get count from collection
            collection = self.vectorstore._collection
            count = collection.count()
            logger.debug(f"Collection '{self.collection_name}' has {count} documents")
            return count > 0
        except Exception as e:
            logger.warning(f"Collection check failed: {e}")
            return False
    
    def get_collection_stats(self) -> dict:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                'name': self.collection_name,
                'document_count': count,
                'exists': count > 0
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                'name': self.collection_name,
                'document_count': 0,
                'exists': False,
                'error': str(e)
            }
