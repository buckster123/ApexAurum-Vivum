"""
Test Suite for Phase 12: Export/Import & Conversation Management

Tests:
1. Export engine (all formats)
2. Import engine (format detection, validation)
3. Configuration manager
4. Conversation metadata (tags, favorites, search)
5. Batch operations
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.export_engine import ExportEngine, JSONExporter, MarkdownExporter
from core.import_engine import ImportEngine
from core.config_manager import ConfigManager
from main import AppState


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_conversation():
    """Create sample conversation for testing"""
    return {
        "id": "test_conv_001",
        "title": "Test Conversation",
        "created_at": "2025-01-01T10:00:00",
        "updated_at": "2025-01-01T12:00:00",
        "messages": [
            {
                "role": "user",
                "content": "Hello, how are you?",
                "timestamp": "2025-01-01T10:00:00"
            },
            {
                "role": "assistant",
                "content": "I'm doing well, thank you! How can I help you today?",
                "timestamp": "2025-01-01T10:01:00"
            },
            {
                "role": "user",
                "content": "Can you explain quantum computing?",
                "timestamp": "2025-01-01T11:00:00"
            },
            {
                "role": "assistant",
                "content": "Quantum computing uses quantum mechanical phenomena...",
                "timestamp": "2025-01-01T11:05:00"
            }
        ],
        "metadata": {
            "model_used": "claude-sonnet-4-5-20250929",
            "tags": ["technology", "quantum"],
            "favorite": True,
            "archived": False
        }
    }


@pytest.fixture
def export_engine():
    """Create export engine instance"""
    return ExportEngine()


@pytest.fixture
def import_engine():
    """Create import engine instance"""
    return ImportEngine()


@pytest.fixture
def config_manager():
    """Create config manager instance"""
    return ConfigManager()


@pytest.fixture
def app_state(tmp_path):
    """Create app state instance with temp storage"""
    storage_path = tmp_path / "conversations.json"
    state = AppState()
    state.conversations_file = storage_path

    # Ensure clean state
    if storage_path.exists():
        storage_path.unlink()

    return state


@pytest.fixture
def mock_session_state():
    """Create mock session state for config testing"""
    class MockSessionState:
        def __init__(self):
            self.model = "claude-sonnet-4-5-20250929"
            self.temperature = 0.7
            self.max_tokens = 4096
            self.tools_enabled = True
            self.system_prompt = "You are a helpful assistant"
            self.streaming_enabled = True
            self.show_tool_execution = True
            self.show_partial_results = True
            self.context_strategy = "balanced"
            self.preserve_recent_count = 10
            self.auto_summarize = True

    return MockSessionState()


# ============================================================================
# Export Engine Tests
# ============================================================================

def test_export_json(export_engine, sample_conversation):
    """Test JSON export"""
    result = export_engine.export_conversation(
        sample_conversation,
        "json",
        {"include_metadata": True, "include_stats": True}
    )

    assert result is not None
    assert isinstance(result, bytes)

    # Parse and verify
    data = json.loads(result.decode("utf-8"))
    assert data["id"] == "test_conv_001"
    assert len(data["messages"]) == 4
    assert "statistics" in data
    assert "exported_at" in data


def test_export_markdown(export_engine, sample_conversation):
    """Test Markdown export"""
    result = export_engine.export_conversation(
        sample_conversation,
        "markdown",
        {}
    )

    assert result is not None
    assert isinstance(result, bytes)

    content = result.decode("utf-8")
    assert "# Test Conversation" in content
    assert "**User:**" in content
    assert "**Assistant:**" in content
    assert "quantum" in content.lower()


def test_export_html(export_engine, sample_conversation):
    """Test HTML export"""
    result = export_engine.export_conversation(
        sample_conversation,
        "html",
        {}
    )

    assert result is not None
    assert isinstance(result, bytes)

    content = result.decode("utf-8")
    assert "<!DOCTYPE html>" in content
    assert "<title>Test Conversation</title>" in content
    assert "<div class='message user'>" in content
    assert "<div class='message assistant'>" in content


def test_export_txt(export_engine, sample_conversation):
    """Test TXT export"""
    result = export_engine.export_conversation(
        sample_conversation,
        "txt",
        {}
    )

    assert result is not None
    assert isinstance(result, bytes)

    content = result.decode("utf-8")
    assert "Test Conversation" in content
    assert "USER:" in content
    assert "ASSISTANT:" in content


def test_export_multiple_combined(export_engine, sample_conversation):
    """Test exporting multiple conversations combined"""
    conversations = [sample_conversation, sample_conversation.copy()]
    conversations[1]["id"] = "test_conv_002"

    result = export_engine.export_multiple(
        conversations,
        "json",
        combine=True
    )

    assert result is not None
    data = json.loads(result.decode("utf-8"))
    assert "conversations" in data
    assert len(data["conversations"]) == 2
    assert data["count"] == 2


def test_get_mime_type(export_engine):
    """Test MIME type detection"""
    assert export_engine.get_mime_type("json") == "application/json"
    assert export_engine.get_mime_type("markdown") == "text/markdown"
    assert export_engine.get_mime_type("html") == "text/html"
    assert export_engine.get_mime_type("txt") == "text/plain"


# ============================================================================
# Import Engine Tests
# ============================================================================

def test_import_json(import_engine, sample_conversation):
    """Test JSON import"""
    # Export then import
    json_data = json.dumps(sample_conversation).encode("utf-8")

    result = import_engine.import_conversation(json_data, format="json")

    assert result is not None
    assert len(result["messages"]) == 4
    assert result["metadata"]["tags"] == ["technology", "quantum"]


def test_import_markdown(import_engine):
    """Test Markdown import"""
    markdown_content = """# My Conversation

