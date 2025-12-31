"""
Test Vector Search Tools

Tests the Claude-accessible vector search tools:
- vector_add
- vector_search
- vector_delete
- vector_list_collections
- vector_get_stats
- vector_add_knowledge
- vector_search_knowledge
"""

import logging
from tools.vector_search import (
    vector_add,
    vector_search,
    vector_delete,
    vector_list_collections,
    vector_get_stats,
    vector_add_knowledge,
    vector_search_knowledge
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_operations():
    """Test basic vector operations"""
    logger.info("\n=== Test Basic Operations ===")

    # Test 1: Add documents
    logger.info("Test 1: Adding documents...")
    result1 = vector_add(
        text="Python is a high-level programming language known for its simplicity",
        metadata={"category": "programming", "language": "python"},
        collection="test_docs"
    )
    logger.info(f"Add result: {result1}")
    assert result1["success"], "Failed to add document 1"

    result2 = vector_add(
        text="JavaScript is used for web development and runs in browsers",
        metadata={"category": "programming", "language": "javascript"},
        collection="test_docs"
    )
    assert result2["success"], "Failed to add document 2"

    result3 = vector_add(
        text="Machine learning is a subset of artificial intelligence",
        metadata={"category": "ai", "topic": "ml"},
        collection="test_docs"
    )
    assert result3["success"], "Failed to add document 3"

    logger.info("✅ Added 3 documents successfully")

    # Test 2: List collections
    logger.info("\nTest 2: Listing collections...")
    collections = vector_list_collections()
    logger.info(f"Collections: {collections}")
    assert "test_docs" in collections, "test_docs collection not found"
    logger.info("✅ Collection listing works")

    # Test 3: Get stats
    logger.info("\nTest 3: Getting collection stats...")
    stats = vector_get_stats("test_docs")
    logger.info(f"Stats: {stats}")
    assert stats["count"] == 3, f"Expected 3 documents, got {stats['count']}"
    logger.info("✅ Stats retrieval works")

    # Test 4: Search
    logger.info("\nTest 4: Semantic search...")
    results = vector_search(
        query="coding languages for software development",
        collection="test_docs",
        top_k=2
    )
    logger.info(f"Search results: {len(results)} matches")
    for i, result in enumerate(results):
        logger.info(f"  {i+1}. {result['text'][:60]}... (similarity: {result.get('similarity', 'N/A'):.3f})")

    assert len(results) == 2, f"Expected 2 results, got {len(results)}"
    assert "Python" in results[0]["text"] or "JavaScript" in results[0]["text"], "Wrong results returned"
    logger.info("✅ Semantic search works")

    # Test 5: Search with filter
    logger.info("\nTest 5: Search with metadata filter...")
    filtered_results = vector_search(
        query="programming",
        collection="test_docs",
        top_k=5,
        filter={"category": "programming"}
    )
    logger.info(f"Filtered results: {len(filtered_results)} matches")
    assert len(filtered_results) == 2, "Filter didn't work correctly"
    logger.info("✅ Filtered search works")

    # Test 6: Delete
    logger.info("\nTest 6: Deleting document...")
    delete_result = vector_delete(result1["id"], "test_docs")
    logger.info(f"Delete result: {delete_result}")
    assert delete_result["success"], "Failed to delete document"

    # Verify deletion
    stats_after = vector_get_stats("test_docs")
    assert stats_after["count"] == 2, "Document not deleted"
    logger.info("✅ Document deletion works")

    return True


def test_knowledge_base():
    """Test knowledge base convenience functions"""
    logger.info("\n=== Test Knowledge Base Functions ===")

    # Add facts
    logger.info("Adding facts to knowledge base...")

    fact1 = vector_add_knowledge(
        fact="User prefers functional programming paradigm",
        category="preferences",
        confidence=0.9,
        source="conversation_test"
    )
    assert fact1["success"], "Failed to add fact 1"
    logger.info(f"Added fact 1: {fact1['id']}")

    fact2 = vector_add_knowledge(
        fact="FastAPI is a modern web framework for Python",
        category="technical",
        confidence=1.0,
        source="documentation"
    )
    assert fact2["success"], "Failed to add fact 2"
    logger.info(f"Added fact 2: {fact2['id']}")

    fact3 = vector_add_knowledge(
        fact="User is working on a machine learning project",
        category="project",
        confidence=0.8,
        source="conversation_test"
    )
    assert fact3["success"], "Failed to add fact 3"
    logger.info(f"Added fact 3: {fact3['id']}")

    logger.info("✅ Added 3 facts to knowledge base")

    # Search knowledge base
    logger.info("\nSearching knowledge base...")

    results = vector_search_knowledge(
        query="What are the user's programming preferences?",
        top_k=2
    )
    logger.info(f"Knowledge search results: {len(results)} matches")
    for i, result in enumerate(results):
        logger.info(f"  {i+1}. {result['text']} (sim: {result.get('similarity', 0):.3f}, conf: {result['metadata'].get('confidence', 'N/A')})")

    assert len(results) > 0, "No results from knowledge search"
    logger.info("✅ Knowledge search works")

    # Search by category
    logger.info("\nSearching by category...")

    tech_results = vector_search_knowledge(
        query="web framework",
        category="technical",
        top_k=5
    )
    logger.info(f"Technical knowledge: {len(tech_results)} matches")
    assert len(tech_results) > 0, "No technical results found"
    assert "FastAPI" in tech_results[0]["text"], "Wrong result for technical category"
    logger.info("✅ Category filtering works")

    # Search with confidence filter
    logger.info("\nSearching with confidence filter...")

    confident_results = vector_search_knowledge(
        query="programming",
        min_confidence=0.9,
        top_k=5
    )
    logger.info(f"High-confidence results: {len(confident_results)} matches")
    for result in confident_results:
        conf = result['metadata'].get('confidence', 0)
        assert conf >= 0.9, f"Result has confidence {conf} < 0.9"
    logger.info("✅ Confidence filtering works")

    return True


def test_error_handling():
    """Test error handling"""
    logger.info("\n=== Test Error Handling ===")

    # Test search on empty collection
    logger.info("Testing search on empty/non-existent collection...")
    empty_results = vector_search(
        query="test",
        collection="empty_collection_xyz",
        top_k=5
    )
    logger.info(f"Empty collection result: {empty_results}")
    assert "error" in empty_results or empty_results.get("success") == False, "Should handle empty collection"
    logger.info("✅ Empty collection handling works")

    # Test delete non-existent document
    logger.info("\nTesting delete non-existent document...")
    delete_result = vector_delete("non_existent_id_xyz", "test_docs")
    # ChromaDB doesn't error on non-existent deletes, just logs
    logger.info(f"Delete result: {delete_result}")
    logger.info("✅ Non-existent delete handling works")

    return True


def test_full_workflow():
    """Test complete workflow"""
    logger.info("\n=== Test Complete Workflow ===")

    collection_name = "workflow_test"

    # Scenario: User asks about a topic, we check knowledge, add if new
    logger.info("Scenario: User asks 'What is React?'")

    # Search existing knowledge
    results = vector_search(
        query="What is React?",
        collection=collection_name,
        top_k=1
    )

    if isinstance(results, list) and len(results) > 0:
        logger.info(f"Found existing knowledge: {results[0]['text'][:60]}...")
    else:
        logger.info("No existing knowledge found. Adding new information...")

        # Add new knowledge
        add_result = vector_add(
            text="React is a JavaScript library for building user interfaces, developed by Facebook",
            metadata={"topic": "react", "category": "web-development"},
            collection=collection_name
        )
        logger.info(f"Added new knowledge: {add_result['id']}")

    # Search again
    results = vector_search(
        query="JavaScript UI libraries",
        collection=collection_name,
        top_k=3
    )
    logger.info(f"Search for UI libraries: {len(results)} results")
    assert len(results) > 0, "Should find React info"

    logger.info("✅ Full workflow works")

    return True


def main():
    """Run all tests"""
    logger.info("🧪 Testing Vector Search Tools\n")

    try:
        # Test 1: Basic operations
        test_basic_operations()

        # Test 2: Knowledge base
        test_knowledge_base()

        # Test 3: Error handling
        test_error_handling()

        # Test 4: Full workflow
        test_full_workflow()

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("ALL TESTS PASSED! ✅")
        logger.info("=" * 60)
        logger.info("Vector search tools are working correctly:")
        logger.info("  ✅ Document addition")
        logger.info("  ✅ Semantic search")
        logger.info("  ✅ Metadata filtering")
        logger.info("  ✅ Document deletion")
        logger.info("  ✅ Knowledge base operations")
        logger.info("  ✅ Category and confidence filtering")
        logger.info("  ✅ Error handling")
        logger.info("  ✅ Complete workflows")
        logger.info("=" * 60)

        # Count tools
        collections = vector_list_collections()
        logger.info(f"\nActive collections: {len(collections)}")
        for coll_name in collections:
            stats = vector_get_stats(coll_name)
            logger.info(f"  • {coll_name}: {stats.get('count', 0)} documents")

        return True

    except Exception as e:
        logger.error(f"\n❌ TEST FAILED: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
