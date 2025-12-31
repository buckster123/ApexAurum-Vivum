# Phase 6 Implementation Plan: Image Support 📸

## Overview

**Goal**: Add vision capabilities to Apex Aurum - Claude Edition, allowing users to upload images and have Claude analyze them using its vision models.

**Complexity**: Medium
**Estimated Time**: 2-3 hours
**Priority**: Medium

---

## Current State

**What we have:**
- ✅ Working chat interface with text messages
- ✅ Claude API integration (Opus, Sonnet, Haiku)
- ✅ Tool calling system
- ✅ Dark mode UI

**What's missing:**
- ❌ Image upload UI
- ❌ Image format conversion for Claude API
- ❌ Image display in chat history
- ❌ Vision model support

---

## Claude Vision API Format

Claude expects images in this format:

```python
{
    "role": "user",
    "content": [
        {
            "type": "text",
            "text": "What's in this image?"
        },
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",  # or image/png, image/webp, image/gif
                "data": "base64_encoded_string_here"
            }
        }
    ]
}
```

**Key differences from OpenAI format:**
- Content is always an array (even for text-only)
- Images use `type: "image"` with nested `source` object
- Media type must be specified
- Supports: JPEG, PNG, WebP, GIF

---

## Implementation Steps

### **Task 1: Add Image Upload UI** 📤

**Location**: `main.py` chat input area

**Changes needed:**
1. Add Streamlit file uploader widget
2. Support multiple image formats (jpg, png, webp, gif)
3. Show image preview after upload
4. Allow multiple images per message
5. Store images in session state

**UI Design:**
```
Chat Input Area:
├── 📎 Image Upload Button
├── [Preview thumbnails of uploaded images]
├── Text input box
└── Send button
```

**Code structure:**
```python
# In main.py, above chat input
uploaded_files = st.file_uploader(
    "Upload images (optional)",
    type=["jpg", "jpeg", "png", "webp", "gif"],
    accept_multiple_files=True,
    key="image_upload"
)

if uploaded_files:
    # Show previews
    cols = st.columns(len(uploaded_files))
    for idx, file in enumerate(uploaded_files):
        with cols[idx]:
            st.image(file, width=100)
```

---

### **Task 2: Image Processing Functions** 🔄

**Location**: `main.py` helper functions

**Functions to add:**

```python
def encode_image_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 string"""
    import base64
    return base64.b64encode(image_bytes).decode('utf-8')

def get_media_type(filename: str) -> str:
    """Get media type from filename"""
    ext = filename.lower().split('.')[-1]
    mapping = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'webp': 'image/webp',
        'gif': 'image/gif'
    }
    return mapping.get(ext, 'image/jpeg')

def create_image_content(image_bytes: bytes, media_type: str) -> Dict:
    """Create Claude image content block"""
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": encode_image_to_base64(image_bytes)
        }
    }
```

---

### **Task 3: Update Message Format Converter** 🔧

**Location**: `core/message_converter.py`

**Changes needed:**
1. Handle multi-content messages (text + images)
2. Convert message content to array format when images present
3. Preserve image format through conversation

**Example conversion:**
```python
# Input (from UI):
{
    "role": "user",
    "content": "What's in this image?",
    "images": [image_data_1, image_data_2]
}

# Output (for Claude):
{
    "role": "user",
    "content": [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image", "source": {...}},
        {"type": "image", "source": {...}}
    ]
}
```

**Function to modify:**
```python
def prepare_messages_for_claude(messages: List[Dict]) -> Tuple[str, List[Dict]]:
    # Add logic to handle images
    # Convert content to array format when images present
    pass
```

---

### **Task 4: Update Process Message Function** 💬

**Location**: `main.py` - `process_message()`

**Changes needed:**
1. Accept uploaded images along with text
2. Create multi-content message structure
3. Store images with message in session state
4. Display images in chat history

**Modified function signature:**
```python
def process_message(user_message: str, uploaded_images: Optional[List] = None):
    # Build content array
    content = []

    if user_message:
        content.append({
            "type": "text",
            "text": user_message
        })

    if uploaded_images:
        for img_file in uploaded_images:
            img_bytes = img_file.read()
            media_type = get_media_type(img_file.name)
            content.append(create_image_content(img_bytes, media_type))

    # Add to session state
    st.session_state.messages.append({
        "role": "user",
        "content": content,  # Now an array
        "images": uploaded_images  # Store for display
    })
```

---

### **Task 5: Update Message Display** 🖼️

**Location**: `main.py` - `render_message()`

**Changes needed:**
1. Handle messages with images
2. Display images in chat history
3. Support both old (string content) and new (array content) formats

**Updated function:**
```python
def render_message(message: Dict[str, str]):
    role = message["role"]
    content = message["content"]

    if role == "user":
        with st.chat_message("user", avatar="👤"):
            # Handle array content (with images)
            if isinstance(content, list):
                for item in content:
                    if item.get("type") == "text":
                        st.markdown(item["text"])
                    elif item.get("type") == "image":
                        # Show image from base64
                        st.image(f"data:{item['source']['media_type']};base64,{item['source']['data']}")
            # Handle string content (backward compatibility)
            elif isinstance(content, str):
                st.markdown(content)

    # Similar for assistant messages
```

---

### **Task 6: Vision Model Support** 🤖

**Location**: UI - Model selection

**Changes needed:**
1. Indicate which models support vision
2. Recommend vision-capable models when images uploaded
3. Show warning if using Haiku with images (limited vision)

**UI update:**
```python
model_options = {
    "Claude Opus 4.5 (Best + Vision)": ClaudeModels.OPUS_4_5.value,
    "Claude Sonnet 4.5 (Balanced + Vision)": ClaudeModels.SONNET_4_5.value,
    "Claude Sonnet 3.7 (Fast + Vision)": ClaudeModels.SONNET_3_7.value,
    "Claude Haiku 3.5 (Fastest, Limited Vision)": ClaudeModels.HAIKU_3_5.value,
}
```

