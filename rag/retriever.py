"""
rag/retriever.py
----------------
Similarity-search helpers that query the ChromaDB collection for a given
video and return the most relevant transcript chunks as context.
"""

from langchain_chroma import Chroma
from langchain_core.retrievers import BaseRetriever

from config.settings import CHROMA_DB_PATH, RETRIEVER_TOP_K
from rag.embedder import get_embeddings
from rag.vector_store import ChromaManager


# ── Internal helper ───────────────────────────────────────────────────────────

def _load_vectorstore(video_id: str) -> Chroma:
    """Load the persisted ChromaDB collection for the given video."""
    return Chroma(
        collection_name=ChromaManager.collection_name(video_id),
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DB_PATH,
    )


# ── Public API ────────────────────────────────────────────────────────────────

def get_retriever(video_id: str, k: int = RETRIEVER_TOP_K) -> BaseRetriever:
    """
    Return a LangChain retriever backed by the video's ChromaDB collection.
    Useful when integrating with LangChain LCEL chains.
    """
    return _load_vectorstore(video_id).as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )


def retrieve_context(question: str, video_id: str, k: int = RETRIEVER_TOP_K) -> str:
    """
    Retrieve the top-k most relevant transcript chunks for `question` and
    return them as a single formatted context string.

    Args:
        question : User's natural-language question
        video_id : YouTube video ID whose ChromaDB collection to search
        k        : Number of chunks to retrieve

    Returns:
        Concatenated chunk texts separated by dividers, or "" if nothing found.
    """
    retriever = get_retriever(video_id, k=k)
    docs      = retriever.invoke(question)

    if not docs:
        return ""

    return "\n\n---\n\n".join(
        f"[Chunk {i + 1}]\n{doc.page_content}"
        for i, doc in enumerate(docs)
    )
