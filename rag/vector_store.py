"""
rag/vector_store.py
-------------------
ChromaDB persistent client manager.
One collection per video_id — survives app restarts (permanent memory).
"""

import chromadb
from config.settings import CHROMA_DB_PATH


# Collection names must start with a letter per ChromaDB rules.
# YouTube IDs can start with digits, so we prefix with "yt_".
def _collection_name(video_id: str) -> str:
    return f"yt_{video_id}"


class ChromaManager:
    """
    Thin wrapper around the ChromaDB persistent client.
    Provides collection lifecycle management keyed by video_id.
    """

    def __init__(self):
        self._client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # ── Public API ────────────────────────────────────────────────────────────

    def collection_exists(self, video_id: str) -> bool:
        """
        Return True if a non-empty collection already exists for this video.
        Used to skip re-embedding on subsequent queries (permanent memory).
        """
        name = _collection_name(video_id)
        try:
            existing = [c.name for c in self._client.list_collections()]
            if name not in existing:
                return False
            col = self._client.get_collection(name)
            return col.count() > 0
        except Exception:
            return False

    def get_or_create_collection(self, video_id: str):
        """Get or create a ChromaDB collection for the given video_id."""
        return self._client.get_or_create_collection(_collection_name(video_id))

    def delete_collection(self, video_id: str) -> None:
        """Delete the ChromaDB collection for the given video_id (cleanup)."""
        try:
            self._client.delete_collection(_collection_name(video_id))
        except Exception:
            pass

    def list_processed_videos(self) -> list[str]:
        """
        Return a list of video_ids that have been embedded and stored.
        Strips the 'yt_' prefix to return raw video IDs.
        """
        try:
            return [
                c.name[3:]          # strip "yt_"
                for c in self._client.list_collections()
                if c.name.startswith("yt_")
            ]
        except Exception:
            return []

    @staticmethod
    def collection_name(video_id: str) -> str:
        return _collection_name(video_id)
