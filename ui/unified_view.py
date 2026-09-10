"""
ui/unified_view.py
------------------
Unified single-page view for YouTube Video Summarization & Context-Grounded RAG Q&A.
"""

import streamlit as st
from config.settings import has_valid_groq_key, has_valid_gemini_key
from core.text_utils import format_rtl
from core.video_processor import extract_video_id
from workflows.summarize_workflow import run_summarize_pipeline
from workflows.rag_workflow import run_rag_pipeline
from rag.vector_store import ChromaManager


def render_unified_view():
    st.caption("Enter a YouTube link to extract the transcript, index for instant Q&A, and generate an AI summary.")

    # Initialize Session State
    if "current_video_url" not in st.session_state:
        st.session_state.current_video_url = ""
    if "current_metadata" not in st.session_state:
        st.session_state.current_metadata = None
    if "current_summary" not in st.session_state:
        st.session_state.current_summary = None
    if "current_language" not in st.session_state:
        st.session_state.current_language = "English"
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    manager = ChromaManager()
    processed_videos = manager.list_processed_videos_with_titles()

    # Stored Videos Quick Selector (Showing Video Title)
    if processed_videos:
        with st.expander(f"📦 Stored Videos in Permanent Memory ({len(processed_videos)} videos ready for Q&A)"):
            options_map = {f"https://www.youtube.com/watch?v={item['video_id']}": item["display_name"] for item in processed_videos}
            selected_url = st.selectbox(
                "Select a previously indexed video to load:",
                options=[""] + list(options_map.keys()),
                format_func=lambda x: "— Select a stored video —" if not x else options_map.get(x, x),
                key="stored_video_selector"
            )
            if selected_url and selected_url != st.session_state.current_video_url:
                st.session_state.current_video_url = selected_url
                st.session_state.chat_history = []
                st.rerun()

    # Input Form
    col_url, col_lang = st.columns([3, 1])

    with col_url:
        url_input = st.text_input(
            "YouTube Video URL",
            value=st.session_state.current_video_url,
            placeholder="https://www.youtube.com/watch?v=...",
            key="main_url_input"
        )
    with col_lang:
        language = st.selectbox(
            "Language / اللغة",
            ["English", "Arabic"],
            index=0 if st.session_state.current_language == "English" else 1,
            key="main_lang_select"
        )

    mode = st.radio(
        "Summary Mode:",
        ["general", "educational"],
        horizontal=True,
        format_func=lambda x: "📌 General Summary" if x == "general" else "🎓 Educational Analysis (Bloom's Taxonomy)",
        key="main_mode_radio"
    )

    with st.expander("🛠️ Advanced: Paste Manual Transcript (Optional / إدخال النص يدوياً)"):
        manual_transcript_input = st.text_area(
            "Paste Transcript Text",
            placeholder="If YouTube restricts auto-captions for this video, paste transcript text here...",
            height=100,
            key="main_manual_transcript"
        )

    btn_col1, btn_col2 = st.columns([2, 1])
    with btn_col1:
        process_clicked = st.button("🚀 Summarize & Start Q&A", type="primary", use_container_width=True)
    with btn_col2:
        if st.session_state.current_metadata and st.button("🔄 Reset Workspace", use_container_width=True):
            st.session_state.current_video_url = ""
            st.session_state.current_metadata = None
            st.session_state.current_summary = None
            st.session_state.chat_history = []
            st.rerun()

    # Trigger Processing
    if process_clicked:
        if not url_input.strip() or not st.session_state.current_video_url.strip():
            st.warning("Please enter a valid YouTube video URL first.")
            return

        if not has_valid_groq_key():
            st.error("⚡ **Groq API Key missing!** Please enter your Groq API key in the sidebar configuration on the left for summarization.")
            return

        with st.spinner("Analyzing video, indexing context to ChromaDB & generating summary with Groq (openai/gpt-oss-120b)..."):
            result = run_summarize_pipeline(
                url=url_input.strip(),
                language=language,
                mode=mode,
                manual_transcript=manual_transcript_input.strip()
            )

        if result.get("error"):
            st.error(f"❌ Error: {result['error']}")
            return

        # Store in session state
        st.session_state.current_video_url = url_input.strip()
        st.session_state.current_metadata = result.get("metadata", {})
        st.session_state.current_summary = result.get("summary", "")
        st.session_state.current_language = language
        st.session_state.current_model_used = result.get("model_used", "Groq")
        st.session_state.chat_history = []
        st.success("✅ Video processed and indexed into ChromaDB! Summary ready and Q&A activated below.")

    # ── Render Video Card & Summary (Top Section) ───────────────────────────
    if st.session_state.current_metadata:
        metadata = st.session_state.current_metadata
        summary = st.session_state.current_summary
        curr_lang = st.session_state.current_language
        model_name = st.session_state.get("current_model_used", "Groq")

        st.divider()

        # Video Card
        col_thumb, col_info = st.columns([1, 2])
        with col_thumb:
            if metadata.get("thumbnail"):
                st.image(metadata["thumbnail"], use_container_width=True)
        with col_info:
            st.subheader(metadata.get("title", "Video Title"))
            st.markdown(f"**Channel:** {metadata.get('channel', 'N/A')}")
            st.markdown(f"**Duration:** {metadata.get('duration', 'N/A')} | **Views:** {metadata.get('view_count', 'N/A')}")
            st.caption(f"Vector Collection: `yt_{metadata.get('video_id', '')}` (Permanent Memory Active)")

        # Summary Display
        if summary:
            st.markdown(f"#### 📄 AI Summary (Powered by Groq `{model_name}`)")
            if curr_lang == "Arabic":
                st.markdown(format_rtl(summary), unsafe_allow_html=True)
            else:
                st.markdown(summary)

        # ── Render Interactive Q&A Chat (Bottom Section) ─────────────────────
        st.divider()
        st.markdown("### 💬 Ask Questions About This Video")
        st.caption("Powered by **Google Gemini** grounded strictly in the video transcript indexed in ChromaDB.")

        # Display Chat History
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                if msg.get("language") == "Arabic" and msg["role"] == "assistant":
                    st.markdown(format_rtl(msg["content"]), unsafe_allow_html=True)
                else:
                    st.markdown(msg["content"])

        # Chat Input
        question = st.chat_input("Ask a question about this video (e.g., 'What are the key points explained?')...")

        if question:
            if not has_valid_gemini_key():
                st.error("🔑 **Gemini API Key missing!** Please enter your Gemini API key in the sidebar for Q&A.")
                return

            # Append user message
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            # Generate Gemini Response
            with st.chat_message("assistant"):
                with st.spinner("Retrieving video context from ChromaDB & generating answer with Gemini..."):
                    rag_result = run_rag_pipeline(
                        url=st.session_state.current_video_url,
                        question=question,
                        language=curr_lang
                    )

                if rag_result.get("error"):
                    err_msg = f"❌ {rag_result['error']}"
                    st.error(err_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": err_msg})
                    return

                answer = rag_result.get("answer", "No response generated.")
                if rag_result.get("is_cached"):
                    st.toast("⚡ Permanent memory hit: context retrieved from ChromaDB vector cache!")

                if curr_lang == "Arabic":
                    st.markdown(format_rtl(answer), unsafe_allow_html=True)
                else:
                    st.markdown(answer)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "language": curr_lang
                })
