"""
Conversation Indexer - Phase 13.3

Automatically indexes conversations for semantic search:
- Batch indexing of existing conversations
- Incremental indexing on save/update
- Smart update detection (only re-index when changed)
- Progress tracking for long operations

Architecture:
- Uses vector_db from Phase 13.1
- Stores in "conversations" collection
- Tracks indexing status in separate metadata file
- Generates searchable text from messages + metadata
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime

from core.vector_db import create_vector_db, VectorDBError

logger = logging.getLogger(__name__)


class ConversationIndexer:
    """Index conversations for semantic search"""

    def __init__(
        self,
        conversations_file: str = "./sandbox/conversations.json",
        collection: str = "conversations"
    ):
        """
        Initialize conversation indexer.

        Args:
            conversations_file: Path to conversations JSON file
            collection: Vector collection name (default: "conversations")
        """
        self.conversations_file = Path(conversations_file)
        self.collection_name = collection
        self.index_status_file = self.conversations_file.parent / "index_status.json"

        # Lazy-load vector DB (only when needed)
        self._vector_db = None
        self._collection = None

    def _get_vector_db(self):
        """Get or initialize vector database (lazy loading)"""
        if self._vector_db is None:
            self._vector_db = create_vector_db()
            self._collection = self._vector_db.get_or_create_collection(self.collection_name)
        return self._vector_db

    def _get_collection(self):
        """Get vector collection (lazy loading)"""
        if self._collection is None:
            self._get_vector_db()
        return self._collection

    def _load_conversations(self) -> List[Dict]:
        """Load conversations from JSON file"""
        try:
            if not self.conversations_file.exists():
                return []

            with open(self.conversations_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading conversations: {e}")
            return []

    def _load_index_status(self) -> Dict[str, Dict]:
        """
        Load indexing status metadata.

        Returns:
            Dict mapping conversation IDs to status info:
            {
                "conv_123": {
                    "indexed_at": "2025-12-29T12:00:00",
                    "updated_at": "2025-12-29T12:00:00",
                    "message_count": 10
                }
            }
        """
        try:
            if not self.index_status_file.exists():
                return {}

            with open(self.index_status_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading index status: {e}")
            return {}

    def _save_index_status(self, status: Dict[str, Dict]):
        """Save indexing status metadata"""
        try:
            self.index_status_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.index_status_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving index status: {e}")

    def _generate_searchable_text(self, conversation: Dict) -> str:
        """
        Generate searchable text from conversation.

        Combines:
        - All message content (user + assistant)
        - Tags
        - Metadata

        Args:
            conversation: Conversation dict with messages and metadata

        Returns:
            Searchable text representation
        """
        parts = []

        # Extract messages
        messages = conversation.get("messages", [])
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            parts.append(f"{role}: {content}")

        # Extract metadata
        metadata = conversation.get("metadata", {})

        # Add tags
        tags = metadata.get("tags", [])
        if tags:
            parts.append(f"Tags: {', '.join(tags)}")

        # Add model info
        model = metadata.get("model_used", "")
        if model:
            parts.append(f"Model: {model}")

        # Add status flags
        if metadata.get("favorite"):
            parts.append("Marked as favorite")
        if metadata.get("archived"):
            parts.append("Archived")

        # Combine all parts
        searchable_text = "\n".join(parts)
        return searchable_text

    def _needs_reindex(self, conv_id: str, conversation: Dict, index_status: Dict) -> bool:
        """
        Check if conversation needs to be re-indexed.

        Args:
            conv_id: Conversation ID
            conversation: Conversation data
            index_status: Current index status

        Returns:
            True if needs re-indexing, False otherwise
        """
        # Not indexed yet
        if conv_id not in index_status:
            return True

        status = index_status[conv_id]

        # Check if conversation was updated after last index
        conv_updated_at = conversation.get("updated_at", "")
        last_indexed_at = status.get("indexed_at", "")

        if conv_updated_at > last_indexed_at:
            return True

        # Check if message count changed
        current_msg_count = len(conversation.get("messages", []))
        indexed_msg_count = status.get("message_count", 0)

        if current_msg_count != indexed_msg_count:
            return True

        return False

    def index_conversation(self, conv_id: str, conversation: Dict) -> bool:
        """
        Index a single conversation.

        Args:
            conv_id: Conversation ID
            conversation: Conversation data

        Returns:
            True if successfully indexed, False otherwise
        """
        try:
            # Generate searchable text
            searchable_text = self._generate_searchable_text(conversation)

            # Prepare metadata for vector store
            # Note: ChromaDB requires scalar values (not lists) in metadata
            tags = conversation.get("metadata", {}).get("tags", [])
            tags_str = ",".join(tags) if tags else ""  # Convert list to comma-separated string

            vector_metadata = {
                "conv_id": conv_id,
                "created_at": conversation.get("created_at", ""),
                "updated_at": conversation.get("updated_at", ""),
                "message_count": len(conversation.get("messages", [])),
                "tags": tags_str,  # Store as string, not list
                "favorite": conversation.get("metadata", {}).get("favorite", False),
                "archived": conversation.get("metadata", {}).get("archived", False),
                "model_used": conversation.get("metadata", {}).get("model_used", ""),
            }

            # Get collection
            collection = self._get_collection()

            # Add to vector database
            collection.add(
                texts=[searchable_text],
                metadatas=[vector_metadata],
                ids=[conv_id]
            )

            # Update index status
            index_status = self._load_index_status()
            index_status[conv_id] = {
                "indexed_at": datetime.now().isoformat(),
                "updated_at": conversation.get("updated_at", ""),
                "message_count": len(conversation.get("messages", []))
            }
            self._save_index_status(index_status)

            logger.info(f"Indexed conversation: {conv_id}")
            return True

        except Exception as e:
            logger.error(f"Error indexing conversation {conv_id}: {e}")
            return False

    def index_all(
        self,
        force: bool = False,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Index all conversations (batch operation).

        Args:
            force: If True, re-index all conversations even if already indexed
            progress_callback: Optional callback(current, total, conv_id)

        Returns:
            Dict with indexing results:
            {
                "total": 100,
                "indexed": 95,
                "skipped": 5,
                "failed": 0,
                "duration_seconds": 12.5
            }
        """
        start_time = datetime.now()

        # Load conversations and index status
        conversations = self._load_conversations()
        index_status = self._load_index_status()

        total = len(conversations)
        indexed = 0
        skipped = 0
        failed = 0

        logger.info(f"Starting batch indexing of {total} conversations...")

        for i, conv in enumerate(conversations):
            conv_id = conv.get("id", "")

            if not conv_id:
                logger.warning(f"Skipping conversation without ID at index {i}")
                skipped += 1
                continue

            # Progress callback
            if progress_callback:
                progress_callback(i + 1, total, conv_id)

            # Skip if already indexed (unless force=True)
            if not force and not self._needs_reindex(conv_id, conv, index_status):
                logger.debug(f"Skipping already-indexed conversation: {conv_id}")
                skipped += 1
                continue

            # Index conversation
            success = self.index_conversation(conv_id, conv)
            if success:
                indexed += 1
            else:
                failed += 1

        duration = (datetime.now() - start_time).total_seconds()

        result = {
            "total": total,
            "indexed": indexed,
            "skipped": skipped,
            "failed": failed,
            "duration_seconds": duration
        }

        logger.info(
            f"Batch indexing complete: {indexed} indexed, "
            f"{skipped} skipped, {failed} failed in {duration:.2f}s"
        )

        return result

    def remove_from_index(self, conv_id: str) -> bool:
        """
        Remove conversation from index.

        Args:
            conv_id: Conversation ID to remove

        Returns:
            True if successfully removed, False otherwise
        """
        try:
            # Remove from vector database
            collection = self._get_collection()
            collection.delete([conv_id])

            # Update index status
            index_status = self._load_index_status()
            if conv_id in index_status:
                del index_status[conv_id]
                self._save_index_status(index_status)

            logger.info(f"Removed conversation from index: {conv_id}")
            return True

        except Exception as e:
            logger.error(f"Error removing conversation {conv_id} from index: {e}")
            return False

    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get indexing statistics.

        Returns:
            Dict with stats:
            {
                "total_conversations": 100,
                "indexed_conversations": 95,
                "unindexed_conversations": 5,
                "last_index_time": "2025-12-29T12:00:00",
                "collection_size": 95
            }
        """
        try:
            conversations = self._load_conversations()
            index_status = self._load_index_status()

            total_conversations = len(conversations)
            indexed_conversations = len(index_status)
            unindexed_conversations = total_conversations - indexed_conversations

            # Get last index time
            last_index_time = None
            if index_status:
                times = [s.get("indexed_at", "") for s in index_status.values()]
                last_index_time = max(times) if times else None

            # Get collection size
            collection_size = 0
            try:
                collection = self._get_collection()
                collection_size = collection.count()
            except Exception as e:
                logger.warning(f"Could not get collection size: {e}")

            return {
                "total_conversations": total_conversations,
                "indexed_conversations": indexed_conversations,
                "unindexed_conversations": unindexed_conversations,
                "last_index_time": last_index_time,
                "collection_size": collection_size
            }

        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {
                "total_conversations": 0,
                "indexed_conversations": 0,
                "unindexed_conversations": 0,
                "last_index_time": None,
                "collection_size": 0
            }

    def search_conversations(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search conversations semantically.

        Args:
            query: Search query (natural language)
            top_k: Max results to return
            filter_metadata: Optional metadata filter (tags, favorite, etc.)

        Returns:
            List of matching conversations with similarity scores
        """
        try:
            collection = self._get_collection()

            results = collection.query(
                query_text=query,
                n_results=top_k,
                filter=filter_metadata
            )

            # Format results
            matches = []
            for i in range(len(results.get("ids", []))):
                metadata = results["metadatas"][i]

                # Convert tags string back to list for API consistency
                if "tags" in metadata and metadata["tags"]:
                    metadata["tags"] = metadata["tags"].split(",")
                else:
                    metadata["tags"] = []

                match = {
                    "conv_id": results["ids"][i],
                    "text": results["documents"][i],
                    "similarity": 1.0 - results["distances"][i],  # Convert distance to similarity
                    "metadata": metadata
                }
                matches.append(match)

            return matches

        except Exception as e:
            logger.error(f"Error searching conversations: {e}")
            return []


# Convenience function for global use
_global_indexer = None

def get_conversation_indexer() -> ConversationIndexer:
    """Get global conversation indexer instance (lazy-loaded)"""
    global _global_indexer
    if _global_indexer is None:
        _global_indexer = ConversationIndexer()
    return _global_indexer
