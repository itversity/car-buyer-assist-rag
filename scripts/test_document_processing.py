"""
Test script for document processing functionality.

This script tests the document processing pipeline without running the full Streamlit app.
It verifies that all components are working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.document_processor import DocumentProcessor
from services.chromadb_service import ChromaDBService
from config.constants import DocumentProcessingConfig
from utils.logger import get_logger

logger = get_logger(__name__)


def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    
    try:
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_chroma import Chroma
        from langsmith import traceable
        import pypdf
        
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_services_initialization():
    """Test that services can be initialized."""
    print("\nTesting service initialization...")
    
    try:
        # Test ChromaDB service
        chromadb_service = ChromaDBService()
        print("✅ ChromaDB service initialized")
        
        # Test document processor
        doc_processor = DocumentProcessor()
        print("✅ Document processor initialized")
        
        return True
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False


def test_collection_operations():
    """Test ChromaDB collection operations."""
    print("\nTesting collection operations...")
    
    try:
        chromadb_service = ChromaDBService()
        
        # Test list collections
        collections = chromadb_service.list_collections()
        print(f"✅ Found {len(collections)} existing collections: {collections}")
        
        # Test get collection stats
        test_collection = "test_collection"
        stats = chromadb_service.get_collection_stats(test_collection)
        print(f"✅ Collection stats retrieved: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ Collection operations error: {e}")
        return False


def test_model_name_extraction():
    """Test model name extraction from filenames."""
    print("\nTesting model name extraction...")
    
    test_cases = [
        ("Toyota_Camry_Specifications.pdf", "Camry"),
        ("Toyota_RAV4_Specifications.pdf", "RAV4"),
        ("Toyota_bZ4X_Specifications.pdf", "bZ4X"),
        ("Toyota_Corolla_Specifications.pdf", "Corolla"),
    ]
    
    all_passed = True
    for filename, expected in test_cases:
        result = DocumentProcessor.extract_model_name(filename)
        if result == expected:
            print(f"✅ {filename} -> {result}")
        else:
            print(f"❌ {filename} -> {result} (expected {expected})")
            all_passed = False
    
    return all_passed


def test_configuration():
    """Test configuration values."""
    print("\nTesting configuration...")
    
    try:
        print(f"Chunk size: {DocumentProcessingConfig.CHUNK_SIZE}")
        print(f"Chunk overlap: {DocumentProcessingConfig.CHUNK_OVERLAP}")
        print(f"Default collection: {DocumentProcessingConfig.DEFAULT_COLLECTION_NAME}")
        print(f"Batch size: {DocumentProcessingConfig.BATCH_SIZE}")
        
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Document Processing Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Service Initialization", test_services_initialization),
        ("Collection Operations", test_collection_operations),
        ("Model Name Extraction", test_model_name_extraction),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
