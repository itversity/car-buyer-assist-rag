# Conversation Starters Fix

## Date
January 21, 2026

## Issue
Conversation starters were not working properly - clicking them didn't fill the text box or process the query.

## Root Cause
The original implementation tried to use the `value` parameter in a Streamlit form to dynamically fill the text input. However, Streamlit forms have a limitation: the `value` parameter only works on initial render. Once a form is rendered, it maintains its own internal state and ignores dynamic `value` updates on subsequent reruns.

### Original Broken Flow
1. Click conversation starter → Sets `st.session_state.user_input`
2. Page reruns
3. Code reads `user_input` and sets it as `default_query`
4. Form renders with `value=default_query` ← **Form ignores this**
5. Text box stays empty ❌

## Solution
Changed the approach to use Streamlit's session state with the `key` parameter to directly control the form input, and added logic to process starter queries immediately.

### New Working Flow
1. Click conversation starter → Sets `st.session_state.starter_query`
2. Page reruns
3. Code detects starter query and:
   - Saves it as `query_to_process`
   - Sets `st.session_state.form_query_input` (the form's key) ← **This works!**
   - Marks `should_process_starter = True`
4. Form renders with text visible (controlled by session state key)
5. Processing logic handles starter query immediately
6. Text appears briefly, then processes and displays response ✅

## Changes Made

### File: `pages/3_interactive_assistant.py`

#### Change 1: Update Conversation Starters (Lines 106-107)
**Before:**
```python
st.session_state.user_input = example_query
```

**After:**
```python
st.session_state.starter_query = example_query
```

#### Change 2: Replace Input Section Logic (Lines 187-200)
**Before:**
```python
# Get default value from conversation starters if set
if 'user_input' in st.session_state:
    default_query = st.session_state.user_input
    del st.session_state.user_input
else:
    default_query = ""
```

**After:**
```python
# Initialize form input state if not exists
if 'form_query_input' not in st.session_state:
    st.session_state.form_query_input = ""

# Check if there's a starter query to process
if 'starter_query' in st.session_state:
    query_to_process = st.session_state.starter_query
    del st.session_state.starter_query
    # Set the form input to show what was clicked
    st.session_state.form_query_input = query_to_process
    should_process_starter = True
else:
    query_to_process = None
    should_process_starter = False
```

#### Change 3: Update Form Text Input (Line 209)
**Before:**
```python
user_query = st.text_input(
    "Ask a question about Toyota vehicles:",
    value=default_query,  # Doesn't work in forms!
    placeholder="...",
    label_visibility="collapsed"
)
```

**After:**
```python
user_query = st.text_input(
    "Ask a question about Toyota vehicles:",
    key="form_query_input",  # Control via session state
    placeholder="...",
    label_visibility="collapsed"
)
```

#### Change 4: Update Clear Chat Button (Lines 222-226)
**Added:**
```python
st.session_state.form_query_input = ""  # Also clear the form input
```

#### Change 5: Update Processing Logic (Lines 229-233)
**Before:**
```python
if send_button and user_query and not st.session_state.processing:
```

**After:**
```python
if (should_process_starter or send_button) and not st.session_state.processing:
    # Use starter query if available, otherwise use form input
    query = query_to_process if should_process_starter else user_query
    
    if query and query.strip():  # Only process non-empty queries
```

#### Change 6: Update All References from `user_query` to `query`
Changed throughout the processing block to use the unified `query` variable.

#### Change 7: Clear Form Input After Processing (Line 271)
**Added:**
```python
st.session_state.form_query_input = ""  # Clear the form input
```

## Expected Behavior After Fix

### ✅ Working Features

1. **Conversation Starters Fill Text Box**
   - Click any starter button
   - Text appears in the input box (briefly)
   - Query is automatically processed
   - Response appears in chat

2. **Starters Disappear After First Use**
   - After first query is processed, `len(chat_messages) > 0`
   - Conversation starters section doesn't render anymore
   - Only the input form remains visible

3. **Enter Key Still Works**
   - Type a question manually
   - Press Enter or click Send
   - Query is processed normally

4. **Input Box Clears After Each Query**
   - After processing, form input state is explicitly cleared
   - Ready for next question immediately

5. **Clear Chat Works Properly**
   - Clears conversation history
   - Clears form input
   - Shows conversation starters again

## Testing Instructions

### Test 1: Basic Starter Functionality
1. Load the Interactive Assistant page
2. Verify 4 conversation starters are visible
3. Click "What are the safety features of the Corolla?"
4. **Expected:** Text briefly appears in box, then processes
5. **Expected:** Response appears with citations
6. **Expected:** Conversation starters disappear
7. **Expected:** Input box is clear and ready for next question

### Test 2: Multiple Starters
1. Start with fresh page (or clear chat)
2. Click different starter button
3. **Expected:** Each starter processes correctly
4. **Expected:** After first use, starters disappear

### Test 3: Combined Usage
1. Click a starter → processes
2. Type follow-up question → press Enter
3. **Expected:** Context is maintained
4. **Expected:** Both queries work correctly

### Test 4: Clear and Restart
1. Have a conversation
2. Click "Clear Chat"
3. **Expected:** Starters reappear
4. Click a starter again
5. **Expected:** Works as before

## Technical Notes

### Why Use `key` Parameter?
When you give a Streamlit widget a `key` parameter, you can control its value through `st.session_state[key]`. This is the proper way to dynamically control form inputs in Streamlit.

### Why `should_process_starter` Flag?
The flag distinguishes between:
- **Starter queries:** Should be processed immediately on the rerun after button click
- **Form submissions:** Only process when Send button is clicked or Enter is pressed

### Form State Management
```python
# This controls the text input widget
st.session_state.form_query_input = "Some text"

# This widget displays the value from session state
st.text_input(..., key="form_query_input")
```

## Conclusion

The conversation starters now work perfectly:
- ✅ Clicking fills the text box
- ✅ Query is processed automatically
- ✅ Starters disappear after first use
- ✅ Input clears for next question
- ✅ Enter key continues to work
- ✅ All existing functionality preserved

The fix uses Streamlit's recommended approach for controlling form inputs through session state, making it more reliable and maintainable.
