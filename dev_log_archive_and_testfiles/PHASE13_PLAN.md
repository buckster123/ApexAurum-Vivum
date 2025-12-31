# Phase 13 Plan: Advanced Memory & Semantic Search

**Status:** 📋 Planning
**Estimated Complexity:** High
**Estimated Lines:** ~1,200 lines + dependencies
**Goal:** Add toggleable vector search layer for semantic conversation search, knowledge management, and RAG capabilities

## Overview

Phase 13 adds a powerful "cortical layer" to Apex Aurum - a semantic search system built on ChromaDB and sentence-transformers. This layer runs **parallel** to the existing memory system, providing semantic understanding without replacing the fast, simple key-value memory that works perfectly for operational data.

**Key Principle:** The existing memory system (`tools/memory.py`) remains untouched and continues to handle operational data (settings, user info, quick facts). Vector search adds new semantic capabilities as an **optional enhancement**.

## Architecture

### Hybrid Memory System

```
┌─────────────────────────────────────────────────────────┐
│                    APEX AURUM                           │
├─────────────────────────────────────────────────────────┤
│  User Query: "Show me conversations about AI models"    │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴─────────────┐
        │                          │
        ▼                          ▼
┌───────────────┐          ┌──────────────┐
│ KEYWORD LAYER │          │ VECTOR LAYER │
│  (Existing)   │          │   (New)      │
├───────────────┤          ├──────────────┤
│ • Fast        │          │ • Semantic   │
│ • Text match  │          │ • ChromaDB   │
│ • Filters     │          │ • Embeddings │
│ • Tags        │          │ • Similarity │
└───────┬───────┘          └──────┬───────┘
        │                         │
        └────────┬────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ MERGED RESULTS │
        │ (Ranked by     │
        │  relevance)    │
        └────────────────┘
```

### Data Flow

```
┌─────────────────────────────────────────────────────┐
│                 CONVERSATION SAVED                   │
└────────────────────┬────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
┌─────────────────┐    ┌────────────────────┐
│  conversations  │    │  Vector DB         │
│   .json file    │    │  (if enabled)      │
│                 │    │                    │
│  • Messages     │    │  • Embeddings      │
│  • Metadata     │    │  • Metadata        │
│  • Tags         │    │  • Collections     │
└─────────────────┘    └────────────────────┘
```

### Vector Collections

1. **conversations** - Semantic conversation search
   - Each conversation indexed with title + message content
   - Metadata: conv_id, created_at, tags, message_count
   - Enables: "Find similar conversations"

2. **knowledge** - Persistent knowledge base
   - Store facts, learnings, preferences
   - Metadata: type, confidence, source, timestamp
   - Enables: RAG context augmentation

3. **documents** - Semantic document/code search
   - Index files in sandbox (optional)
   - Metadata: filename, path, file_type, size
   - Enables: "Find code that handles authentication"

4. **memory_semantic** - Optional semantic memory layer
   - Parallel to key-value memory
   - For when you need semantic search of memories
   - Metadata: memory_key, stored_at

## Core Components

### 1. Vector Database Engine
**File:** `core/vector_db.py` (~400 lines)

**Purpose:** ChromaDB wrapper and embedding management

**Classes:**
```python
class VectorDB:
    """Main vector database interface"""

    def __init__(self, persist_directory: str, model_name: str)
    def get_or_create_collection(self, name: str) -> Collection
    def list_collections(self) -> List[str]
    def delete_collection(self, name: str) -> bool

class EmbeddingGenerator:
    """Handle text embeddings with sentence-transformers"""

    def __init__(self, model_name: str)
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray
    def encode_batch(self, texts: List[str], batch_size: int) -> List[np.ndarray]

class VectorCollection:
    """Wrapper for ChromaDB collection operations"""

    def add(self, texts: List[str], metadatas: List[Dict], ids: List[str])
    def query(self, query_text: str, n_results: int, filter: Dict) -> QueryResult
    def delete(self, ids: List[str])
    def update(self, ids: List[str], metadatas: List[Dict])
    def count(self) -> int
```

**Key Features:**
- Lazy loading (only initialize when enabled)
- Batch processing for efficient embedding
- Progress callbacks for long operations
- Error handling and fallbacks
- Disk persistence

### 2. Vector Search Tools
**File:** `tools/vector_search.py` (~300 lines)

**Purpose:** Claude-accessible vector search tools

