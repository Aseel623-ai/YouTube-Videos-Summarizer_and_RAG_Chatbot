"""
ui/summarizer_tab.py
--------------------
Streamlit UI layout & rendering logic for Tab 1 (Summarizer).
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
from workflows.summarize_workflow import run_summarize_pipeline
import streamlit as st



def render_summarizer_tab():
    st.markdown("### 📝 YouTube Video Summarizer")
    st.caption("Generate structured summaries powered by CrewAI agents, LangGraph, and Gemini.")

    col_url, col_lang = st.columns([3, 1])

    with col_url:
        url_input = st.text_input(
            "YouTube Video URL",
            placeholder="https://www.youtube.com/watch?v=...",
            key="summarizer_url_input"
        )
    with col_lang:
        language = st.selectbox(
            "Output Language",
            ["English", "Arabic"],
            key="summarizer_lang_select"
        )

    mode = st.radio(
        "Summary Mode",
        ["general", "educational"],
        horizontal=True,
        format_func=lambda x: "📌 General Summary" if x == "general" else "🎓 Educational Analysis (Bloom's Taxonomy)",
        key="summarizer_mode_radio"
    )

    with st.expander("🛠️ Advanced: Paste Manual Transcript (Optional / خيار إدخال النص يدوياً)"):
        manual_transcript_input = st.text_area(
            "Paste Transcript Text",
            placeholder="If YouTube restricts auto-captions for this video, copy and paste the transcript text here...",
            height=120,
            key="summarizer_manual_transcript"
        )

    if st.button("🚀 Generate Summary", type="primary", use_container_width=True):
        if not has_valid_api_key():
            st.error("🔑 **Gemini API Key missing!** Please enter your API key in the sidebar configuration on the left.")
            return

        if not url_input.strip():
            st.warning("Please enter a YouTube video URL first.")
            return

        with st.spinner("Processing video and running AI workflow..."):
            result = run_summarize_pipeline(
                url=url_input,
                language=language,
                mode=mode,
                manual_transcript=manual_transcript_input.strip()
            )


        if result.get("error"):
            st.error(f"❌ Error: {result['error']}")
            return

        metadata = result.get("metadata", {})
        summary = result.get("summary", "")

        # Display Video Metadata Card
        st.divider()
        col_thumb, col_info = st.columns([1, 2])
        with col_thumb:
            if metadata.get("thumbnail"):
                st.image(metadata["thumbnail"], use_container_width=True)
        with col_info:
            st.subheader(metadata.get("title", "Video Title"))
            st.markdown(f"**Channel:** {metadata.get('channel', 'N/A')}")
            st.markdown(f"**Duration:** {metadata.get('duration', 'N/A')} | **Views:** {metadata.get('view_count', 'N/A')}")

        st.divider()
        st.markdown("### 📄 Summary Result")

        if language == "Arabic":
            st.markdown(format_rtl(summary), unsafe_allow_html=True)
        else:
            st.markdown(summary)
