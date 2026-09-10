"""
ui/sidebar.py
--------------
Streamlit Sidebar rendering: Groq & Gemini API key configuration, model selector & user instructions.
"""

import streamlit as st
import os


def render_sidebar():
    """Render the sidebar configuration and API key guide."""
    with st.sidebar:
        st.markdown("## ⚙️ Configuration / الإعدادات")
        st.caption("Provide API keys for Groq (Summarizer) & Google Gemini (Q&A Chatbot).")

        # 1. Groq API Key
        custom_groq_key = st.text_input(
            "⚡ Groq API Key (Summarizer)",
            type="password",
            placeholder="gsk_...",
            help="Required for video summarization with Groq models.",
            key="custom_groq_api_key"
        )
        active_groq_key = custom_groq_key.strip() or os.getenv("GROQ_API_KEY", "")
        if not active_groq_key:
            try:
                if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                    active_groq_key = str(st.secrets["GROQ_API_KEY"])
            except Exception:
                pass

        if custom_groq_key.strip():
            st.success("🟢 Groq: Using Custom Key")
        elif active_groq_key:
            st.info("🔵 Groq: Using System Key")
        else:
            st.warning("⚠️ Groq Key Missing (Summarizer requires Groq)")

        # Groq Model Selector
        st.selectbox(
            "⚡ Groq Summarizer Model:",
            options=[
                "openai/gpt-oss-120b",
                "openai/gpt-oss-20b",
                "qwen/qwen3.8-27b",
                "allam-2-7b"
            ],
            index=0,
            format_func=lambda x: {
                "openai/gpt-oss-120b": "🧠 GPT-OSS 120B (Default)",
                "openai/gpt-oss-20b": "⚡ GPT-OSS 20B (Fast)",
                "qwen/qwen3.8-27b": "🌟 Qwen 3.8 27B (High Quality)",
                "allam-2-7b": "🇸🇦 Allam 2 7B (Arabic Specialist)"
            }.get(x, x),
            key="groq_model_select",
            help="Select the Groq model for video summarization."
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # 2. Gemini API Key
        custom_gemini_key = st.text_input(
            "🔑 Gemini API Key (RAG Chatbot)",
            type="password",
            placeholder="AIzaSy...",
            help="Required for context-grounded Q&A with Gemini 2.5 Flash.",
            key="custom_gemini_api_key"
        )
        active_gemini_key = custom_gemini_key.strip() or os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
        if not active_gemini_key:
            try:
                if hasattr(st, "secrets"):
                    if "GEMINI_API_KEY" in st.secrets:
                        active_gemini_key = str(st.secrets["GEMINI_API_KEY"])
                    elif "GOOGLE_API_KEY" in st.secrets:
                        active_gemini_key = str(st.secrets["GOOGLE_API_KEY"])
            except Exception:
                pass

        if custom_gemini_key.strip():
            st.success("🟢 Gemini: Using Custom Key")
        elif active_gemini_key:
            st.info("🔵 Gemini: Using System Key")
        else:
            st.warning("⚠️ Gemini Key Missing (Q&A requires Gemini)")

        st.divider()

        # Token Saver Control
        st.markdown("### ⚡ Context Processing Mode")
        st.radio(
            "Transcript Context Length:",
            options=["saver", "balanced", "detailed"],
            index=1,
            format_func=lambda x: {
                "saver": "⚡ Token Saver (~3.5k tokens)",
                "balanced": "⚖️ Balanced (~7k tokens - Recommended)",
                "detailed": "📜 Detailed (~13k tokens)"
            }[x],
            key="token_mode_radio",
            help="Controls max transcript context length per LLM request."
        )

        st.divider()

        # How to get API Keys expander
        with st.expander("❓ How to get FREE API Keys? / كيف تحصل على المفاتيح مجاناً؟", expanded=False):
            st.markdown("""
            ### ⚡ 1. Groq API Key (Free & Ultra-Fast):
            - **[Groq Console](https://console.groq.com/keys)**
            - Sign up / log in with Google or GitHub -> click **"Create API Key"** -> Copy and paste above.
            
            ---

            ### 🔑 2. Google Gemini API Key (Free):
            - **[Google AI Studio](https://aistudio.google.com/app/apikey)**
            - Sign in with Google Account -> click **"Create API Key"** -> Copy and paste above.

            ---

            🔒 **Privacy Note / ملاحظة خصوصية:**
            - API keys remain in your browser session memory.
            - Keys are **never** logged or saved to disk.
            """)

        st.divider()
        st.caption("🚀 **YouTube AI Suite** | Groq + Gemini + LangGraph + ChromaDB")