**Functions:**
```python
def vector_add(text: str, metadata: Dict, collection: str) -> Dict
    """Add a document to vector database"""

def vector_search(query: str, collection: str, top_k: int, filter: Dict) -> List[Dict]
    """Semantic search across collection"""

def vector_delete(id: str, collection: str) -> Dict
    """Remove document from collection"""

def vector_list_collections() -> List[str]
    """List all available collections"""

def vector_add_knowledge(fact: str, confidence: float, source: str) -> Dict
    """Add to knowledge base (convenience function)"""

def vector_search_knowledge(query: str, top_k: int) -> List[Dict]
    """Search knowledge base (convenience function)"""
```

**Tool Schemas:**
- Comprehensive descriptions for Claude
- Validation of inputs
- Rich error messages
- Usage examples in descriptions

### 3. Conversation Indexer
**File:** `core/conversation_indexer.py` (~250 lines)

**Purpose:** Index conversations for semantic search

**Classes:**
```python
class ConversationIndexer:
    """Index conversations into vector DB"""

    def __init__(self, vector_db: VectorDB, app_state: AppState)

    def index_conversation(self, conversation: Dict) -> bool
        """Index single conversation"""

    def index_all_conversations(self, progress_callback: Callable) -> Dict
        """Index all existing conversations with progress"""

    def update_conversation_index(self, conv_id: str) -> bool
        """Update index for modified conversation"""

    def remove_conversation_index(self, conv_id: str) -> bool
        """Remove conversation from index"""

    def get_indexing_stats(self) -> Dict
        """Get indexing statistics"""
```

**Indexing Strategy:**
- Concatenate title + first message + summary of other messages
- Limit total text to ~1000 tokens per conversation
- Update index when conversation modified
- Remove from index when deleted
- Background re-indexing option

### 4. Enhanced Search Interface
**File:** Modifications to `main.py` (~200 lines added)

**Sidebar Enhancements:**
```python
# In settings section
st.checkbox("Enable Vector Search", key="vector_enabled")
if st.session_state.vector_enabled:
    st.selectbox("Embedding Model", ["MiniLM-L6", "MiniLM-L12", "MPNet"])
    st.slider("Similarity Threshold", 0.0, 1.0, 0.5)
    if st.button("Re-index Conversations"):
        # Trigger full re-indexing
```

**Search Enhancements:**
```python
# In conversation browser
if st.session_state.vector_enabled:
    search_mode = st.radio("Search Mode", ["Keyword", "Semantic", "Hybrid"])
else:
    search_mode = "Keyword"

if search_mode == "Semantic":
    # Use vector_search
    results = vector_search(query, "conversations", top_k=20)
    # Show similarity scores
elif search_mode == "Hybrid":
    # Combine keyword + vector results
    # Rank by weighted score
```

**Indexing Progress:**
- Progress bar during initial indexing
- Show indexed/total conversations
- Estimated time remaining
- Cancel button

### 5. Knowledge Base Manager
**File:** `core/knowledge_base.py` (~200 lines)

**Purpose:** Manage persistent knowledge

**Classes:**
```python
class KnowledgeBase:
    """Manage persistent knowledge storage"""

    def add_fact(self, fact: str, category: str, confidence: float, source: str)
    def search_facts(self, query: str, category: str, min_confidence: float)
    def update_fact(self, fact_id: str, new_confidence: float)
    def delete_fact(self, fact_id: str)
    def get_related_facts(self, fact_id: str, top_k: int)
    def export_knowledge(self) -> List[Dict]
    def import_knowledge(self, facts: List[Dict])
```

**Categories:**
- `user_preferences` - User likes, dislikes, preferences
- `technical_knowledge` - Code patterns, technical facts
- `conversation_insights` - Learnings from conversations
- `project_context` - Project-specific information

### 6. Document Indexer (Optional)
**File:** `core/document_indexer.py` (~150 lines)

**Purpose:** Index sandbox files for semantic search

**Features:**
- Index Python, JS, TS, JSON, MD, TXT files
- Chunk large files (1000 tokens per chunk)
- Update index on file changes
- Exclude binary files
- Respect .gitignore patterns

### 7. RAG Context Augmenter
**File:** `core/rag_context.py` (~150 lines)

**Purpose:** Augment context with relevant knowledge

