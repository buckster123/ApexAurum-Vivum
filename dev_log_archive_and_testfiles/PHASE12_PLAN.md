# Phase 12 Implementation Plan: Export/Import & Conversation Management

## Overview

Add comprehensive export/import capabilities for conversations and configurations, plus conversation management features for searching, filtering, and organizing chat history.

**Goal:** Enable users to save, share, and manage their conversations and app configurations effectively.

---

## Current State Analysis

### What Works:
- ✅ Conversations stored in `./sandbox/conversations/`
- ✅ Basic JSON storage format
- ✅ Conversation list in sidebar
- ✅ New conversation creation
- ✅ Conversation switching

### Current Limitations:
- ❌ No export functionality (conversations trapped in app)
- ❌ No import functionality (can't bring in external conversations)
- ❌ No format conversion (JSON only)
- ❌ No search/filter across conversations
- ❌ No batch operations (delete multiple, export multiple)
- ❌ No configuration export/import (settings, prompts)
- ❌ No sharing capabilities
- ❌ Limited conversation metadata (no tags, categories, notes)

### Technical Foundation:
- `core/storage.py` handles conversation persistence
- JSON format: `{id, title, created_at, updated_at, messages[]}`
- Conversations directory: `./sandbox/conversations/`

---

## Goals

### Primary Goals:
1. **Export Conversations** - Multiple formats (JSON, Markdown, HTML, PDF, TXT)
2. **Import Conversations** - From JSON and other formats
3. **Configuration Management** - Export/import app settings
4. **Conversation Search** - Search across all conversations
5. **Conversation Organization** - Tags, categories, favorites
6. **Batch Operations** - Multi-select for bulk actions
7. **Sharing** - Generate shareable links/files

### Secondary Goals:
8. Advanced filtering (date range, model used, length)
9. Conversation templates
10. Automatic backups
11. Cloud sync (future consideration)

---

## Implementation Tasks

### Task 1: Create Export Engine
**File:** `core/export_engine.py` (NEW)

**Purpose:** Convert conversations to various formats

**Components:**

1. **BaseExporter** - Abstract base class
2. **JSONExporter** - Export to JSON (clean format)
3. **MarkdownExporter** - Export to Markdown
4. **HTMLExporter** - Export to HTML (styled)
5. **TXTExporter** - Export to plain text
6. **PDFExporter** - Export to PDF (using reportlab or weasyprint)

**Methods:**
```python
class ExportEngine:
    def export_conversation(
        self,
        conversation: Dict,
        format: str,
        options: Dict = None
    ) -> bytes:
        """Export a single conversation"""

    def export_multiple(
        self,
        conversation_ids: List[str],
        format: str,
        combine: bool = False
    ) -> Union[bytes, List[bytes]]:
        """Export multiple conversations"""

    def export_with_metadata(
        self,
        conversation_id: str,
        format: str,
        include_stats: bool = True
    ) -> bytes:
        """Export with metadata and statistics"""
```

**Export Formats:**

**JSON:**
```json
{
  "id": "conv_123",
  "title": "Discussion about Python",
  "created_at": "2025-12-29T15:00:00Z",
  "updated_at": "2025-12-29T15:30:00Z",
  "model": "claude-sonnet-4-5",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2025-12-29T15:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help?",
      "timestamp": "2025-12-29T15:00:05Z"
    }
  ],
  "metadata": {
    "total_messages": 10,
    "total_tokens": 1500,
    "tools_used": ["search_web", "read_file"],
    "tags": ["python", "coding"]
  }
}
```

**Markdown:**
```markdown
# Discussion about Python

**Created:** 2025-12-29 15:00
**Model:** claude-sonnet-4-5
**Messages:** 10

---

## Conversation

**User:**
Hello

**Assistant:**
Hi! How can I help?

**User:**
Can you explain Python decorators?

**Assistant:**
[Response with code blocks preserved]
```

**HTML:**
```html
<!DOCTYPE html>
<html>
<head>
  <title>Discussion about Python</title>
  <style>
    /* Styled CSS for nice presentation */
  </style>
</head>
<body>
  <h1>Discussion about Python</h1>
  <div class="metadata">...</div>
  <div class="conversation">
    <div class="message user">...</div>
    <div class="message assistant">...</div>
  </div>
</body>
</html>
```

**Lines:** ~400 lines

---

### Task 2: Create Import Engine
**File:** `core/import_engine.py` (NEW)

**Purpose:** Import conversations from various formats

**Components:**

1. **ImportEngine** - Main import coordinator
2. **JSONImporter** - Import from JSON
3. **MarkdownImporter** - Import from Markdown (best effort)
4. **FormatDetector** - Auto-detect file format

**Methods:**
```python
class ImportEngine:
    def detect_format(self, file_content: bytes) -> str:
        """Detect file format"""

    def import_conversation(
        self,
        file_content: bytes,
        format: str = None,
        validate: bool = True
    ) -> Dict:
        """Import a single conversation"""

    def import_multiple(
        self,
        files: List[Tuple[str, bytes]]
    ) -> List[Dict]:
        """Import multiple conversations"""

    def validate_conversation(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate conversation structure"""
```

**Validation Rules:**
- Required fields: `title`, `messages`
- Messages must have `role` and `content`
- Timestamps optional but validated if present
- IDs regenerated on import to avoid conflicts

**Lines:** ~300 lines

---

### Task 3: Add Configuration Export/Import
**File:** `core/config_manager.py` (NEW)

**Purpose:** Save and load app configurations

**What Gets Saved:**
```python
{
  "version": "1.0",
  "exported_at": "2025-12-29T15:00:00Z",
  "settings": {
    "model": "claude-sonnet-4-5",
    "temperature": 0.7,
    "max_tokens": 4096,
    "tools_enabled": true,
    "streaming_enabled": true,
    "show_tool_execution": true,
    "context_strategy": "balanced",
    "preserve_recent_count": 10
  },
  "system_prompts": [
    {
      "name": "Default",
      "content": "You are a helpful AI assistant..."
    },
    {
      "name": "Code Helper",
      "content": "You are an expert programmer..."
    }
  ],
  "custom_tools": [],
  "theme": "default"
}
```

**Methods:**
```python
class ConfigManager:
    def export_config(self) -> Dict:
        """Export current configuration"""

    def import_config(
        self,
        config: Dict,
        merge: bool = False
    ) -> bool:
        """Import configuration"""

    def validate_config(self, config: Dict) -> Tuple[bool, List[str]]:
        """Validate configuration structure"""

    def reset_to_defaults(self):
        """Reset all settings to defaults"""
```

**Lines:** ~200 lines

---

### Task 4: Add Conversation Management UI
**File:** `main.py` (MODIFY - Sidebar)

**Location:** New section in sidebar after "💬 Conversations"

**Features:**

1. **Search Bar**
```python
search_query = st.text_input(
    "🔍 Search conversations",
    placeholder="Search messages, titles...",
    help="Search across all conversations"
)
```

2. **Filter Controls**
```python
with st.expander("🔧 Filters", expanded=False):
    # Date range
    date_range = st.date_input("Date Range", value=[])

    # Model filter
    models_used = st.multiselect("Models", options=["Haiku", "Sonnet", "Opus"])

    # Tag filter
    tags = st.multiselect("Tags", options=get_all_tags())

    # Message count range
    msg_count = st.slider("Message Count", 1, 500, (1, 500))
```

3. **Batch Operations**
```python
with st.expander("✅ Batch Actions", expanded=False):
    # Multi-select mode
    batch_mode = st.toggle("Select Multiple")

    if batch_mode:
        selected = st.multiselect(
            "Select conversations",
            options=[c["id"] for c in conversations]
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📤 Export"):
                export_multiple(selected)
        with col2:
            if st.button("🗑️ Delete"):
                delete_multiple(selected)
        with col3:
            if st.button("🏷️ Tag"):
                tag_multiple(selected)
```

**Lines:** ~150 lines

---

### Task 5: Add Export/Import Dialogs
**File:** `main.py` (MODIFY - Main Area)

**Export Dialog:**
```python
if st.session_state.get("show_export_dialog"):
    st.markdown("### 📤 Export Conversation")

    with st.form("export_form"):
        # Format selection
        format = st.selectbox(
            "Format",
            options=["JSON", "Markdown", "HTML", "PDF", "TXT"],
            help="Choose export format"
        )

        # Options
        include_metadata = st.checkbox("Include metadata", value=True)
        include_stats = st.checkbox("Include statistics", value=True)

        if format == "PDF":
            include_toc = st.checkbox("Include table of contents", value=True)

        # Export button
        if st.form_submit_button("Export"):
            content = export_current_conversation(format, options)
            st.download_button(
                "Download",
                data=content,
                file_name=f"{conversation_title}.{format.lower()}",
                mime=get_mime_type(format)
            )
```

**Import Dialog:**
```python
if st.session_state.get("show_import_dialog"):
    st.markdown("### 📥 Import Conversation")

    with st.form("import_form"):
        # File upload
        uploaded_file = st.file_uploader(
            "Choose file",
            type=["json", "md", "txt"],
            help="Upload conversation file"
        )

        # Options
        merge_mode = st.radio(
            "Import Mode",
            options=["New Conversation", "Merge with Current"],
            help="Create new or merge with current conversation"
        )

        validate = st.checkbox("Validate before import", value=True)

        # Import button
        if st.form_submit_button("Import"):
            if uploaded_file:
                result = import_conversation(uploaded_file, merge_mode, validate)
                st.success(f"✅ Imported: {result['title']}")
```

**Lines:** ~200 lines

---

### Task 6: Add Configuration Management UI
**File:** `main.py` (MODIFY - Sidebar)

**Location:** Under "⚙️ Settings"

```python
st.divider()
st.subheader("💾 Configuration")
with st.expander("Export/Import Settings", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        # Export config
        if st.button("📤 Export Config", use_container_width=True):
            config = config_manager.export_config()
            st.download_button(
                "Download",
                data=json.dumps(config, indent=2),
                file_name="claude_config.json",
                mime="application/json"
            )

    with col2:
        # Import config
        uploaded_config = st.file_uploader(
            "📥 Import Config",
            type=["json"],
            key="config_upload"
        )

        if uploaded_config:
            config = json.load(uploaded_config)
            if st.button("Apply Configuration"):
                config_manager.import_config(config)
                st.success("✅ Configuration imported!")
                st.rerun()

    # Reset to defaults
    if st.button("🔄 Reset to Defaults", use_container_width=True):
        if st.confirm("Are you sure? This will reset all settings."):
            config_manager.reset_to_defaults()
            st.rerun()
```

**Lines:** ~80 lines

---

### Task 7: Add Conversation Metadata & Tags
**File:** `core/storage.py` (MODIFY)

**Enhanced Conversation Format:**
```python
{
  "id": "conv_123",
  "title": "Python Discussion",
  "created_at": "2025-12-29T15:00:00Z",
  "updated_at": "2025-12-29T15:30:00Z",
  "messages": [...],

  # New metadata fields (Phase 12)
  "metadata": {
    "tags": ["python", "coding", "tutorial"],
    "category": "Programming",
    "favorite": false,
    "archived": false,
    "notes": "Discussion about decorators and metaclasses",
    "model_used": "claude-sonnet-4-5",
    "total_messages": 10,
    "total_tokens": 1500,
    "tools_used": ["search_web", "read_file"],
    "created_by": "user",
    "shared": false,
    "share_link": null,
    "export_count": 3,
    "last_exported": "2025-12-29T16:00:00Z"
  }
}
```

**New Methods:**
```python
class ConversationStorage:
    def add_tag(self, conversation_id: str, tag: str):
        """Add tag to conversation"""

    def remove_tag(self, conversation_id: str, tag: str):
        """Remove tag from conversation"""

    def set_favorite(self, conversation_id: str, favorite: bool):
        """Mark as favorite"""

    def set_archived(self, conversation_id: str, archived: bool):
        """Archive conversation"""

    def search_conversations(
        self,
        query: str,
        filters: Dict = None
    ) -> List[Dict]:
        """Search conversations"""

    def get_all_tags(self) -> List[str]:
        """Get all unique tags"""
```

**Lines:** ~150 lines added

---

### Task 8: Create Phase 12 Test Suite
**File:** `test_phase12.py` (NEW)

**Tests:**
1. ✅ Export engine creates valid JSON
2. ✅ Export engine creates valid Markdown
3. ✅ Export engine creates valid HTML
4. ✅ Export to PDF works (if library available)
5. ✅ Import engine detects formats correctly
6. ✅ Import engine validates conversations
7. ✅ Import from JSON works
8. ✅ Configuration export includes all settings
9. ✅ Configuration import applies settings
10. ✅ Conversation search finds matches
11. ✅ Tag management works
12. ✅ Batch operations work correctly
13. ✅ Metadata storage persists
14. ✅ Export/import UI components exist
15. ✅ Download buttons function

**Lines:** ~400 lines

---

## UI Mockups

### Export Dialog:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 Export Conversation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Format: [JSON ▼]

☑️ Include metadata
☑️ Include statistics
☐ Include images (if supported)

Export Options:
• File name: python_discussion.json
• Size estimate: ~15 KB
• Messages: 24

[Export] [Cancel]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Import Dialog:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 Import Conversation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Drop file here or click to upload
Supported: JSON, Markdown, TXT

Import Mode:
○ New Conversation
● Merge with Current

☑️ Validate before import
☐ Preserve original timestamps

[Import] [Cancel]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Conversation Search:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 [Search conversations...          ]

🔧 Filters ▼
  Date Range: [Last 30 days ▼]
  Models: [All ▼]
  Tags: [python] [coding] [+]
  Messages: [1 ━━━━━━━━━ 500]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Results: 3 conversations

✅ Python Discussion (24 msgs)
   Tags: python, coding
   Dec 29, 2025 • Sonnet 4.5

✅ Async Programming Guide (15 msgs)
   Tags: python, async
   Dec 28, 2025 • Opus 4.5

✅ FastAPI Tutorial (38 msgs)
   Tags: python, api, web
   Dec 27, 2025 • Sonnet 4.5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Batch Operations:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Batch Actions

☑️ Select Multiple

Selected: 3 conversations

[📤 Export] [🗑️ Delete] [🏷️ Tag]

  ☑️ Python Discussion
  ☑️ Async Programming
  ☐ FastAPI Tutorial
  ☑️ Web Scraping Guide
  ☐ Data Analysis Project
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Technical Considerations

### Export Formats

**JSON:**
- Lossless, complete data preservation
- Machine-readable, importable
- Include full metadata
- Size: Smallest (compressed)

**Markdown:**
- Human-readable
- Preserves code blocks, formatting
- Good for documentation
- Can be imported (basic)
- Size: Small

**HTML:**
- Beautiful presentation
- Styled, ready to view
- Can include CSS
- Not easily importable
- Size: Medium

**PDF:**
- Best for sharing/archiving
- Professional appearance
- Not importable
- Requires library (reportlab/weasyprint)
- Size: Largest

**TXT:**
- Simple, universal
- No formatting
- Very readable
- Not importable
- Size: Smallest

### Import Considerations

**Format Detection:**
```python
def detect_format(content: bytes) -> str:
    # Try JSON first
    try:
        json.loads(content)
        return "json"
    except:
        pass

    # Check for markdown headers
    if b"# " in content[:100]:
        return "markdown"

    # Default to text
    return "text"
```

**Validation:**
- Check required fields exist
- Validate message structure
- Verify timestamps format
- Sanitize content (XSS prevention)
- Check for conflicts (duplicate IDs)

### Search Implementation

**Simple Search (Phase 12):**
```python
def search(query: str, conversations: List[Dict]) -> List[Dict]:
    results = []
    query_lower = query.lower()

    for conv in conversations:
        # Search title
        if query_lower in conv["title"].lower():
            results.append(conv)
            continue

        # Search messages
        for msg in conv["messages"]:
            if query_lower in str(msg["content"]).lower():
                results.append(conv)
                break

    return results
```

**Future Enhancement:**
- Full-text search index (SQLite FTS5)
- Vector search (embeddings)
- Fuzzy matching
- Regex support

---

## Session State Variables

New session state variables:

```python
# Export/Import
st.session_state.show_export_dialog = False
st.session_state.show_import_dialog = False
st.session_state.export_format = "json"
st.session_state.import_mode = "new"

# Search & Filter
st.session_state.search_query = ""
st.session_state.filter_date_range = None
st.session_state.filter_models = []
st.session_state.filter_tags = []

# Batch operations
st.session_state.batch_mode = False
st.session_state.selected_conversations = []

# Configuration
st.session_state.show_config_dialog = False
```

---

## File Structure

```
claude-version/
├── core/
│   ├── export_engine.py (NEW - ~400 lines)
│   ├── import_engine.py (NEW - ~300 lines)
│   ├── config_manager.py (NEW - ~200 lines)
│   └── storage.py (MODIFIED - +~150 lines)
├── test_phase12.py (NEW - ~400 lines)
├── main.py (MODIFIED - ~580 lines added)
├── PHASE12_PLAN.md (this file)
├── PHASE12_COMPLETE.md (after implementation)
└── PHASE12_QUICKSTART.md (after implementation)
```

**Total New Code:** ~1,450 lines
**Total Modified:** ~730 lines

---

## Implementation Order

### Phase 1 - Core Export (Tasks 1)
1. Create `core/export_engine.py`
2. Implement JSON exporter
3. Implement Markdown exporter
4. Implement HTML exporter
5. Implement TXT exporter
6. Test exporters

### Phase 2 - Core Import (Task 2)
7. Create `core/import_engine.py`
8. Implement format detection
9. Implement JSON importer
10. Implement validation
11. Test importers

### Phase 3 - Configuration (Task 3)
12. Create `core/config_manager.py`
13. Implement config export
14. Implement config import
15. Test configuration management

### Phase 4 - UI Integration (Tasks 4-6)
16. Add search/filter UI
17. Add batch operations UI
18. Add export dialog
19. Add import dialog
20. Add config management UI

### Phase 5 - Metadata & Enhancement (Task 7)
21. Enhance conversation storage
22. Add tag management
23. Add favorites/archive
24. Test metadata features

### Phase 6 - Testing & Polish (Task 8)
25. Create comprehensive test suite
26. Fix bugs and edge cases
27. Performance optimization
28. Documentation

---

## Success Criteria

Phase 12 will be considered complete when:

✅ Can export conversations to JSON, Markdown, HTML, TXT
✅ Can import conversations from JSON
✅ Can export/import app configuration
✅ Can search across all conversations
✅ Can filter by date, model, tags
✅ Can batch select and export/delete
✅ Can add tags and favorites to conversations
✅ All 15 tests pass
✅ Export/import preserves data integrity
✅ UI is intuitive and responsive

---

## Dependencies

### Required:
- No new dependencies for JSON, Markdown, HTML, TXT exporters
- All can be done with Python stdlib

### Optional:
- `reportlab` or `weasyprint` - For PDF export (can be optional feature)
- `markdown` - Better Markdown rendering (stdlib is fine for basic)

### Recommended:
- Keep it dependency-free for core features
- Make PDF export optional ("Install reportlab for PDF export")

---

## Future Enhancements (Post-Phase 12)

1. **Cloud Sync** - Sync conversations across devices
2. **Collaboration** - Share conversations with others (real-time)
3. **Version History** - Track conversation edits
4. **Advanced Search** - Vector search, semantic search
5. **Templates** - Pre-defined conversation starters
6. **Scheduled Exports** - Auto-backup on schedule
7. **Export to Notion/Obsidian** - Integration with note apps
8. **Conversation Analytics** - Usage statistics, insights

---

## Notes

### Design Philosophy:
- **User data ownership** - Easy export means users own their data
- **Privacy first** - All exports/imports local (no cloud required)
- **Format flexibility** - Multiple formats for different use cases
- **Lossless** - JSON export/import preserves everything
- **Human-readable** - Markdown/HTML for sharing and reading

### Edge Cases:
- Very large conversations (>1000 messages) - pagination for export
- Binary data in messages (images) - handle gracefully
- Corrupted import files - clear error messages
- Conflicting IDs on import - regenerate IDs
- Missing metadata fields - use sensible defaults

---

## Ready for Implementation?

This plan provides:
- ✅ Clear task breakdown (8 tasks)
- ✅ Detailed technical specifications
- ✅ UI mockups and examples
- ✅ Comprehensive testing strategy
- ✅ Success criteria
- ✅ Implementation order

**Next Step:** Get user approval and proceed with implementation!

---

**Plan Status:** ✅ Ready for Review
**Created:** 2025-12-29
**Phase:** 12 - Export/Import & Conversation Management
