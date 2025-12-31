# Phase 5 Hotfix: top_p Parameter Issue

## Issue

During user testing with Claude Sonnet 4.5, the `top_p` parameter was causing API errors when passed to the Claude API.

**Error symptoms:**
- API rejecting requests with top_p parameter
- Responses failing after adding advanced settings

## Root Cause

The `top_p` parameter was being passed to the Claude API, but:
1. It wasn't properly declared in the `create_message()` method signature
2. It wasn't conditionally added to request parameters
3. Some Claude models may not support it or it may require specific handling

## Fix Applied

### 1. Updated API Client (`core/api_client.py`)

**Added top_p parameter to method signatures:**
```python
def create_message(
    self,
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    system: Optional[str] = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 1.0,
    top_p: Optional[float] = None,  # ← Added, defaults to None
    tools: Optional[List[Dict[str, Any]]] = None,
    stream: bool = False,
) -> Any:
```

**Only include top_p in request if not None:**
```python
# Build request parameters
request_params = {
    "model": model_id,
    "messages": messages,
    "max_tokens": max_tokens,
    "temperature": temperature,
}

# Add top_p if provided (optional parameter)
if top_p is not None:  # ← Only add if explicitly set
    request_params["top_p"] = top_p
```

### 2. Updated UI (`main.py`)

**Changed session state default:**
```python
if "top_p" not in st.session_state:
    st.session_state.top_p = None  # ← Changed from 0.99 to None
```

**Removed top_p slider from UI:**
```python
# Advanced settings
st.subheader("🎛️ Advanced Settings")
with st.expander("Model Parameters", expanded=False):
    st.session_state.temperature = st.slider(...)

    # Note: top_p removed due to API compatibility issues
    st.session_state.top_p = None  # ← Hardcoded to None

    st.session_state.max_tokens = st.number_input(...)
```

## Result

- ✅ `top_p` now defaults to `None`
- ✅ Claude API uses its default behavior when `top_p` is not provided
- ✅ No API errors
- ✅ UI simplified (removed problematic slider)
- ✅ Temperature and max_tokens still fully functional

## Testing

```bash
# Test imports
python -c "import main; print('✅ Success')"

# Run the app
streamlit run main.py

# Verify:
# - No top_p slider in Advanced Settings
# - Temperature slider works
# - Max tokens input works
# - Chat responses work normally
```

## Why This Works

**Claude API behavior:**
- When `top_p` is not provided, Claude uses its internal default
- This is often model-specific and optimized by Anthropic
- Explicitly setting `top_p` may conflict with some model configurations

**Benefits of None default:**
- Uses Claude's optimal settings
- Avoids API compatibility issues
- Simpler for users (one less parameter to tune)
- Still allows programmatic setting if needed

## Advanced Usage

If you need to use `top_p` programmatically, you can still set it:

```python
# In session state
st.session_state.top_p = 0.9

# Will be passed to API
response = loop.run(
    messages=messages,
    temperature=0.7,
    top_p=0.9,  # Will be included in API call
    ...
)
```

## Alternative: Re-enable top_p Slider (Optional)

If you want to experiment with `top_p`, you can re-enable the slider:

```python
# In main.py, replace the hardcoded None with:
st.session_state.top_p = st.slider(
    "Top P (Experimental)",
    min_value=0.0,
    max_value=1.0,
    value=0.0,  # 0.0 means "use Claude default"
    step=0.05,
    help="⚠️ Experimental: May cause errors with some models. 0.0 = Claude default"
)

# Then modify the API call to only pass if > 0:
if st.session_state.top_p > 0:
    kwargs["top_p"] = st.session_state.top_p
```

## Files Modified

1. **`core/api_client.py`** - Added top_p parameter handling
2. **`main.py`** - Removed slider, defaulted to None

## Status

✅ **FIXED** - top_p no longer causes API errors
✅ **TESTED** - App runs successfully with Sonnet 4.5
✅ **DOCUMENTED** - This hotfix document created

---

**Version**: Phase 5.1 (Hotfix)
**Date**: December 29, 2025
**Tested with**: Claude Sonnet 4.5