**Usage:**
```python
class RAGAugmenter:
    """Augment conversation context with relevant knowledge"""

    def augment_system_prompt(self, user_query: str, base_prompt: str) -> str
        """Add relevant facts to system prompt"""

    def get_relevant_context(self, query: str, max_tokens: int) -> str
        """Retrieve relevant context for query"""
```

**Integration:**
- Before sending to Claude API
- Retrieve top-K relevant facts from knowledge base
- Add to system prompt or as context messages
- Token budget management

## Implementation Steps

### Phase 13.1: Core Vector Infrastructure (Foundation)

**Files to Create:**
1. `core/vector_db.py` - Vector database wrapper
2. `requirements-vector.txt` - New dependencies

**Tasks:**
- [ ] Set up ChromaDB with persistence
- [ ] Implement EmbeddingGenerator with sentence-transformers
- [ ] Create VectorCollection wrapper
- [ ] Add collection management (create, list, delete)
- [ ] Implement batch operations
- [ ] Add error handling and fallbacks
- [ ] Test on Pi-5 (performance profiling)

**Dependencies:**
```
chromadb>=0.4.0
sentence-transformers>=2.2.0
```

**Testing:**
- Unit tests for embedding generation
- Collection CRUD operations
- Batch processing performance
- Error scenarios

### Phase 13.2: Vector Search Tools

**Files to Create:**
1. `tools/vector_search.py` - Claude-accessible tools
2. Modify `tools/registry.py` - Register vector tools

**Tasks:**
- [ ] Implement vector_add function
- [ ] Implement vector_search function
- [ ] Implement vector_delete function
- [ ] Implement vector_list_collections function
- [ ] Create tool schemas for Claude
- [ ] Add convenience functions (knowledge base)
- [ ] Register tools in registry
- [ ] Test tools with mock API calls

**Tool Examples:**
```python
# Add knowledge
vector_add_knowledge(
    "User prefers TypeScript over JavaScript",
    confidence=0.9,
    source="conversation_2025-01-15"
)

# Search knowledge
results = vector_search_knowledge(
    "What are user's language preferences?",
    top_k=5
)
```

### Phase 13.3: Conversation Indexing

**Files to Create:**
1. `core/conversation_indexer.py` - Indexing logic
2. Modify `main.py` - Auto-index on save/delete

**Tasks:**
- [ ] Implement conversation text extraction
- [ ] Implement single conversation indexing
- [ ] Implement batch indexing with progress
- [ ] Add auto-index on conversation save
- [ ] Add auto-remove on conversation delete
- [ ] Add re-index button to UI
- [ ] Show indexing status in sidebar
- [ ] Test with 100+ conversations

**Indexing Format:**
```python
{
    "text": "Title: My Conversation\n\nUser: Hello...\nAssistant: Hi...",
    "metadata": {
        "conv_id": "conv_abc123",
        "created_at": "2025-01-15T10:00:00",
        "tags": ["python", "coding"],
        "message_count": 12,
        "favorite": True
    }
}
```

### Phase 13.4: Enhanced Search UI

**Files to Modify:**
1. `main.py` - Search interface, settings

**Tasks:**
- [ ] Add "Enable Vector Search" toggle to settings
- [ ] Add embedding model selector
- [ ] Add similarity threshold slider
- [ ] Add search mode selector (Keyword/Semantic/Hybrid)
- [ ] Implement semantic search results display
- [ ] Show similarity scores in results
- [ ] Add re-index button with progress bar
- [ ] Add indexing statistics display
- [ ] Test search modes with various queries

**UI Flow:**
```
Settings:
  [x] Enable Vector Search
  Embedding Model: [MiniLM-L6-v2 ▼]
  Similarity Threshold: [0.5        ]

  Indexed: 47/50 conversations
  [Re-index All Conversations]

Search:
  🔍 [Show me AI project discussions    ]
  Search Mode: (•) Semantic ( ) Keyword ( ) Hybrid

  Results (5):
  ⭐ AI Model Training Discussion (similarity: 0.87)
  📦 Neural Network Architecture (similarity: 0.82)
  ...
```

### Phase 13.5: Knowledge Base

**Files to Create:**
1. `core/knowledge_base.py` - Knowledge management
2. Modify `main.py` - Knowledge UI (optional)

**Tasks:**
- [ ] Implement KnowledgeBase class
- [ ] Add fact categories
- [ ] Implement confidence scoring
- [ ] Add fact relationships
- [ ] Create knowledge export/import
- [ ] Add knowledge browser to UI (optional)
- [ ] Test knowledge operations
- [ ] Test with 100+ facts

