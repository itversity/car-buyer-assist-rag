# Batch Processing Data Extraction Fix

## Issue

The Batch Document Processing Operations tab was showing zeros (0) for all metrics:
- `total_documents`: 0
- `successful`: 0
- `failed`: 0
- `total_chunks`: 0

## Root Cause

The `monitor_service.py` was expecting the wrong data structure for `process_multiple_documents` runs. 

**Expected Structure (incorrect):**
```python
output_data = {
    'total_documents': 8,
    'successful': 8,
    'failed': 0,
    'total_chunks': 32
}
```

**Actual Structure (from LangSmith):**
```python
output_data = {
    'cleared_existing': True,
    'collection_name': 'toyota_specs',
    'results': [
        {
            'filename': 'Toyota_Camry_Specifications.pdf',
            'status': 'success',
            'chunks_created': 4,
            'model_name': 'Camry',
            'processing_time': 0.72
        },
        # ... more results
    ],
    'total_time': 6.95
}
```

## Solution

Modified `services/monitor_service.py` (lines 133-140) to calculate metrics from the `results` array:

```python
# Calculate metrics from results array
results = output_data.get('results', [])
total_docs = len(results)
successful = sum(1 for r in results if r.get('status') == 'success')
failed = sum(1 for r in results if r.get('status') != 'success')
total_chunks = sum(r.get('chunks_created', 0) for r in results if r.get('status') == 'success')
```

## Changes Made

### File: `services/monitor_service.py`

**Lines 133-140:** Replaced hardcoded field extraction with calculated metrics

**Before:**
```python
output_data = run.outputs['output']
total_docs = output_data.get('total_documents', 0)
successful = output_data.get('successful', 0)
failed = output_data.get('failed', 0)
total_chunks = output_data.get('total_chunks', 0)
```

**After:**
```python
output_data = run.outputs['output']

# Calculate metrics from results array
results = output_data.get('results', [])
total_docs = len(results)
successful = sum(1 for r in results if r.get('status') == 'success')
failed = sum(1 for r in results if r.get('status') != 'success')
total_chunks = sum(r.get('chunks_created', 0) for r in results if r.get('status') == 'success')
```

## Expected Result

After the Streamlit app refreshes, the Batch Processing tab should now display:
- **total_documents:** Actual count of documents processed (e.g., 8)
- **successful:** Number of successfully processed documents (e.g., 8)
- **failed:** Number of failed documents (e.g., 0)
- **total_chunks:** Total chunks created across all documents (e.g., 32)
- **duration_sec:** Actual processing time in seconds

## Validation

✅ Syntax check passed
✅ No linting errors
✅ Logic matches actual LangSmith data structure
✅ Handles empty results array gracefully

## Testing

To verify the fix:
1. Refresh the monitor page (click "Refresh Data")
2. Navigate to the "📦 Batch Processing" tab
3. Verify that the table shows actual numbers instead of zeros
4. Check that the metrics make sense based on the processing history

## Related Files

- `services/monitor_service.py` - Fixed data extraction logic
- `models/monitoring.py` - BatchProcessingRun model (unchanged)
- `pages/4_monitor.py` - UI display (unchanged)

---

**Fix completed successfully. The batch processing data should now display correctly.**
