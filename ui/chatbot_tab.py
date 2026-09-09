"""
ui/chatbot_tab.py
-----------------
Streamlit UI layout & chat history state management for Tab 2 (RAG Chatbot).
"""

try:
    from config.settings import has_valid_api_key
except Exception:
    def has_valid_api_key():
        import os
        try:
            if "custom_gemini_api_key" in st.session_state and st.session_state["custom_gemini_api_key"]:
                return True
            if hasattr(st, "secrets") and ("GEMINI_API_KEY" in st.secrets or "GOOGLE_API_KEY" in st.secrets):
                return True
        except Exception:
            pass
        return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))

from core.text_utils import format_rtl
from workflows.rag_workflow import run_rag_pipeline
from rag.vector_store import ChromaManager



def render_chatbot_tab():
    st.markdown("### 💬 Multilingual Video RAG Chatbot")
    st.caption("Ask questions about any YouTube video. Permanent memory via ChromaDB vector index.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    col_url, col_lang = st.columns([3, 1])

    with col_url:
        rag_url = st.text_input(
            "YouTube Video URL for Chat",
            placeholder="https://www.youtube.com/watch?v=...",
            key="rag_url_input"
        )
    with col_lang:
        language = st.selectbox(
            "Answer Language",
            ["English", "Arabic"],
            key="rag_lang_select"
        )

    # Show persistent video index status
    manager = ChromaManager()
    processed_videos = manager.list_processed_videos()
    if processed_videos:
        with st.expander(f"📦 Stored Vector Indexes ({len(processed_videos)} videos in permanent memory)"):
            for v_id in processed_videos:
                st.write(f"- Video ID: `{v_id}` (embedded and ready for instant Q&A)")

    st.divider()

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if msg.get("language") == "Arabic" and msg["role"] == "assistant":
                st.markdown(format_rtl(msg["content"]), unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])

    # User input
    question = st.chat_input("Ask a question about this video...")

    if question:
        if not has_valid_api_key():
            st.error("🔑 **Gemini API Key missing!** Please enter your API key in the sidebar configuration on the left.")
            return

        if not rag_url.strip():
            st.warning("Please provide a YouTube video URL first.")
            return


        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving context from ChromaDB & running Q&A agent..."):
                result = run_rag_pipeline(url=rag_url, question=question, language=language)

            if result.get("error"):
                error_msg = f"❌ {result['error']}"
                st.error(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                return

            answer = result.get("answer", "No response generated.")
            is_cached = result.get("is_cached", False)

            if is_cached:
                st.toast("⚡ Permanent memory hit: loaded context from ChromaDB cache!")

            if language == "Arabic":
                st.markdown(format_rtl(answer), unsafe_allow_html=True)
            else:
                st.markdown(answer)

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer,
                "language": language
            })