**Knowledge UI (Optional):**
```
📚 Knowledge Base (127 facts):

  [Search knowledge...]

  Category: [All ▼] Confidence: [0.0 ──────●── 1.0]

  User Preferences (23)
  • Prefers TypeScript (0.9) - conversation_20250115
  • Uses VSCode editor (0.8) - conversation_20250112
  ...

  Technical Knowledge (45)
  • FastAPI uses Pydantic for validation (1.0) - manual_entry
  ...
```

### Phase 13.6: RAG Context Augmentation

**Files to Create:**
1. `core/rag_context.py` - RAG augmentation
2. Modify `main.py` - Integrate with API calls

**Tasks:**
- [ ] Implement RAGAugmenter class
- [ ] Add context retrieval based on query
- [ ] Implement token budget management
- [ ] Integrate with system prompt
- [ ] Add RAG enable/disable toggle
- [ ] Add RAG settings (top_k, max_tokens)
- [ ] Test with various queries
- [ ] Measure impact on response quality

**Integration:**
```python
# Before API call
if st.session_state.vector_enabled and st.session_state.rag_enabled:
    augmenter = RAGAugmenter(vector_db)

    # Get relevant context
    context = augmenter.get_relevant_context(
        user_message,
        max_tokens=500
    )

    # Add to system prompt
    enhanced_prompt = f"{system_prompt}\n\nRelevant Context:\n{context}"
```

### Phase 13.7: Document Indexing (Bonus)

**Files to Create:**
1. `core/document_indexer.py` - Document indexing
2. Add document search to UI

**Tasks:**
- [ ] Implement document file scanning
- [ ] Implement file chunking strategy
- [ ] Add document indexing
- [ ] Add document search UI
- [ ] Filter by file type
- [ ] Show file context in results
- [ ] Test with various file types

### Phase 13.8: Testing & Optimization

**Files to Create:**
1. `test_phase13.py` - Comprehensive test suite

**Tasks:**
- [ ] Test vector DB operations
- [ ] Test embedding generation
- [ ] Test search accuracy
- [ ] Test indexing performance
- [ ] Test with 1000+ conversations
- [ ] Optimize for Pi-5
- [ ] Profile memory usage
- [ ] Create performance benchmarks

**Test Coverage:**
- Vector DB CRUD operations (10 tests)
- Embedding generation (5 tests)
- Conversation indexing (8 tests)
- Search operations (10 tests)
- Knowledge base (8 tests)
- RAG augmentation (5 tests)
- Document indexing (5 tests)

**Target:** 50+ tests passing

## Dependencies

### New Python Packages

```bash
# In requirements-vector.txt
chromadb>=0.4.0
sentence-transformers>=2.2.0
torch>=2.0.0  # For sentence-transformers
numpy>=1.24.0
```

### Installation

```bash
# In virtual environment
pip install -r requirements-vector.txt
```

### Model Downloads

First run will download models (~90MB for MiniLM-L6):
```python
# Happens automatically on first use
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### Storage Requirements

- **ChromaDB**: ~10MB per 1000 conversations
- **Models**: ~90MB (MiniLM-L6) to ~400MB (MPNet)
- **Total**: ~500MB for typical usage

## Performance Considerations (Pi-5)

### Embedding Performance

**all-MiniLM-L6-v2** (recommended):
- Size: 90MB
- Embedding time: ~50ms per text
- Quality: Good for most use cases

**all-MiniLM-L12-v2** (better quality):
- Size: 134MB
- Embedding time: ~80ms per text
- Quality: Better semantic understanding

**all-mpnet-base-v2** (best quality):
- Size: 438MB
- Embedding time: ~120ms per text
- Quality: Best semantic understanding

### Indexing Performance

**Initial indexing (100 conversations):**
- MiniLM-L6: ~5-8 seconds
- MiniLM-L12: ~8-12 seconds
- MPNet: ~12-20 seconds

**Incremental indexing (per conversation):**
- ~50-120ms (depending on model)
- Happens in background, non-blocking

### Search Performance

**Query time:**
- Embedding query: ~50ms
- Vector search: ~20-50ms
- Total: ~70-150ms (acceptable!)

### Memory Usage

- ChromaDB: ~100MB base
- Model: ~200-500MB (loaded once)
- Embeddings: ~1KB per document
- Total: ~300-800MB (acceptable on Pi-5)

### Optimization Strategies

1. **Lazy Loading:** Only load when vector search enabled
2. **Model Caching:** Keep model in memory once loaded
3. **Batch Processing:** Embed multiple texts together
4. **Background Indexing:** Don't block UI during indexing
5. **Disk Persistence:** Embeddings persist, no re-calculation

## Settings & Configuration

### New Session State

```python
# Vector search settings
if "vector_enabled" not in st.session_state:
    st.session_state.vector_enabled = False