**Created:** 2025-01-01

**User:**
Hello there

**Assistant:**
Hello! How can I help you?

**User:**
Tell me about AI

**Assistant:**
AI stands for Artificial Intelligence...
"""

    result = import_engine.import_conversation(
        markdown_content.encode("utf-8"),
        format="markdown"
    )

    assert result is not None
    assert result["title"] == "My Conversation"
    assert len(result["messages"]) == 4
    assert result["messages"][0]["role"] == "user"
    assert result["messages"][0]["content"] == "Hello there"


def test_format_detection_json(import_engine):
    """Test auto-detection of JSON format"""
    json_data = json.dumps({"title": "Test", "messages": []}).encode("utf-8")
    format = import_engine.detect_format(json_data)
    assert format == "json"


def test_format_detection_markdown(import_engine):
    """Test auto-detection of Markdown format"""
    markdown_data = b"# Title\n\n**User:** Hello"
    format = import_engine.detect_format(markdown_data)
    assert format == "markdown"


def test_import_validation(import_engine):
    """Test validation during import"""
    # Invalid conversation (missing messages)
    invalid_conv = {
        "title": "Test"
        # Missing "messages" field
    }

    with pytest.raises(ValueError, match="Validation failed"):
        import_engine.import_conversation(
            json.dumps(invalid_conv).encode("utf-8"),
            format="json",
            validate=True
        )


def test_conversation_normalization(import_engine, sample_conversation):
    """Test that imported conversations are normalized"""
    json_data = json.dumps(sample_conversation).encode("utf-8")
    result = import_engine.import_conversation(json_data, format="json")

    # Should have new ID
    assert result["id"] != sample_conversation["id"]
    assert result["id"].startswith("conv_")

    # Should have import metadata
    assert "imported_at" in result["metadata"]


# ============================================================================
# Configuration Manager Tests
# ============================================================================

def test_export_config(config_manager, mock_session_state):
    """Test configuration export"""
    config = config_manager.export_config(mock_session_state)

    assert config is not None
    assert config["version"] == "1.0"
    assert "exported_at" in config
    assert "settings" in config
    assert "system_prompts" in config
    assert "ui_preferences" in config

    # Verify settings
    assert config["settings"]["model"] == "claude-sonnet-4-5-20250929"
    assert config["settings"]["temperature"] == 0.7


def test_import_config(config_manager, mock_session_state):
    """Test configuration import"""
    # Create config to import
    config = {
        "version": "1.0",
        "settings": {
            "model": "claude-opus-4-5-20251101",
            "temperature": 0.9,
            "max_tokens": 8192,
            "tools_enabled": False
        },
        "system_prompts": [
            {"name": "Test", "content": "Test prompt"}
        ],
        "ui_preferences": {
            "streaming_enabled": False,
            "show_tool_execution": False
        }
    }

    success, messages = config_manager.import_config(
        config,
        mock_session_state,
        merge=False
    )

    assert success is True
    assert len(messages) > 0
    assert mock_session_state.model == "claude-opus-4-5-20251101"
    assert mock_session_state.temperature == 0.9
    assert mock_session_state.streaming_enabled is False


def test_validate_config_valid(config_manager):
    """Test validation of valid config"""
    config = {
        "version": "1.0",
        "settings": {
            "model": "claude-sonnet-4-5-20250929",
            "temperature": 0.7,
            "max_tokens": 4096
        }
    }

    is_valid, errors = config_manager.validate_config(config)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_config_invalid(config_manager):
    """Test validation of invalid config"""
    config = {
        # Missing "version"
        "settings": {
            "temperature": 2.0,  # Invalid (> 1.0)
            "max_tokens": 10000,  # Invalid (> 8192)
            "model": "invalid-model"  # Invalid model
        }
    }

    is_valid, errors = config_manager.validate_config(config)
    assert is_valid is False
    assert len(errors) > 0


def test_reset_to_defaults(config_manager, mock_session_state):
    """Test resetting to default configuration"""
    # Change some values
    mock_session_state.model = "claude-opus-4-5-20251101"
    mock_session_state.temperature = 0.1

    # Reset
    config_manager.reset_to_defaults(mock_session_state)

    # Should be back to defaults
    assert mock_session_state.model == "claude-sonnet-4-5-20250929"
    assert mock_session_state.temperature == 0.7


def test_export_to_json(config_manager, mock_session_state):
    """Test exporting config as JSON string"""
    json_str = config_manager.export_to_json(mock_session_state)

    assert json_str is not None
    assert isinstance(json_str, str)

    # Should be valid JSON
    data = json.loads(json_str)
    assert data["version"] == "1.0"
    assert "settings" in data


# ============================================================================
# AppState Metadata Tests
# ============================================================================

def test_add_tag(app_state, sample_conversation):
    """Test adding tags to conversation"""
    # Save conversation
    app_state.save_conversation(
        sample_conversation["messages"],
        sample_conversation["metadata"]
    )

    conversations = app_state.get_conversations()
    conv_id = conversations[0]["id"]

    # Add tag
    app_state.add_tag(conv_id, "test-tag")

    # Verify
    conversations = app_state.get_conversations()
    tags = conversations[0]["metadata"].get("tags", [])
    assert "test-tag" in tags


def test_remove_tag(app_state, sample_conversation):
    """Test removing tags from conversation"""
    app_state.save_conversation(
        sample_conversation["messages"],
        sample_conversation["metadata"]
    )

    conversations = app_state.get_conversations()
    conv_id = conversations[0]["id"]

    # Remove existing tag
    app_state.remove_tag(conv_id, "technology")

    # Verify
    conversations = app_state.get_conversations()
    tags = conversations[0]["metadata"].get("tags", [])
    assert "technology" not in tags


def test_set_favorite(app_state, sample_conversation):
    """Test marking conversation as favorite"""
    sample_conversation["metadata"]["favorite"] = False
    app_state.save_conversation(
        sample_conversation["messages"],
        sample_conversation["metadata"]
    )

    conversations = app_state.get_conversations()
    conv_id = conversations[0]["id"]

    # Set favorite
    app_state.set_favorite(conv_id, True)

    # Verify
    conversations = app_state.get_conversations()
    assert conversations[0]["metadata"]["favorite"] is True


def test_set_archived(app_state, sample_conversation):
    """Test archiving conversation"""
    app_state.save_conversation(
        sample_conversation["messages"],
        sample_conversation["metadata"]
    )

    conversations = app_state.get_conversations()
    conv_id = conversations[0]["id"]

    # Archive
    app_state.set_archived(conv_id, True)

    # Verify
    conversations = app_state.get_conversations()
    assert conversations[0]["metadata"]["archived"] is True


def test_get_all_tags(app_state, sample_conversation):
    """Test getting all unique tags"""
    # Save multiple conversations with different tags
    app_state.save_conversation(
        sample_conversation["messages"],
        {"tags": ["python", "coding"]}
    )
    app_state.save_conversation(
        sample_conversation["messages"],
        {"tags": ["python", "ai"]}
    )

    tags = app_state.get_all_tags()
    assert set(tags) == {"python", "coding", "ai"}


def test_search_conversations_by_text(app_state, sample_conversation):
    """Test searching conversations by text"""
    app_state.save_conversation(
        sample_conversation["messages"],
        sample_conversation["metadata"]
    )

    # Search for quantum
    results = app_state.search_conversations("quantum", filters={})
    assert len(results) == 1

    # Search for non-existent term
    results = app_state.search_conversations("nonexistent", filters={})
    assert len(results) == 0


def test_search_with_filters(app_state, sample_conversation):
    """Test searching with filters"""
    app_state.save_conversation(
        sample_conversation["messages"],
        {"tags": ["technology"], "favorite": True}
    )
    app_state.save_conversation(
        sample_conversation["messages"],
        {"tags": ["science"], "favorite": False}
    )

    # Filter by favorite
    results = app_state.search_conversations(
        "",
        filters={"favorite": True}
    )
    assert len(results) == 1

    # Filter by tag
    results = app_state.search_conversations(
        "",
        filters={"tags": ["technology"]}
    )
    assert len(results) == 1


def test_batch_delete(app_state, sample_conversation):
    """Test batch deleting conversations"""
    # Save multiple conversations
    app_state.save_conversation(sample_conversation["messages"], {})
    app_state.save_conversation(sample_conversation["messages"], {})
    app_state.save_conversation(sample_conversation["messages"], {})

    conversations = app_state.get_conversations()
    assert len(conversations) == 3

    # Delete first two
    conv_ids = [conversations[0]["id"], conversations[1]["id"]]
    app_state.batch_delete(conv_ids)

    # Verify
    conversations = app_state.get_conversations()
    assert len(conversations) == 1


def test_batch_tag(app_state, sample_conversation):
    """Test batch tagging conversations"""
    # Save multiple conversations
    app_state.save_conversation(sample_conversation["messages"], {})
    app_state.save_conversation(sample_conversation["messages"], {})

    conversations = app_state.get_conversations()
    conv_ids = [c["id"] for c in conversations]

    # Batch tag
    app_state.batch_tag(conv_ids, "batch-test")

    # Verify all have the tag
    conversations = app_state.get_conversations()
    for conv in conversations:
        tags = conv["metadata"].get("tags", [])
        assert "batch-test" in tags


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
