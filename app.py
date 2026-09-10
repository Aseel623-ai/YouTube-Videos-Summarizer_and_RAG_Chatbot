"""
app.py
------
Main Streamlit Entrypoint for YouTube Video Summarizer & RAG Chatbot.
Unified single-page workspace powered by LangGraph, Groq (openai/gpt-oss-120b), Google Gemini, and ChromaDB.
"""

import sys
from pathlib import Path
import streamlit as st

# Ensure project root directory is always at the head of sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ui.sidebar import render_sidebar
from ui.unified_view import render_unified_view


st.set_page_config(
    page_title="YouTube AI Suite — Summarizer & RAG Chatbot",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render sidebar configuration & guide
render_sidebar()

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF0000, #FF4B4B, #FF8E53);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .main-subtext {
        font-size: 1rem;
        color: #718096;
        margin-bottom: 1.2rem;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎬 YouTube AI Suite</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="main-subtext">Multilingual Video Summarization & RAG Q&A — Powered by <b>LangGraph</b>, <b>Groq (openai/gpt-oss-120b)</b>, <b>Google Gemini</b>, and <b>ChromaDB</b>.</div>',
    unsafe_allow_html=True
)

# Render Unified Workspace
render_unified_view()
