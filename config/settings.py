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


# ── API Key Management ────────────────────────────────────────────────────────

def get_gemini_api_key() -> str:
    """
    Dynamically retrieve the active Google Gemini API key.
    Priority:
    1. Streamlit session_state user input (custom_gemini_api_key)
    2. Streamlit secrets (GEMINI_API_KEY or GOOGLE_API_KEY)
    3. Environment variables (GEMINI_API_KEY or GOOGLE_API_KEY)
    """
    api_key = ""
    try:
        if "custom_gemini_api_key" in st.session_state and st.session_state["custom_gemini_api_key"]:
            api_key = st.session_state["custom_gemini_api_key"].strip()
    except Exception:
        pass

    if not api_key:
        try:
            if hasattr(st, "secrets"):
                if "GEMINI_API_KEY" in st.secrets:
                    api_key = str(st.secrets["GEMINI_API_KEY"]).strip()
                elif "GOOGLE_API_KEY" in st.secrets:
                    api_key = str(st.secrets["GOOGLE_API_KEY"]).strip()
        except Exception:
            pass

    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")

    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        os.environ["GOOGLE_API_KEY"] = api_key

    return api_key


def get_groq_api_key() -> str:
    """
    Dynamically retrieve the active Groq API key.
    Priority:
    1. Streamlit session_state user input (custom_groq_api_key)
    2. Streamlit secrets (GROQ_API_KEY)
    3. Environment variables (GROQ_API_KEY)
    """
    api_key = ""
    try:
        if "custom_groq_api_key" in st.session_state and st.session_state["custom_groq_api_key"]:
            api_key = st.session_state["custom_groq_api_key"].strip()
    except Exception:
        pass

    if not api_key:
        try:
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = str(st.secrets["GROQ_API_KEY"]).strip()
        except Exception:
            pass

    if not api_key:
        api_key = os.getenv("GROQ_API_KEY", "")

    if api_key:
        os.environ["GROQ_API_KEY"] = api_key

    return api_key


def has_valid_gemini_key() -> bool:
    """Return True if a non-empty Gemini API key is available."""
    return bool(get_gemini_api_key())


def has_valid_groq_key() -> bool:
    """Return True if a non-empty Groq API key is available."""
    return bool(get_groq_api_key())


# ── LLM Models (Dual-LLM Architecture) ───────────────────────────────────────

def get_groq_model() -> str:
    """Retrieve active Groq model from session_state or default."""
    try:
        if "groq_model_select" in st.session_state and st.session_state["groq_model_select"]:
            return st.session_state["groq_model_select"]
    except Exception:
        pass
    return os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


# Summarizer LLM: Groq (Verified active models)
DEFAULT_GROQ_MODEL: str = "openai/gpt-oss-120b"
FALLBACK_GROQ_MODEL: str = "openai/gpt-oss-20b"
GROQ_TEMPERATURE: float = 0.3

# RAG Q&A LLM: Google Gemini
GEMINI_MODEL: str = "gemini-3.6-flash"
GEMINI_FALLBACK_MODEL: str = "gemini-1.5-flash"
GEMINI_TEMPERATURE: float = 0.2

# ── Embeddings (Local High-Speed Multilingual MiniLM — ~470MB, Zero API Cost) ─
EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DEVICE: str = "cpu"                         # change to "cuda" if GPU available

# ── ChromaDB (Persistent Vector Store) ──────────────────────────────────────
CHROMA_DB_PATH: str = "./chroma_db"                   # relative to project root

# ── Text Chunking ────────────────────────────────────────────────────────────
CHUNK_SIZE: int = 1000
CHUNK_OVERLAP: int = 150

# ── Retriever ────────────────────────────────────────────────────────────────
RETRIEVER_TOP_K: int = 5


def get_max_transcript_chars() -> int:
    """Return max transcript length based on user Token Mode setting in sidebar and model constraints."""
    mode = "balanced"
    try:
        mode = st.session_state.get("token_mode_radio", "balanced")
    except Exception:
        pass

    selected_model = get_groq_model()
    # If using gpt-oss-120b with strict 8k TPM limit on Groq Free Tier, cap context
    if "gpt-oss-120b" in selected_model:
        return 12_000   # ~2.8k tokens, fits easily within Groq 8k TPM limit

    if mode == "saver":
        return 15_000   # ~3.5k tokens
    elif mode == "detailed":
        return 55_000   # ~13k tokens
    return 30_000       # ~7k tokens (default balanced)


# ── Transcript ───────────────────────────────────────────────────────────────
MAX_TRANSCRIPT_CHARS: int = 25_000
