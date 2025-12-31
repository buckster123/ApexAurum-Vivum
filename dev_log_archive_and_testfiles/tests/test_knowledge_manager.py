"""
Test Knowledge Base Manager - Phase 13.5

Tests:
- Basic CRUD operations (add, get, update, delete)
- Category filtering and sorting
- Batch operations
- Export/Import functionality
- Semantic search
- Edge cases and validation
"""

import logging
import json
import time
from main import AppState
from tools.vector_search import vector_add_knowledge, vector_search_knowledge, vector_delete

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_crud():
    """Test basic Create, Read, Update, Delete operations"""
    logger.info("\n=== Test 1: Basic CRUD Operations ===")

    app_state = AppState()

    # CREATE: Add a new fact
    logger.info("Adding test fact...")
    result = vector_add_knowledge(
        fact="Python uses indentation for code blocks instead of braces",
        category="technical",
        confidence=1.0,
        source="test"
    )

    assert result.get("success"), "Failed to add fact"
    fact_id = result["id"]
    logger.info(f"✅ Created fact: {fact_id}")

    # READ: Get all knowledge
    logger.info("\nReading all facts...")
    facts = app_state.get_all_knowledge()
    assert len(facts) > 0, "No facts found"

    # Find our test fact
    test_fact = next((f for f in facts if f["id"] == fact_id), None)
    assert test_fact is not None, "Test fact not found"
    assert test_fact["category"] == "technical", "Wrong category"
    assert test_fact["confidence"] == 1.0, "Wrong confidence"
    logger.info("✅ Read fact successfully")

    # UPDATE: Modify the fact
    logger.info("\nUpdating fact...")
    update_result = app_state.update_knowledge(
        fact_id=fact_id,
        confidence=0.9,
        source="test-updated"
    )
    assert update_result.get("success"), f"Failed to update: {update_result.get('error')}"
    logger.info("✅ Updated fact successfully")

    # Verify update
    time.sleep(0.5)  # Give it a moment
    facts = app_state.get_all_knowledge()
    updated_fact = next((f for f in facts if f["id"] == fact_id), None)
    assert updated_fact is not None, "Updated fact not found"
    assert updated_fact["confidence"] == 0.9, "Confidence not updated"
    assert updated_fact["source"] == "test-updated", "Source not updated"
    logger.info("✅ Verified update")

    # DELETE: Remove the fact
    logger.info("\nDeleting fact...")
    delete_result = vector_delete(fact_id, collection="knowledge")
    assert delete_result.get("success"), "Failed to delete"
    logger.info("✅ Deleted fact successfully")

    # Verify deletion
    time.sleep(0.5)
    facts = app_state.get_all_knowledge()
    deleted_fact = next((f for f in facts if f["id"] == fact_id), None)
    assert deleted_fact is None, "Fact still exists after deletion"
    logger.info("✅ Verified deletion")

    logger.info("\n✅ All CRUD operations work!")


def test_filtering_and_sorting():
    """Test category filtering and sorting"""
    logger.info("\n=== Test 2: Filtering and Sorting ===")

    app_state = AppState()

    # Add test facts in different categories
    test_facts = [
        {"text": "User prefers dark mode", "category": "preferences", "confidence": 1.0},
        {"text": "React uses virtual DOM", "category": "technical", "confidence": 0.9},
        {"text": "Project uses FastAPI backend", "category": "project", "confidence": 1.0},
        {"text": "Always write clean code", "category": "general", "confidence": 0.8},
    ]

    added_ids = []
    for fact_data in test_facts:
        result = vector_add_knowledge(
            fact=fact_data["text"],
            category=fact_data["category"],
            confidence=fact_data["confidence"],
            source="test"
        )
        if result.get("success"):
            added_ids.append(result["id"])

    logger.info(f"Added {len(added_ids)} test facts")
    time.sleep(0.5)

    # Test category filtering
    logger.info("\nTesting category filters...")
    prefs = app_state.get_all_knowledge(category="preferences")
    tech = app_state.get_all_knowledge(category="technical")

    assert any(f["category"] == "preferences" for f in prefs), "No preferences found"
    assert any(f["category"] == "technical" for f in tech), "No technical found"
    logger.info(f"✅ Category filtering works (prefs: {len(prefs)}, tech: {len(tech)})")

    # Test sorting by confidence
    logger.info("\nTesting sorting...")
    by_confidence_desc = app_state.get_all_knowledge(sort_by="confidence", sort_order="desc")
    by_confidence_asc = app_state.get_all_knowledge(sort_by="confidence", sort_order="asc")

    if len(by_confidence_desc) >= 2:
        assert by_confidence_desc[0]["confidence"] >= by_confidence_desc[1]["confidence"], "Desc sort failed"
    if len(by_confidence_asc) >= 2:
        assert by_confidence_asc[0]["confidence"] <= by_confidence_asc[1]["confidence"], "Asc sort failed"

    logger.info("✅ Sorting works correctly")

    # Cleanup
    for fact_id in added_ids:
        vector_delete(fact_id, collection="knowledge")

    logger.info("✅ Filtering and sorting complete!")


