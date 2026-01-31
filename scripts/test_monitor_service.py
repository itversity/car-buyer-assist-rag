"""
Test script for monitor service.

This script tests the monitor service functionality by attempting to fetch
data from LangSmith and verifying the data structures.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.monitor_service import MonitorService
from models.monitoring import (
    DocumentProcessingRun,
    BatchProcessingRun,
    QueryRun,
    MonitoringSummary
)

def test_monitor_service():
    """Test monitor service functionality."""
    
    print("=" * 60)
    print("MONITOR SERVICE TEST")
    print("=" * 60)
    
    try:
        # Initialize service
        print("\n1. Initializing MonitorService...")
        service = MonitorService()
        print("   ✓ Service initialized successfully")
        
        # Test document processing runs
        print("\n2. Fetching document processing runs...")
        doc_runs = service.get_document_processing_runs(limit=5)
        print(f"   ✓ Fetched {len(doc_runs)} document processing runs")
        
        if doc_runs:
            print("\n   Sample document run:")
            run = doc_runs[0]
            print(f"   - Filename: {run.filename}")
            print(f"   - Model: {run.model_name}")
            print(f"   - Chunks: {run.chunks_created}")
            print(f"   - Duration: {run.duration_sec}s")
            print(f"   - Status: {run.status}")
            print(f"   - Timestamp: {run.timestamp_formatted}")
            
            # Test to_dict method
            run_dict = run.to_dict()
            print(f"   ✓ to_dict() works: {len(run_dict)} fields")
        else:
            print("   ⚠ No document runs found (process some documents first)")
        
        # Test batch processing runs
        print("\n3. Fetching batch processing runs...")
        batch_runs = service.get_batch_processing_runs(limit=5)
        print(f"   ✓ Fetched {len(batch_runs)} batch processing runs")
        
        if batch_runs:
            print("\n   Sample batch run:")
            run = batch_runs[0]
            print(f"   - Total docs: {run.total_documents}")
            print(f"   - Successful: {run.successful_documents}")
            print(f"   - Failed: {run.failed_documents}")
            print(f"   - Total chunks: {run.total_chunks}")
            print(f"   - Duration: {run.duration_sec}s")
        else:
            print("   ⚠ No batch runs found")
        
        # Test query runs
        print("\n4. Fetching query runs...")
        query_runs = service.get_query_runs(limit=5)
        print(f"   ✓ Fetched {len(query_runs)} query runs")
        
        if query_runs:
            print("\n   Sample query run:")
            run = query_runs[0]
            print(f"   - Question: {run.question_preview}")
            print(f"   - Answer: {run.answer_preview}")
            print(f"   - Sources: {run.sources_formatted}")
            print(f"   - Chunks: {run.retrieved_chunks}")
            print(f"   - Duration: {run.duration_sec}s")
        else:
            print("   ⚠ No query runs found (ask some questions first)")
        
        # Test summary metrics
        print("\n5. Calculating summary metrics...")
        summary = service.get_summary_metrics()
        print("   ✓ Summary metrics calculated")
        print(f"   - Total operations: {summary.total_operations}")
        print(f"   - Documents processed: {summary.total_documents_processed}")
        print(f"   - Queries executed: {summary.total_queries_executed}")
        print(f"   - Avg duration: {summary.avg_duration_formatted}")
        print(f"   - Success rate: {summary.success_rate_percent}")
        print(f"   - Last operation: {summary.last_operation_formatted}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_monitor_service()
    sys.exit(0 if success else 1)