---

### **Task 7: Conversation Storage** 💾

**Location**: `main.py` - `AppState.save_message()`

**Changes needed:**
1. Handle storing images in conversations.json
2. Option 1: Store base64 in JSON (simple but large files)
3. Option 2: Save images to disk, store paths (efficient)

**Recommended approach:**
```python
def save_message(self, role: str, content: Any, images: Optional[List] = None):
    message = {
        "role": role,
        "content": content,  # Can be string or array
        "timestamp": datetime.now().isoformat()
    }

    # Option: Don't persist images (to keep JSON small)
    # Images only available during session
    if isinstance(content, list):
        # Remove base64 data before saving
        message["content"] = [
            item for item in content
            if item.get("type") != "image"
        ]
        message["had_images"] = True
```

---

### **Task 8: Testing** ✅

**Test cases:**
1. Upload single image and ask about it
2. Upload multiple images in one message
3. Mix text and images
4. Verify image display in chat history
5. Test all supported formats (jpg, png, webp, gif)
6. Test with different models
7. Verify conversation loading (without images)
8. Test error handling (unsupported format, too large)

---

## File Structure After Phase 6

```
claude-version/
├── main.py                         # ← Modified: Image upload UI, display
├── core/
│   ├── message_converter.py       # ← Modified: Multi-content support
│   └── api_client.py              # No changes needed
├── .streamlit/
│   └── config.toml                # No changes needed
└── tests/
    └── test_phase6.py             # ← New: Image support tests
```

---

## Example User Flow

```
1. User clicks "Upload images"
   ↓
2. Selects 2 images (cat.jpg, dog.png)
   ↓
3. Images show as thumbnails below upload button
   ↓
4. User types: "Compare these two animals"
   ↓
5. Clicks Send
   ↓
6. Message appears with text + both images
   ↓
7. Claude responds with analysis
   ↓
8. Both user images and Claude response shown in history
```

---

## Technical Considerations

### Image Size Limits
- Claude API accepts images up to **5MB** (after base64 encoding)
- Original images up to ~3.75MB before encoding
- UI should validate size before upload

### Supported Formats
- ✅ JPEG/JPG
- ✅ PNG
- ✅ WebP
- ✅ GIF
- ❌ SVG (not supported)
- ❌ BMP (not supported)

### Performance
- Base64 encoding adds ~33% size overhead
- Larger messages = slower API calls
- Consider image compression for large files

### Cost
- Vision requests cost more tokens
- Images: ~85-170 tokens per image (depends on size)
- Recommend using Haiku for simple vision tasks

---

## UI Mockup

```
┌─────────────────────────────────────────────────┐
│ 💬 Apex Aurum - Claude Edition                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  👤 User: [image: cat.jpg] [image: dog.png]   │
│          "Compare these two animals"           │
│                                                 │
│  🤖 Claude: "The first image shows a cat..."   │
│                                                 │
│ ┌─────────────────────────────────────────────┐│
│ │ 📎 Upload Images                            ││
│ │ [cat.jpg 📷] [dog.png 📷] [+]              ││
│ │                                              ││
│ │ ┌──────────────────────────────────────────┐││
│ │ │ Message Claude...                        │││
│ │ └──────────────────────────────────────────┘││
│ └─────────────────────────────────────────────┘│
└─────────────────────────────────────────────────┘
```

---

## Success Criteria

Phase 6 complete when:
- ✅ Users can upload images (jpg, png, webp, gif)
- ✅ Images display in chat history
- ✅ Claude analyzes images correctly
- ✅ Multiple images per message work
- ✅ All vision-capable models work
- ✅ Error handling for invalid images
- ✅ Tests pass

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Large file sizes | Slow uploads, API errors | Add size validation, compress images |
| Base64 JSON size | Large conversation files | Don't persist images in JSON |
| Format compatibility | Some images fail | Validate format before upload |
| Token costs | Expensive for users | Show token estimate, recommend Haiku |

---

## Optional Enhancements

**Not required for Phase 6, but nice to have:**
- Image compression before sending
- Drag-and-drop image upload
- Paste image from clipboard
- Image URL support (download and convert)
- OCR preprocessing for text-heavy images
- Image editing tools (crop, resize, rotate)

---

## Questions to Resolve

1. **Storage**: Store images in conversations.json or exclude them?
   - **Recommendation**: Exclude to keep JSON manageable

2. **Size limits**: Client-side validation or let API reject?
   - **Recommendation**: Client-side with clear error messages

3. **Compression**: Auto-compress large images?
   - **Recommendation**: Phase 6: No compression (keep it simple)
   - Can add in future if needed

4. **Multiple images**: How many per message?
   - **Recommendation**: No limit in UI, but show warning if >3

---

## Timeline

| Task | Time | Dependencies |
|------|------|--------------|
| 1. Upload UI | 30 min | None |
| 2. Processing functions | 20 min | Task 1 |
| 3. Message converter | 30 min | Task 2 |
| 4. Process message | 30 min | Tasks 2-3 |
| 5. Message display | 30 min | Task 4 |
| 6. Model indicators | 10 min | None |
| 7. Storage handling | 20 min | Task 4 |
| 8. Testing | 40 min | All tasks |
| **Total** | **~3 hours** | |

---

## Next Steps

After Phase 6 approval:
1. Start with Task 1 (Upload UI)
2. Test incrementally after each task
3. Create test_phase6.py
4. Document in PHASE6_COMPLETE.md

**Ready to proceed?** 🚀

---

*Planning Document | December 29, 2025*