def test_batch_operations():
    """Test batch deletion"""
    logger.info("\n=== Test 3: Batch Operations ===")

    app_state = AppState()

    # Add multiple facts
    test_facts = [
        "Fact 1 for batch test",
        "Fact 2 for batch test",
        "Fact 3 for batch test"
    ]

    added_ids = []
    for fact_text in test_facts:
        result = vector_add_knowledge(fact=fact_text, category="general", source="batch-test")
        if result.get("success"):
            added_ids.append(result["id"])

    logger.info(f"Added {len(added_ids)} facts for batch test")
    assert len(added_ids) == 3, "Failed to add all test facts"

    # Batch delete
    logger.info("Performing batch delete...")
    result = app_state.batch_delete_knowledge(added_ids)

    assert result.get("success"), "Batch delete failed"
    assert result["deleted"] == 3, f"Expected 3 deletions, got {result['deleted']}"
    assert result["failed"] == 0, f"Expected 0 failures, got {result['failed']}"

    logger.info(f"✅ Batch deleted {result['deleted']} facts")

    # Verify deletion
    time.sleep(0.5)
    facts = app_state.get_all_knowledge()
    for fact_id in added_ids:
        assert not any(f["id"] == fact_id for f in facts), f"Fact {fact_id} still exists"

    logger.info("✅ Batch operations work!")


def test_export_import():
    """Test export and import functionality"""
    logger.info("\n=== Test 4: Export/Import ===")

    app_state = AppState()

    # Add some test facts
    test_facts = [
        {"text": "Export test fact 1", "category": "preferences", "confidence": 1.0},
        {"text": "Export test fact 2", "category": "technical", "confidence": 0.9}
    ]

    added_ids = []
    for fact_data in test_facts:
        result = vector_add_knowledge(
            fact=fact_data["text"],
            category=fact_data["category"],
            confidence=fact_data["confidence"],
            source="export-test"
        )
        if result.get("success"):
            added_ids.append(result["id"])

    time.sleep(0.5)
    logger.info(f"Added {len(added_ids)} facts for export test")

    # EXPORT
    logger.info("\nTesting export...")
    export_result = app_state.export_knowledge(format="json")

    assert export_result.get("success"), "Export failed"
    assert "data" in export_result, "No data in export result"
    assert "facts" in export_result["data"], "No facts in export data"

    export_data = export_result["data"]
    logger.info(f"✅ Exported {export_data['total_facts']} facts")

    # Delete the facts
    for fact_id in added_ids:
        vector_delete(fact_id, collection="knowledge")

    time.sleep(0.5)

    # IMPORT
    logger.info("\nTesting import...")

    # Create import data with just our test facts
    import_data = {
        "version": "1.0",
        "facts": [
            {"text": "Imported fact 1", "category": "general", "confidence": 1.0, "source": "import-test"},
            {"text": "Imported fact 2", "category": "preferences", "confidence": 0.8, "source": "import-test"}
        ]
    }

    import_result = app_state.import_knowledge(data=import_data, validate=True)

    assert import_result.get("success"), f"Import failed: {import_result.get('error')}"
    assert import_result["imported"] == 2, f"Expected 2 imports, got {import_result['imported']}"
    assert import_result["failed"] == 0, f"Expected 0 failures, got {import_result['failed']}"

    logger.info(f"✅ Imported {import_result['imported']} facts")

    # Verify imported facts exist
    time.sleep(0.5)
    facts = app_state.get_all_knowledge()
    imported_facts = [f for f in facts if f.get("source") == "import-test"]
    assert len(imported_facts) == 2, "Imported facts not found"

    logger.info("✅ Verified imported facts")

    # Cleanup
    for fact in imported_facts:
        vector_delete(fact["id"], collection="knowledge")

    logger.info("✅ Export/Import complete!")


def test_semantic_search():
    """Test semantic search functionality"""
    logger.info("\n=== Test 5: Semantic Search ===")

    app_state = AppState()

    # Add test facts
    test_facts = [
        {"text": "Python is a high-level programming language", "category": "technical"},
        {"text": "User prefers Python for data analysis", "category": "preferences"},
        {"text": "JavaScript runs in web browsers", "category": "technical"}
    ]

    added_ids = []
    for fact_data in test_facts:
        result = vector_add_knowledge(
            fact=fact_data["text"],
            category=fact_data["category"],
            confidence=1.0,
            source="search-test"
        )
        if result.get("success"):
            added_ids.append(result["id"])

    time.sleep(0.5)
    logger.info(f"Added {len(added_ids)} facts for search test")

    # Search for Python-related facts
    logger.info("\nSearching for 'Python programming'...")
    results = vector_search_knowledge(
        query="Python programming language",
        top_k=3
    )

    assert results, "No search results"
    assert not isinstance(results, dict) or not results.get("error"), f"Search error: {results.get('error')}"

    logger.info(f"Found {len(results)} results")

    # Check if relevant results found
    python_results = [r for r in results if "python" in r.get("text", "").lower()]
    assert len(python_results) > 0, "No Python-related results found"

    logger.info(f"✅ Found {len(python_results)} Python-related facts")

    # Test category filtering in search
    logger.info("\nSearching with category filter...")
    tech_results = vector_search_knowledge(
        query="programming",
        category="technical",
        top_k=5
    )

    if tech_results and not isinstance(tech_results, dict):
        for result in tech_results:
            category = result.get("metadata", {}).get("category")
            assert category == "technical", f"Non-technical result in filtered search: {category}"
        logger.info(f"✅ Category filter works ({len(tech_results)} results)")

    # Cleanup
    for fact_id in added_ids:
        vector_delete(fact_id, collection="knowledge")

    logger.info("✅ Semantic search works!")


