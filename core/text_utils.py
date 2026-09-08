"""
core/text_utils.py
------------------
Text processing utilities: chunking transcripts into LangChain Documents,
RTL formatting for Arabic, and transcript truncation.
"""

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP, MAX_TRANSCRIPT_CHARS, get_max_transcript_chars


# ── Chunking ──────────────────────────────────────────────────────────────────

def chunk_transcript(text: str, video_id: str) -> list[Document]:
    """
    Split a transcript into overlapping chunks suitable for embedding.

    Args:
        text     : Full transcript string
        video_id : YouTube video ID used as metadata

    Returns:
        List of LangChain Document objects, each with metadata.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
    )
    raw_chunks = splitter.split_text(text)
    return [
        Document(
            page_content=chunk,
            metadata={
                "video_id":    video_id,
                "chunk_index": i,
                "source":      f"youtube_{video_id}",
            },
        )
        for i, chunk in enumerate(raw_chunks)
    ]


# ── Transcript Truncation ─────────────────────────────────────────────────────

def truncate_transcript(text: str, max_chars: int | None = None) -> str:
    """
    Truncate transcript to avoid overflowing LLM context windows and save tokens.
    Appends a note so the LLM knows it's working with partial content.
    """
    limit = max_chars if max_chars is not None else get_max_transcript_chars()
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n[Transcript truncated for token efficiency — core content preserved.]"



# ── RTL Formatting ────────────────────────────────────────────────────────────

def format_rtl(content: str) -> str:
    """
    Wrap Arabic text in a styled RTL div for correct Streamlit rendering.
    Uses Google Fonts Tajawal for beautiful Arabic typography.
    """
    return f"""
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
<div style="
    direction: rtl;
    text-align: right;
    font-family: 'Tajawal', 'Cairo', 'Arial', sans-serif;
    line-height: 2;
    font-size: 1rem;
    padding: 0.5rem 0;
">
{content}
</div>
"""
