"""
rag/embedder.py
---------------
Embed transcript chunks with the lightweight multilingual model
(sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2, ~470MB) and persist them in
ChromaDB.  The embedding model is loaded once (singleton) and cached for
the lifetime of the process — no repeated downloads after first run.

Key property:
  If a collection for `video_id` already exists in ChromaDB, the function
  skips embedding entirely and returns the existing store.  This is the
  "permanent memory" behaviour — each video is processed only once.
"""

from functools import lru_cache

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from config.settings import (
    CHROMA_DB_PATH,
    EMBEDDING_MODEL,
    EMBEDDING_DEVICE,
)
from rag.vector_store import ChromaManager


# ── Embeddings singleton ──────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_embeddings() -> HuggingFaceEmbeddings:
    """
    Load the lightweight multilingual embedding model once and cache it.
    Downloads ~470 MB (one-time only) and provides 5x faster CPU inference.
    """
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": EMBEDDING_DEVICE},
        encode_kwargs={"normalize_embeddings": True},   # cosine-similarity friendly
    )


# ── Public API ────────────────────────────────────────────────────────────────

def get_embeddings() -> HuggingFaceEmbeddings:
    """Expose the singleton embeddings to other modules."""
    return _get_embeddings()


def embed_and_store(chunks: list[Document], video_id: str) -> Chroma:
    """
    Embed `chunks` and persist them in ChromaDB under a collection named
    after `video_id`.

    If the collection already exists (permanent memory cache), skips
    embedding and returns the existing Chroma vectorstore.

    Args:
        chunks   : LangChain Document objects (from core.text_utils.chunk_transcript)
        video_id : YouTube video ID (used as collection key)

    Returns:
        A LangChain Chroma vectorstore instance ready for similarity search.
    """
    manager    = ChromaManager()
    embeddings = get_embeddings()
    col_name   = ChromaManager.collection_name(video_id)

    if manager.collection_exists(video_id):
        # ── Cache hit: load existing collection, no re-embedding ──────────────
        return Chroma(
            collection_name=col_name,
            embedding_function=embeddings,
            persist_directory=CHROMA_DB_PATH,
        )

    # ── Cache miss: embed all chunks and persist ──────────────────────────────
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=col_name,
        persist_directory=CHROMA_DB_PATH,
    )
