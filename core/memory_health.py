"""
Memory Health Utilities (Phase 3)

Provides functions for memory maintenance, cleanup, and health monitoring.
Works with enhanced vector metadata to identify stale, low-quality, or duplicate memories.

Part of Azoth's adaptive memory architecture to counter long-context KV degradation.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


def get_stale_memories(
    days_unused: int = 30,
    collection: str = "knowledge",
    min_confidence: Optional[float] = None,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Find memories not accessed in X days.

    IMPLEMENTATION NOTE: ChromaDB filters only work on numbers with $lt/$gt.
    We use last_accessed_ts (Unix timestamp) for filtering.

    Args:
        days_unused: Threshold in days (default: 30)
        collection: Which collection to scan (default: "knowledge")
        min_confidence: Only return items BELOW this confidence (for cleanup targets)
        limit: Maximum results to return

    Returns:
        Dict with success, stale_memories list, and stats
    """
    try:
        from tools.vector_search import _get_vector_db

        db = _get_vector_db()
        if db is None:
            return {"success": False, "error": "Vector database not available"}

        coll = db.get_or_create_collection(collection)

        # Calculate cutoff timestamp
        cutoff_date = datetime.now() - timedelta(days=days_unused)
        cutoff_ts = cutoff_date.timestamp()

        # Get all documents (ChromaDB doesn't support complex filtering in query)
        all_docs = coll.get(limit=None)  # Get all

        if not all_docs["ids"]:
            return {
                "success": True,
                "stale_memories": [],
                "total_checked": 0,
                "cutoff_date": cutoff_date.isoformat()
            }

        # Filter in Python
        stale_memories = []

        for i, (doc_id, doc_text, metadata) in enumerate(
            zip(all_docs["ids"], all_docs["documents"], all_docs["metadatas"])
        ):
            last_accessed = metadata.get("last_accessed_ts", 0)
            confidence = metadata.get("confidence", 1.0)
            access_count = metadata.get("access_count", 0)

            # Check if stale
            is_stale = last_accessed < cutoff_ts

            # Check confidence filter if specified
            if min_confidence is not None and confidence >= min_confidence:
                continue  # Skip high-confidence items

            if is_stale:
                last_accessed_dt = datetime.fromtimestamp(last_accessed) if last_accessed else None

                stale_memories.append({
                    "id": doc_id,
                    "text": doc_text[:200] + "..." if len(doc_text) > 200 else doc_text,
                    "full_text": doc_text,
                    "last_accessed": last_accessed_dt.isoformat() if last_accessed_dt else "never",
                    "days_since_access": (datetime.now() - last_accessed_dt).days if last_accessed_dt else 999,
                    "access_count": access_count,
                    "confidence": confidence,
                    "category": metadata.get("category", "unknown"),
                    "source": metadata.get("source", "unknown")
                })

            # Apply limit
            if limit and len(stale_memories) >= limit:
                break

        # Sort by days since access (oldest first)
        stale_memories.sort(key=lambda x: x["days_since_access"], reverse=True)

        logger.info(f"Found {len(stale_memories)} stale memories (unused for {days_unused}+ days)")

        return {
            "success": True,
            "stale_memories": stale_memories,
            "total_checked": len(all_docs["ids"]),
            "stale_count": len(stale_memories),
            "cutoff_date": cutoff_date.isoformat(),
            "days_threshold": days_unused
        }

    except Exception as e:
        logger.error(f"Error in get_stale_memories: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_low_access_memories(
    max_access_count: int = 2,
    min_age_days: int = 7,
    collection: str = "knowledge",
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Find memories with very low access counts (rarely used).

    Args:
        max_access_count: Maximum access count to flag (default: 2)
        min_age_days: Only flag memories older than this (default: 7 days)
        collection: Which collection to scan
        limit: Maximum results

    Returns:
        Dict with low-access memories
    """
    try:
        from tools.vector_search import _get_vector_db

        db = _get_vector_db()
        if db is None:
            return {"success": False, "error": "Vector database not available"}

        coll = db.get_or_create_collection(collection)

        # Get all documents
        all_docs = coll.get(limit=None)

        if not all_docs["ids"]:
            return {
                "success": True,
                "low_access_memories": [],
                "total_checked": 0
            }

        # Calculate age cutoff
        age_cutoff = datetime.now() - timedelta(days=min_age_days)
        age_cutoff_ts = age_cutoff.timestamp()

        # Filter
        low_access_memories = []

        for doc_id, doc_text, metadata in zip(
            all_docs["ids"], all_docs["documents"], all_docs["metadatas"]
        ):
            access_count = metadata.get("access_count", 0)
            added_at = metadata.get("added_at", None)

            # Parse added_at
            if added_at:
                try:
                    added_dt = datetime.fromisoformat(added_at)
                    added_ts = added_dt.timestamp()
                except:
                    added_ts = 0
            else:
                added_ts = 0

            # Check conditions
            is_old_enough = added_ts < age_cutoff_ts
            is_low_access = access_count <= max_access_count

            if is_old_enough and is_low_access:
                age_days = (datetime.now() - datetime.fromtimestamp(added_ts)).days if added_ts else 999

                low_access_memories.append({
                    "id": doc_id,
                    "text": doc_text[:200] + "..." if len(doc_text) > 200 else doc_text,
                    "access_count": access_count,
                    "age_days": age_days,
                    "confidence": metadata.get("confidence", 1.0),
                    "category": metadata.get("category", "unknown")
                })

            if limit and len(low_access_memories) >= limit:
                break

        # Sort by access count (lowest first)
        low_access_memories.sort(key=lambda x: (x["access_count"], -x["age_days"]))

        logger.info(f"Found {len(low_access_memories)} low-access memories")

        return {
            "success": True,
            "low_access_memories": low_access_memories,
            "total_checked": len(all_docs["ids"]),
            "flagged_count": len(low_access_memories)
        }

    except Exception as e:
        logger.error(f"Error in get_low_access_memories: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_duplicate_candidates(
    collection: str = "knowledge",
    similarity_threshold: float = 0.95,
    limit: int = 100,
    sample_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Find potential duplicate memories using search-based similarity.

    IMPLEMENTATION NOTE: We use ChromaDB's own search rather than O(n²) comparisons.
    For each document, we search for similar documents. If similarity > threshold
    and it's a different document, it's a duplicate candidate.

    Args:
        collection: Collection to scan (default: "knowledge")
        similarity_threshold: Similarity cutoff (default: 0.95, range 0.0-1.0)
        limit: Maximum duplicate pairs to return
        sample_size: If set, only check this many recent documents (for performance)

    Returns:
        Dict with duplicate pairs and stats
    """
    try:
        from tools.vector_search import _get_vector_db

        db = _get_vector_db()
        if db is None:
            return {"success": False, "error": "Vector database not available"}

        coll = db.get_or_create_collection(collection)

        # Get documents to check
        all_docs = coll.get(limit=sample_size)

        if not all_docs["ids"]:
            return {
                "success": True,
                "duplicate_pairs": [],
                "total_checked": 0
            }

        # Find duplicates using search
        seen_pairs = set()
        duplicate_pairs = []

        for doc_id, doc_text in zip(all_docs["ids"], all_docs["documents"]):
            # Search for similar documents
            results = coll.query(
                query_text=doc_text,
                n_results=5,  # Top 5 similar
                include_distances=True
            )

            # Check results
            for result_id, result_doc, distance in zip(
                results["ids"], results["documents"], results["distances"]
            ):
                # Skip self-match
                if result_id == doc_id:
                    continue

                # Calculate similarity (1.0 - distance)
                similarity = 1.0 - distance

                # Check threshold
                if similarity >= similarity_threshold:
                    # Create canonical pair ID (sorted to avoid duplicates)
                    pair_id = tuple(sorted([doc_id, result_id]))

                    if pair_id not in seen_pairs:
                        seen_pairs.add(pair_id)

                        duplicate_pairs.append({
                            "id1": doc_id,
                            "id2": result_id,
                            "similarity": round(similarity, 4),
                            "text1": doc_text[:150] + "..." if len(doc_text) > 150 else doc_text,
                            "text2": result_doc[:150] + "..." if len(result_doc) > 150 else result_doc
                        })

                        # Apply limit
                        if len(duplicate_pairs) >= limit:
                            break

            if len(duplicate_pairs) >= limit:
                break

        # Sort by similarity (highest first)
        duplicate_pairs.sort(key=lambda x: x["similarity"], reverse=True)

        logger.info(f"Found {len(duplicate_pairs)} duplicate candidates in {collection}")

        return {
            "success": True,
            "duplicate_pairs": duplicate_pairs,
            "total_checked": len(all_docs["ids"]),
            "duplicates_found": len(duplicate_pairs),
            "threshold": similarity_threshold
        }

    except Exception as e:
        logger.error(f"Error in get_duplicate_candidates: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def consolidate_memories(
    id1: str,
    id2: str,
    collection: str = "knowledge",
    keep: str = "higher_confidence"
) -> Dict[str, Any]:
    """
    Merge two similar memories into one, preserving higher quality.

    Strategy options:
    - "higher_confidence": Keep the one with higher confidence
    - "higher_access": Keep the one with more access_count
    - "id1" or "id2": Explicitly keep one

    The kept memory gets:
    - Combined access_count from both
    - Related_memories list updated with both IDs
    - Most recent last_accessed_ts
    - Higher confidence (or averaged)

    Args:
        id1: First memory ID
        id2: Second memory ID
        collection: Collection name
        keep: Strategy for which to keep

    Returns:
        Dict with consolidation result
    """
    try:
        from tools.vector_search import _get_vector_db

        db = _get_vector_db()
        if db is None:
            return {"success": False, "error": "Vector database not available"}

        coll = db.get_or_create_collection(collection)

        # Get both documents
        docs = coll.get(ids=[id1, id2])

        if len(docs["ids"]) != 2:
            return {
                "success": False,
                "error": f"Could not find both memories: {id1}, {id2}"
            }

        # Extract metadata
        meta1 = docs["metadatas"][0]
        meta2 = docs["metadatas"][1]

        # Determine which to keep
        if keep == "higher_confidence":
            keep_idx = 0 if meta1.get("confidence", 0) >= meta2.get("confidence", 0) else 1
        elif keep == "higher_access":
            keep_idx = 0 if meta1.get("access_count", 0) >= meta2.get("access_count", 0) else 1
        elif keep == "id1":
            keep_idx = 0
        elif keep == "id2":
            keep_idx = 1
        else:
            return {"success": False, "error": f"Invalid keep strategy: {keep}"}

        discard_idx = 1 - keep_idx

        keep_id = docs["ids"][keep_idx]
        discard_id = docs["ids"][discard_idx]
        keep_meta = docs["metadatas"][keep_idx]
        discard_meta = docs["metadatas"][discard_idx]

        # Merge metadata
        merged_meta = keep_meta.copy()

        # Combine access counts
        merged_meta["access_count"] = (
            keep_meta.get("access_count", 0) + discard_meta.get("access_count", 0)
        )

        # Keep most recent access time
        merged_meta["last_accessed_ts"] = max(
            keep_meta.get("last_accessed_ts", 0),
            discard_meta.get("last_accessed_ts", 0)
        )

        # Merge related_memories (stored as JSON string)
        related_keep = json.loads(keep_meta.get("related_memories", "[]"))
        related_discard = json.loads(discard_meta.get("related_memories", "[]"))
        related = set(related_keep)
        related.update(related_discard)
        related.add(discard_id)  # Add the discarded ID
        merged_meta["related_memories"] = json.dumps(list(related))

        # Average confidence (or keep higher - configurable)
        merged_meta["confidence"] = max(
            keep_meta.get("confidence", 1.0),
            discard_meta.get("confidence", 1.0)
        )

        # Mark as consolidated
        merged_meta["consolidated_at"] = datetime.now().isoformat()
        merged_meta["consolidated_from"] = discard_id

        # Update kept memory
        coll.update(ids=[keep_id], metadatas=[merged_meta])

        # Delete discarded memory
        coll.delete([discard_id])

        logger.info(f"Consolidated {id1} and {id2} -> kept {keep_id}")

        return {
            "success": True,
            "kept_id": keep_id,
            "discarded_id": discard_id,
            "new_access_count": merged_meta["access_count"],
            "new_confidence": merged_meta["confidence"],
            "related_memories": json.loads(merged_meta["related_memories"])
        }

    except Exception as e:
        logger.error(f"Error in consolidate_memories: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def detect_village_convergence(
    similarity_threshold: float = 0.85,
    limit: int = 20,
    min_text_length: int = 50
) -> Dict[str, Any]:
    """
    Detect cross-agent convergence in the village.

    Finds cases where different agents expressed semantically similar ideas,
    indicating potential consensus or emergent patterns.

    Convergence Types:
    - HARMONY: 2 agents converging on similar ideas
    - CONSENSUS: 3+ agents expressing the same concept

    Args:
        similarity_threshold: Minimum similarity to flag (default: 0.85 = 85%)
        limit: Maximum convergence events to return
        min_text_length: Minimum message length to consider (filters noise)

    Returns:
        Dict with convergence_events list, agent_pairs stats, and insights
    """
    try:
        from tools.vector_search import _get_vector_db

        db = _get_vector_db()
        if db is None:
            return {"success": False, "error": "Vector database not available"}

        # Get village collection
        coll = db.get_or_create_collection("knowledge_village")

        all_docs = coll.get(limit=None)

        if not all_docs["ids"] or len(all_docs["ids"]) < 2:
            return {
                "success": True,
                "convergence_events": [],
                "total_messages": len(all_docs["ids"]) if all_docs["ids"] else 0,
                "message": "Not enough village messages for convergence detection"
            }

        # Track convergence events and agent pairs
        convergence_events = []
        seen_pairs = set()
        agent_pair_counts = defaultdict(int)
        agent_convergence_topics = defaultdict(list)

        # For each message, find similar messages from OTHER agents
        for i, (doc_id, doc_text, metadata) in enumerate(
            zip(all_docs["ids"], all_docs["documents"], all_docs["metadatas"])
        ):
            # Skip short messages (likely noise)
            if len(doc_text) < min_text_length:
                continue

            agent1 = metadata.get("agent_id", "unknown")

            # Search for similar messages
            results = coll.query(
                query_text=doc_text,
                n_results=10,  # Check top 10 similar
                include_distances=True
            )

            if not results["ids"]:
                continue

            # Check each similar result (results are flat lists)
            for match_id, match_dist, match_meta, match_doc in zip(
                results["ids"],
                results["distances"],
                results["metadatas"],
                results["documents"]
            ):
                # Skip self
                if match_id == doc_id:
                    continue

                # Convert distance to similarity (1.0 - distance for normalized vectors)
                similarity = max(0, 1.0 - match_dist)

                if similarity < similarity_threshold:
                    continue

                agent2 = match_meta.get("agent_id", "unknown")

                # Skip same agent (that's echo, not convergence)
                if agent1 == agent2:
                    continue

                # Create canonical pair key to avoid duplicates
                pair_key = tuple(sorted([doc_id, match_id]))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                # Record convergence event
                event = {
                    "agents": sorted([agent1, agent2]),
                    "similarity": round(similarity * 100, 1),  # As percentage
                    "message1": {
                        "id": doc_id,
                        "agent": agent1,
                        "text": doc_text[:150] + "..." if len(doc_text) > 150 else doc_text,
                        "thread": metadata.get("conversation_thread", "")[:20] if metadata.get("conversation_thread") else ""
                    },
                    "message2": {
                        "id": match_id,
                        "agent": agent2,
                        "text": match_doc[:150] + "..." if len(match_doc) > 150 else match_doc,
                        "thread": match_meta.get("conversation_thread", "")[:20] if match_meta.get("conversation_thread") else ""
                    },
                    "type": "HARMONY"  # Will upgrade to CONSENSUS if 3+ agents
                }

                convergence_events.append(event)

                # Track agent pair frequency
                agent_pair = tuple(sorted([agent1, agent2]))
                agent_pair_counts[agent_pair] += 1

                # Track convergence topics per agent
                topic_snippet = doc_text[:50]
                agent_convergence_topics[agent1].append(topic_snippet)
                agent_convergence_topics[agent2].append(topic_snippet)

                if len(convergence_events) >= limit:
                    break

            if len(convergence_events) >= limit:
                break

        # Sort by similarity (highest first)
        convergence_events.sort(key=lambda x: x["similarity"], reverse=True)

        # Detect CONSENSUS (same topic across 3+ agents)
        # Group by similar text patterns
        topic_agents = defaultdict(set)
        for event in convergence_events:
            # Use first 30 chars as rough topic key
            topic_key = event["message1"]["text"][:30].lower()
            topic_agents[topic_key].update(event["agents"])

        consensus_topics = [
            {"topic": topic[:50], "agents": list(agents), "agent_count": len(agents)}
            for topic, agents in topic_agents.items()
            if len(agents) >= 3
        ]

        # Mark consensus events
        for event in convergence_events:
            topic_key = event["message1"]["text"][:30].lower()
            if len(topic_agents.get(topic_key, set())) >= 3:
                event["type"] = "CONSENSUS"

        # Generate insights
        insights = []

        if convergence_events:
            top_pair = max(agent_pair_counts.items(), key=lambda x: x[1]) if agent_pair_counts else None
            if top_pair:
                insights.append(f"🤝 Strongest connection: {top_pair[0][0].upper()} ↔ {top_pair[0][1].upper()} ({top_pair[1]} convergences)")

            avg_similarity = sum(e["similarity"] for e in convergence_events) / len(convergence_events)
            insights.append(f"📊 Average convergence strength: {avg_similarity:.1f}%")

            if consensus_topics:
                insights.append(f"🎯 {len(consensus_topics)} consensus topic(s) detected (3+ agents agree)")

        logger.info(f"Detected {len(convergence_events)} convergence events in village")

        return {
            "success": True,
            "convergence_events": convergence_events[:limit],
            "total_messages": len(all_docs["ids"]),
            "events_found": len(convergence_events),
            "agent_pair_counts": {f"{p[0]}↔{p[1]}": c for p, c in agent_pair_counts.items()},
            "consensus_topics": consensus_topics,
            "insights": insights
        }

    except Exception as e:
        logger.error(f"Error in detect_village_convergence: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Export all functions
__all__ = [
    'get_stale_memories',
    'get_low_access_memories',
    'get_duplicate_candidates',
    'consolidate_memories',
    'detect_village_convergence'
]