if "vector_model" not in st.session_state:
    st.session_state.vector_model = "all-MiniLM-L6-v2"

if "vector_similarity_threshold" not in st.session_state:
    st.session_state.vector_similarity_threshold = 0.5

if "rag_enabled" not in st.session_state:
    st.session_state.rag_enabled = False

if "rag_top_k" not in st.session_state:
    st.session_state.rag_top_k = 3

if "rag_max_tokens" not in st.session_state:
    st.session_state.rag_max_tokens = 500
```

### Configuration Export/Import

Extend Phase 12's config manager to include:
```json
{
  "vector_search": {
    "enabled": true,
    "model": "all-MiniLM-L6-v2",
    "similarity_threshold": 0.5
  },
  "rag": {
    "enabled": false,
    "top_k": 3,
    "max_tokens": 500
  }
}
```

## User Experience

### First-Time Setup

1. User enables "Vector Search" in settings
2. System prompts: "Index existing conversations? (47 found)"
3. Progress bar: "Indexing: 23/47 (5s remaining)..."
4. Completion: "✅ Indexed 47 conversations"
5. Search immediately available

### Daily Usage

**Semantic Conversation Search:**
```
User types: "machine learning projects"
Results show:
  • "Building Neural Network" (87% match)
  • "Training Classification Model" (82% match)
  • "AI Model Discussion" (78% match)
```

**Knowledge Base Usage:**
```
Claude uses vector_add_knowledge() during conversation:
  "User prefers functional programming"

Later, Claude uses vector_search_knowledge():
  Query: "coding style preferences"
  Finds: "functional programming preference"

Claude adapts response accordingly
```

**RAG Context:**
```
User: "How should I structure my API?"

System retrieves from knowledge base:
  • "User prefers FastAPI framework"
  • "User uses RESTful patterns"
  • "User likes clean code architecture"

Claude's response incorporates this context
```

### Settings Management

**Vector Search Section:**
```
⚙️ Vector Search Settings

[x] Enable Semantic Search

Embedding Model: [MiniLM-L6-v2 ▼]
├─ MiniLM-L6 (Fast, 90MB) ← Recommended
├─ MiniLM-L12 (Better, 134MB)
└─ MPNet (Best, 438MB)

Similarity Threshold: [────●────] 0.5
(Higher = stricter matching)

Indexing Status:
✅ 47/47 conversations indexed
Last indexed: 5 minutes ago

[Re-index All] [Clear Index]
```

**RAG Settings:**
```
🧠 RAG Context Augmentation

[ ] Enable RAG (Experimental)

When enabled, relevant knowledge is automatically
added to conversations for better context.

