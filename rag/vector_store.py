"""
rag/vector_store.py
-------------------
ChromaDB persistent client manager.
One collection per video_id — survives app restarts (permanent memory).
"""

import chromadb
from config.settings import CHROMA_DB_PATH
from core.video_processor import get_video_metadata


# Collection names must start with a letter per ChromaDB rules.
# YouTube IDs can start with digits, so we prefix with "yt_".
def _collection_name(video_id: str) -> str:
    return f"yt_{video_id}"


class ChromaManager:
    """
    Thin wrapper around the ChromaDB persistent client.
    Provides collection lifecycle management keyed strictly by video_id.
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

    def list_processed_videos_with_titles(self) -> list[dict]:
        """
        Return a list of dictionaries with 'video_id', 'title', and 'chunk_count'
        to display user-friendly titles in the Streamlit UI without altering
        ChromaDB keys or storage.
        """
        processed = []
        for vid in self.list_processed_videos():
            try:
                meta = get_video_metadata(vid)
                title = meta.get("title", f"Video {vid}")
            except Exception:
                title = f"Video {vid}"
            
            processed.append({
                "video_id": vid,
                "title": title,
                "display_name": f"🎬 {title} (ID: {vid})"
            })
        return processed

    def get_collection_data(self, video_id: str) -> dict:
        """
        Retrieve all documents, metadatas, and chunk IDs stored in a video's collection.
        """
        name = _collection_name(video_id)
        try:
            col = self._client.get_collection(name)
            data = col.get()
            return {
                "count": col.count(),
                "ids": data.get("ids", []),
                "documents": data.get("documents", []),
                "metadatas": data.get("metadatas", []),
            }
        except Exception:
            return {"count": 0, "ids": [], "documents": [], "metadatas": []}

    def get_db_stats(self) -> dict:
        """
        Return overall ChromaDB statistics across all stored video collections.
        """
        total_collections = 0
        total_chunks = 0
        video_stats = []

        try:
            collections = self._client.list_collections()
            total_collections = len(collections)
            for c in collections:
                count = c.count()
                total_chunks += count
                v_id = c.name[3:] if c.name.startswith("yt_") else c.name
                video_stats.append({"video_id": v_id, "chunk_count": count})
        except Exception:
            pass

        return {
            "total_collections": total_collections,
            "total_chunks": total_chunks,
            "video_stats": video_stats,
            "db_path": CHROMA_DB_PATH,
        }

    @staticmethod
    def collection_name(video_id: str) -> str:
        return _collection_name(video_id)
