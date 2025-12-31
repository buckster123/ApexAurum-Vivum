"""
Performance profiling for vector database on Pi-5

Tests:
- Embedding generation speed
- Batch embedding speed
- Search speed
- Indexing speed for various dataset sizes
"""

import time
import logging
from core.vector_db import create_vector_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def profile_embedding_speed():
    """Profile single embedding generation"""
    logger.info("\n=== Embedding Speed Test ===")

    db = create_vector_db()

    texts = [
        "Hello world, this is a test sentence.",
        "Artificial intelligence is transforming the world.",
        "Machine learning enables computers to learn from data without explicit programming.",
    ]

    # Warmup
    db.embedding_generator.encode(texts[0])

    # Profile single embeddings
    times = []
    for text in texts:
        start = time.time()
        embedding = db.embedding_generator.encode(text)
        elapsed = (time.time() - start) * 1000  # ms
        times.append(elapsed)
        logger.info(f"Embedding ({len(text)} chars): {elapsed:.1f}ms")

    avg_time = sum(times) / len(times)
    logger.info(f"Average embedding time: {avg_time:.1f}ms")

    return avg_time


def profile_batch_embedding():
    """Profile batch embedding"""
    logger.info("\n=== Batch Embedding Test ===")

    db = create_vector_db()

    # Create test data
    texts = [
        f"This is test document number {i} with some content about various topics."
        for i in range(100)
    ]

    start = time.time()
    embeddings = db.embedding_generator.encode(texts, show_progress=False)
    elapsed = time.time() - start

    logger.info(f"Batch embedding 100 documents: {elapsed:.2f}s")
    logger.info(f"Average per document: {(elapsed / 100) * 1000:.1f}ms")

    return elapsed


def profile_search_speed():
    """Profile search speed"""
    logger.info("\n=== Search Speed Test ===")

    db = create_vector_db()
    collection = db.get_or_create_collection("perf_test")

    # Add test documents
    texts = [
        f"Document {i}: This discusses topic {i % 10} with content about various subjects."
        for i in range(100)
    ]

    logger.info("Adding 100 documents...")
    start = time.time()
    collection.add(
        texts=texts,
        ids=[f"doc_{i}" for i in range(100)]
    )
    add_time = time.time() - start
    logger.info(f"Add time: {add_time:.2f}s")

    # Profile searches
    queries = [
        "topic about subjects",
        "document content discussion",
        "various information details"
    ]

    search_times = []
    for query in queries:
        start = time.time()
        results = collection.query(query, n_results=10)
        elapsed = (time.time() - start) * 1000  # ms
        search_times.append(elapsed)
        logger.info(f"Search '{query}': {elapsed:.1f}ms ({len(results['ids'])} results)")

    avg_search = sum(search_times) / len(search_times)
    logger.info(f"Average search time: {avg_search:.1f}ms")

    # Cleanup
    db.delete_collection("perf_test")

    return avg_search


def profile_large_dataset():
    """Profile with larger dataset"""
    logger.info("\n=== Large Dataset Test ===")

    db = create_vector_db()
    collection = db.get_or_create_collection("large_test")

    sizes = [10, 50, 100, 200]

    for size in sizes:
        texts = [
            f"Conversation {i}: User discusses various topics including AI, machine learning, "
            f"programming, technology, and asks questions about implementation details."
            for i in range(size)
        ]

        start = time.time()
        collection.add(
            texts=texts,
            ids=[f"conv_{i}" for i in range(size)]
        )
        elapsed = time.time() - start

        logger.info(f"Indexed {size} conversations: {elapsed:.2f}s ({elapsed/size*1000:.0f}ms per conv)")

        # Search
        start = time.time()
        results = collection.query("AI and machine learning", n_results=5)
        search_time = (time.time() - start) * 1000
        logger.info(f"  Search in {size} docs: {search_time:.1f}ms")

        # Clear for next size
        db.delete_collection("large_test")
        collection = db.get_or_create_collection("large_test")

    # Cleanup
    db.delete_collection("large_test")


def main():
    """Run all performance tests"""
    logger.info("🚀 Vector Database Performance Profiling on Pi-5\n")

    try:
        # Test 1: Single embedding speed
        avg_embed = profile_embedding_speed()

        # Test 2: Batch embedding
        batch_time = profile_batch_embedding()

        # Test 3: Search speed
        avg_search = profile_search_speed()

        # Test 4: Large dataset
        profile_large_dataset()

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("PERFORMANCE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Embedding (single):  {avg_embed:.1f}ms")
        logger.info(f"Embedding (batch):   {(batch_time / 100) * 1000:.1f}ms per doc")
        logger.info(f"Search (avg):        {avg_search:.1f}ms")
        logger.info(f"Model:               all-MiniLM-L6-v2 (90MB)")
        logger.info(f"Dimension:           384")
        logger.info("=" * 60)

        logger.info("\n✅ Performance profiling complete!")

    except Exception as e:
        logger.error(f"❌ Performance profiling failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