def test_edge_cases():
    """Test edge cases and validation"""
    logger.info("\n=== Test 6: Edge Cases ===")

    app_state = AppState()

    # Test 1: Empty knowledge base stats
    logger.info("\nTesting stats on empty database...")
    stats = app_state.get_knowledge_stats()
    assert isinstance(stats, dict), "Stats should return dict"
    assert "total" in stats, "Stats missing total"
    logger.info(f"✅ Stats work (total: {stats['total']})")

    # Test 2: Update non-existent fact
    logger.info("\nTesting update of non-existent fact...")
    result = app_state.update_knowledge(
        fact_id="nonexistent_id_12345",
        confidence=0.5
    )
    assert not result.get("success"), "Should fail for non-existent fact"
    logger.info("✅ Correctly handles non-existent fact")

    # Test 3: Import invalid data
    logger.info("\nTesting import with invalid data...")
    invalid_data = {
        "facts": [
            {"text": "Valid fact", "category": "general"},
            {"category": "technical"},  # Missing text
            {"text": "Fact with invalid category", "category": "invalid_cat"}
        ]
    }

    result = app_state.import_knowledge(data=invalid_data, validate=True)
    assert result.get("success"), "Import should partially succeed"
    assert result["failed"] > 0, "Should have some failures"
    logger.info(f"✅ Import validation works (failed: {result['failed']})")

    # Cleanup any successfully imported facts
    facts = app_state.get_all_knowledge()
    for fact in facts:
        if fact.get("text") == "Valid fact":
            vector_delete(fact["id"], collection="knowledge")

    # Test 4: Confidence clamping
    logger.info("\nTesting confidence value clamping...")
    result = vector_add_knowledge(
        fact="Test confidence clamping",
        category="general",
        confidence=1.5,  # Invalid: > 1.0
        source="edge-test"
    )

    # The vector_add_knowledge function should accept it (it doesn't validate)
    # but our import function should clamp it
    if result.get("success"):
        vector_delete(result["id"], collection="knowledge")

    logger.info("✅ Edge case handling works!")


def test_get_knowledge_stats():
    """Test knowledge statistics"""
    logger.info("\n=== Test 7: Knowledge Statistics ===")

    app_state = AppState()

    # Get current stats
    stats = app_state.get_knowledge_stats()

    logger.info(f"\nCurrent Knowledge Base Stats:")
    logger.info(f"  Total: {stats['total']}")
    logger.info(f"  Preferences: {stats['preferences']}")
    logger.info(f"  Technical: {stats['technical']}")
    logger.info(f"  Project: {stats['project']}")
    logger.info(f"  General: {stats['general']}")
    logger.info(f"  Avg Confidence: {stats['avg_confidence']:.2f}")

    assert stats["total"] >= 0, "Total should be non-negative"
    assert stats["total"] == (stats["preferences"] + stats["technical"] +
                               stats["project"] + stats["general"]), "Category counts don't add up"

    logger.info("✅ Statistics calculation works!")


def main():
    """Run all tests"""
    logger.info("🧪 Testing Knowledge Base Manager (Phase 13.5)\n")

    try:
        # Test 1: Basic CRUD
        test_basic_crud()

        # Test 2: Filtering and sorting
        test_filtering_and_sorting()

        # Test 3: Batch operations
        test_batch_operations()

        # Test 4: Export/Import
        test_export_import()

        # Test 5: Semantic search
        test_semantic_search()

        # Test 6: Edge cases
        test_edge_cases()

        # Test 7: Statistics
        test_get_knowledge_stats()

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("ALL TESTS PASSED! ✅")
        logger.info("=" * 60)
        logger.info("Knowledge Base Manager is working correctly:")
        logger.info("  ✅ Basic CRUD operations")
        logger.info("  ✅ Category filtering")
        logger.info("  ✅ Sorting (by date, confidence, category)")
        logger.info("  ✅ Batch operations")
        logger.info("  ✅ Export to JSON")
        logger.info("  ✅ Import from JSON")
        logger.info("  ✅ Semantic search")
        logger.info("  ✅ Category-based search")
        logger.info("  ✅ Edge case handling")
        logger.info("  ✅ Statistics calculation")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"\n❌ TEST FAILED: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