Top Results: [──●──] 3
Max Tokens: [────●──] 500
```

## Testing Strategy

### Unit Tests

**Vector DB Tests:**
```python
def test_vector_db_init()
def test_create_collection()
def test_add_documents()
def test_query_documents()
def test_delete_documents()
def test_collection_count()
def test_list_collections()
def test_delete_collection()
def test_batch_operations()
def test_error_handling()
```

**Embedding Tests:**
```python
def test_embedding_generation()
def test_batch_embedding()
def test_embedding_similarity()
def test_model_loading()
def test_embedding_dimensions()
```

**Indexing Tests:**
```python
def test_index_conversation()
def test_index_batch()
def test_update_index()
def test_remove_from_index()
def test_indexing_stats()
def test_text_extraction()
def test_chunking_strategy()
def test_progress_callback()
```

**Search Tests:**
```python
def test_semantic_search()
def test_search_with_filters()
def test_similarity_threshold()
def test_search_ranking()
def test_hybrid_search()
def test_empty_results()
def test_invalid_query()
def test_search_performance()
def test_top_k_results()
def test_metadata_filtering()
```

**Knowledge Base Tests:**
```python
def test_add_fact()
def test_search_facts()
def test_update_confidence()
def test_delete_fact()
def test_related_facts()
def test_export_knowledge()
def test_import_knowledge()
def test_category_filtering()
```

### Integration Tests

```python
def test_full_indexing_workflow()
def test_search_workflow()
def test_rag_augmentation()
def test_tool_integration()
def test_ui_integration()
```

### Performance Tests

```python
def test_embedding_speed()
def test_search_speed()
def test_indexing_large_dataset()
def test_memory_usage()
def test_concurrent_operations()
```

## Success Metrics

### Functional Goals
- ✅ Vector search successfully indexes conversations
- ✅ Semantic search returns relevant results
- ✅ Similarity scores are meaningful (0.5-1.0 range)
- ✅ Knowledge base stores and retrieves facts
- ✅ RAG augmentation improves responses
- ✅ All tests pass (50+ tests)

### Performance Goals
- ✅ Embedding: < 100ms per text (Pi-5)
- ✅ Search: < 200ms per query
- ✅ Indexing: < 15s for 100 conversations
- ✅ Memory: < 800MB total usage
- ✅ UI remains responsive during operations

### User Experience Goals
- ✅ Setup takes < 30 seconds
- ✅ Search results are more relevant than keyword
- ✅ System works with vector search disabled
- ✅ Clear feedback during long operations
- ✅ Settings are intuitive

## Future Enhancements (Phase 14+)

### Advanced Features
1. **Multiple Vector Stores**
   - Per-project vector databases
   - Shareable knowledge bases
   - Team collaboration

2. **Advanced RAG**
   - Multi-query retrieval
   - Reranking with cross-encoders
   - Source attribution

3. **Embeddings Management**
   - Custom embeddings
   - Fine-tuned models
   - Embedding visualization

4. **Knowledge Graph**
   - Relationship mapping
   - Entity extraction
   - Graph queries

5. **Dataset Creation** (from original moonshot)
   - Create training datasets from conversations
   - Export for fine-tuning
   - Dataset management UI

### Integrations
- Export vector DB to cloud
- Import from external knowledge bases
- API for external tools

## Risk Mitigation

### Potential Issues & Solutions

**Issue:** Large model download on first run
**Solution:** Show download progress, offer model selection, cache downloads

**Issue:** Slow indexing on Pi-5
**Solution:** Background indexing, batch processing, progress indication, cancellable

**Issue:** High memory usage
**Solution:** Lazy loading, model unloading when idle, memory monitoring

**Issue:** Poor search results
**Solution:** Similarity threshold tuning, hybrid search, result ranking

**Issue:** Compatibility issues
**Solution:** Fallback to keyword search, error handling, clear error messages

**Issue:** Storage space
**Solution:** Periodic cleanup, compression, user control over indexed collections

## Documentation

### User Documentation
- `docs/VECTOR_SEARCH.md` - User guide
- `docs/KNOWLEDGE_BASE.md` - Knowledge base guide
- `docs/RAG_GUIDE.md` - RAG usage guide

### Developer Documentation
- `docs/VECTOR_API.md` - API reference
- `docs/EMBEDDING_MODELS.md` - Model comparison
- `docs/PERFORMANCE_TUNING.md` - Optimization guide

## Conclusion

Phase 13 adds a powerful "cortical layer" to Apex Aurum without disrupting existing functionality. The toggleable vector search system enables:

✅ **Semantic conversation search** - Find by meaning, not just keywords
✅ **Knowledge persistence** - Remember and recall facts across conversations
✅ **RAG augmentation** - Automatically enhance context with relevant information
✅ **Document search** - Find code and docs by semantic meaning
✅ **Future-ready** - Foundation for advanced AI features

The hybrid architecture keeps the fast, simple key-value memory for operational data while adding semantic understanding where it matters. All features are optional and toggleable, ensuring the system remains performant even with vector search disabled.

**Implementation Priority:**
1. Core infrastructure (vector DB, embeddings)
2. Conversation search (most impactful)
3. Knowledge base (enables RAG)
4. RAG augmentation (advanced feature)
5. Document indexing (bonus feature)

**Estimated Timeline:**
- Phase 13.1-13.3: 2-3 hours (core + search)
- Phase 13.4-13.6: 2-3 hours (UI + knowledge + RAG)
- Phase 13.7-13.8: 1-2 hours (docs + testing)
- **Total: 5-8 hours of development**

Let's build this cortical layer! 🧠🚀
