"""
app.py
------
Main Streamlit Entrypoint for YouTube Video Summarizer & RAG Chatbot.
"""

import streamlit as st
from ui.sidebar import render_sidebar
from ui.summarizer_tab import render_summarizer_tab
from ui.chatbot_tab import render_chatbot_tab
from ui.admin_tab import render_admin_tab

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
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF0000, #FF4B4B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        font-size: 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎬 YouTube AI Suite</div>', unsafe_allow_html=True)
st.caption("Multilingual Summarization & RAG Chatbot powered by CrewAI, LangChain, LangGraph, ChromaDB, and Gemini.")

tab1, tab2, tab3 = st.tabs(["📝 Summarizer", "💬 RAG Chatbot", "👑 Admin Dashboard"])

with tab1:
    render_summarizer_tab()

with tab2:
    render_chatbot_tab()

with tab3:
    render_admin_tab()

