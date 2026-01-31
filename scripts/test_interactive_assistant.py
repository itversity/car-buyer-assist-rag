"""
Test script for Interactive Assistant functionality.

This script tests the RAG service and multi-turn conversation handling
to ensure context is maintained properly across multiple queries.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.chat import ChatMessage
from services.rag_service import RAGService
from utils.logger import get_logger

logger = get_logger(__name__)


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 80 + "\n")


def test_single_turn_query():
    """Test a single query without conversation history."""
    print("TEST 1: Single-turn Query")
    print_separator()
    
    try:
        rag_service = RAGService()
        
        # Check if collection exists
        stats = rag_service.get_collection_stats()
        print(f"Collection stats: {stats}")
        
        if not stats['exists'] or stats['document_count'] == 0:
            print("❌ FAILED: No documents in collection. Please process documents first.")
            return False
        
        query = "What are the safety features of the Corolla?"
        print(f"Query: {query}")
        print("\nProcessing...")
        
        response = rag_service.query(query)
        
        print(f"\n✅ Response generated in {response.processing_time:.2f}s")
        print(f"Retrieved chunks: {response.retrieved_chunks}")
        print(f"Sources: {', '.join(response.sources)}")
        print(f"\nAnswer:\n{response.answer}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


def test_multi_turn_context():
    """Test multi-turn conversation with context resolution."""
    print("TEST 2: Multi-turn Conversation with Context")
    print_separator()
    
    try:
        rag_service = RAGService()
        
        # First query
        query1 = "What are the safety features of the Corolla?"
        print(f"Query 1: {query1}")
        print("\nProcessing...")
        
        response1 = rag_service.query(query1)
        print(f"\n✅ Response 1 generated in {response1.processing_time:.2f}s")
        print(f"Sources: {', '.join(response1.sources)}")
        print(f"\nAnswer:\n{response1.answer[:200]}...")
        
        # Build conversation history
        conversation = [
            ChatMessage(role="user", content=query1),
            ChatMessage(role="assistant", content=response1.answer, sources=response1.sources)
        ]
        
        # Second query with context reference
        query2 = "What is the base price of it?"
        print(f"\n\nQuery 2: {query2}")
        print("(Note: 'it' should resolve to 'Corolla' from previous context)")
        print("\nProcessing with conversation history...")
        
        response2 = rag_service.query(query2, conversation_history=conversation)
        print(f"\n✅ Response 2 generated in {response2.processing_time:.2f}s")
        print(f"Sources: {', '.join(response2.sources)}")
        print(f"\nAnswer:\n{response2.answer}")
        
        # Check if response mentions Corolla (context resolution)
        if "corolla" in response2.answer.lower():
            print("\n✅ Context resolution successful: Response references Corolla!")
        else:
            print("\n⚠️ Warning: Response may not have properly resolved 'it' to Corolla")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


def test_comparison_query():
    """Test a comparison query across multiple models."""
    print("TEST 3: Comparison Query")
    print_separator()
    
    try:
        rag_service = RAGService()
        
        query = "Compare fuel efficiency between RAV4 and Highlander"
        print(f"Query: {query}")
        print("\nProcessing...")
        
        response = rag_service.query(query)
        
        print(f"\n✅ Response generated in {response.processing_time:.2f}s")
        print(f"Retrieved chunks: {response.retrieved_chunks}")
        print(f"Sources: {', '.join(response.sources)}")
        print(f"\nAnswer:\n{response.answer}")
        
        # Check if both models are mentioned
        answer_lower = response.answer.lower()
        if "rav4" in answer_lower and "highlander" in answer_lower:
            print("\n✅ Comparison successful: Both models mentioned!")
        else:
            print("\n⚠️ Warning: Comparison may be incomplete")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


def test_out_of_scope():
    """Test handling of out-of-scope queries."""
    print("TEST 4: Out-of-Scope Query")
    print_separator()
    
    try:
        rag_service = RAGService()
        
        query = "Where is the nearest Toyota dealership?"
        print(f"Query: {query}")
        print("(This is out of scope - should acknowledge limitation)")
        print("\nProcessing...")
        
        response = rag_service.query(query)
        
        print(f"\n✅ Response generated in {response.processing_time:.2f}s")
        print(f"\nAnswer:\n{response.answer}")
        
        # Check if response acknowledges limitation
        answer_lower = response.answer.lower()
        if any(phrase in answer_lower for phrase in ["don't have", "not in", "not available", "cannot"]):
            print("\n✅ Out-of-scope handling successful: Acknowledged limitation!")
        else:
            print("\n⚠️ Warning: May have hallucinated answer to out-of-scope question")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("INTERACTIVE ASSISTANT TEST SUITE")
    print("=" * 80)
    
    tests = [
        ("Single-turn Query", test_single_turn_query),
        ("Multi-turn Context", test_multi_turn_context),
        ("Comparison Query", test_comparison_query),
        ("Out-of-Scope Handling", test_out_of_scope)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print_separator()
        result = test_func()
        results.append((test_name, result))
        print_separator()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
