"""
Centralized configuration — all settings loaded dynamically.
"""

import os
import sys
from dotenv import load_dotenv
import streamlit as st

# ChromaDB sqlite3 fix for Linux / Streamlit Cloud compatibility
try:
    import sqlite3
    if sqlite3.sqlite_version_info < (3, 35, 0):
        import pysqlite3
        sys.modules["sqlite3"] = pysqlite3
except Exception:
    pass

load_dotenv()


def get_gemini_api_key() -> str:
    """
    Dynamically retrieve the active Gemini API key.
    Priority order:
    1. Streamlit session_state user input (custom_gemini_api_key)
    2. Streamlit secrets (st.secrets["GEMINI_API_KEY"] or st.secrets["GOOGLE_API_KEY"])
    3. Environment variables (GEMINI_API_KEY or GOOGLE_API_KEY)
    """
    api_key = ""

    # 1. User input in Streamlit sidebar
    try:
        if "custom_gemini_api_key" in st.session_state and st.session_state["custom_gemini_api_key"]:
            api_key = st.session_state["custom_gemini_api_key"].strip()
    except Exception:
        pass

    # 2. Streamlit Cloud Secrets
    if not api_key:
        try:
            if "GEMINI_API_KEY" in st.secrets:
                api_key = str(st.secrets["GEMINI_API_KEY"]).strip()
            elif "GOOGLE_API_KEY" in st.secrets:
                api_key = str(st.secrets["GOOGLE_API_KEY"]).strip()
        except Exception:
            pass

    # 3. Environment variables
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")

    # Sync to os.environ for LiteLLM / CrewAI / Google SDKs
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        os.environ["GOOGLE_API_KEY"] = api_key

    return api_key


def has_valid_api_key() -> bool:
    """Return True if a non-empty Gemini API key is available."""
    return bool(get_gemini_api_key())


# ── LLM (Google Gemini) ─────────────────────────────────────────────────────
LLM_MODEL: str = "gemini/gemini-3.6-flash"          # CrewAI / LiteLLM format
LANGCHAIN_LLM_MODEL: str = "gemini-3.6-flash"        # LangChain format
LLM_TEMPERATURE: float = 0.3

# ── Embeddings (Local BGE-M3 — zero API calls) ──────────────────────────────
EMBEDDING_MODEL: str = "BAAI/bge-m3"
EMBEDDING_DEVICE: str = "cpu"                         # change to "cuda" if GPU available

# ── ChromaDB (Persistent Vector Store) ──────────────────────────────────────
CHROMA_DB_PATH: str = "./chroma_db"                   # relative to project root

# ── Text Chunking ────────────────────────────────────────────────────────────
CHUNK_SIZE: int = 1000
CHUNK_OVERLAP: int = 150

# ── Retriever ────────────────────────────────────────────────────────────────
RETRIEVER_TOP_K: int = 5

def get_max_transcript_chars() -> int:
    """Return max transcript length based on user Token Mode setting in sidebar."""
    try:
        mode = st.session_state.get("token_mode_radio", "balanced")
        if mode == "saver":
            return 15_000   # ~3.5k tokens
        elif mode == "detailed":
            return 45_000   # ~11k tokens
    except Exception:
        pass
    return 25_000           # ~6k tokens (default balanced)


# ── Transcript ───────────────────────────────────────────────────────────────
MAX_TRANSCRIPT_CHARS: int = 25_000   # ~6k tokens; optimized default


