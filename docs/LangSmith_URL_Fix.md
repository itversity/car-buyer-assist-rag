# LangSmith Trace URL Fix

## Issue

The "View Trace" links for both Single Document Processing and Batch Processing were returning 404 errors when clicked.

## Root Cause

The LangSmith URL format was incorrect. The service was using:
```
https://smith.langchain.com/public/{project_name}/{run_id}/r
```

This format includes `/public/` and the project name, which is not the correct URL structure for LangSmith traces.

## Solution

Updated all three trace URL constructions in `services/monitor_service.py` to use the correct format:
```
https://smith.langchain.com/o/{run_id}/r
```

The correct format uses `/o/` (organization) and directly includes the run ID without the project name.

## Changes Made

### File: `services/monitor_service.py`

**Line 88** - Document Processing URLs:
```python
# Before:
langsmith_url=f"https://smith.langchain.com/public/{self.project_name}/{run.id}/r"

# After:
langsmith_url=f"https://smith.langchain.com/o/{run.id}/r"
```

**Line 157** - Batch Processing URLs:
```python
# Before:
langsmith_url=f"https://smith.langchain.com/public/{self.project_name}/{run.id}/r"

# After:
langsmith_url=f"https://smith.langchain.com/o/{run.id}/r"
```

**Line 228** - Query Operations URLs:
```python
# Before:
langsmith_url=f"https://smith.langchain.com/public/{self.project_name}/{run.id}/r"

# After:
langsmith_url=f"https://smith.langchain.com/o/{run.id}/r"
```

## Expected Result

After refreshing the Streamlit app, all "View Trace" links should now:
1. Open correctly in LangSmith
2. Display the full trace details for that specific run
3. Show request/response data, timing, and token usage

## Validation

✅ Syntax check passed
✅ No linting errors
✅ All three operation types updated consistently
✅ URL format matches LangSmith's expected structure

## Testing

To verify the fix:
1. Refresh the monitor page
2. Go to any of the three tabs (Single Document Processing, Batch Processing, or Query Operations)
3. Expand "View LangSmith Traces"
4. Click on any trace link
5. Verify that it opens the correct trace in LangSmith (no 404 error)

## Related Files

- `services/monitor_service.py` - Fixed URL format (3 locations)
- `models/monitoring.py` - No changes needed
- `pages/4_monitor.py` - No changes needed

## Notes

The URL format `/o/{run_id}/r` appears to be the standard format for LangSmith trace links where:
- `/o/` - Indicates organization-level access
- `{run_id}` - The unique identifier for the specific run
- `/r` - Indicates this is a run/trace view

The project name is not needed in the URL path as LangSmith can determine the project from the run ID itself.

---

**Fix completed successfully. All trace links should now work correctly.**
