"""
ui/admin_tab.py
---------------
Streamlit UI for Tab 3: Protected Admin Dashboard to inspect and manage ChromaDB vector store.
"""

import os
import streamlit as st

def get_admin_password() -> str:
    try:
        from config.settings import get_admin_password as _gap
        return _gap()
    except Exception:
        try:
            if hasattr(st, "secrets") and "ADMIN_PASSWORD" in st.secrets:
                return str(st.secrets["ADMIN_PASSWORD"]).strip()
        except Exception:
            pass
        return os.getenv("ADMIN_PASSWORD", "admin123")

try:
    from rag.vector_store import ChromaManager
except Exception:
    ChromaManager = None

try:
    from core.video_processor import get_video_metadata
except Exception:
    def get_video_metadata(video_id: str) -> dict:
        return {
            "title": f"Video {video_id}",
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
            "channel": "Unknown Channel",
            "duration": "N/A",
            "view_count": "N/A",
            "upload_date": "N/A",
            "video_id": video_id,
        }




def render_admin_tab():
    st.markdown("### 👑 Admin Dashboard — ChromaDB Vector Store Inspector")
    st.caption("Inspect stored vector collections, view text chunks, and manage database memory.")

    # 1. Admin Authentication Check
    if not st.session_state.get("admin_authenticated", False):
        st.divider()
        st.warning("🔒 **Admin Access Required**. Please authenticate to view ChromaDB contents.")

        col_pwd, col_btn = st.columns([3, 1])
        with col_pwd:
            input_pwd = st.text_input(
                "Enter Admin Password",
                type="password",
                placeholder="Default: admin123",
                key="admin_pwd_input"
            )
        with col_btn:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🔓 Login to Dashboard", type="primary", use_container_width=True):
                correct_pwd = get_admin_password()
                if input_pwd.strip() == correct_pwd:
                    st.session_state.admin_authenticated = True
                    st.success("✅ Admin authenticated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Access denied.")
        st.info("💡 **Default Password**: `admin123` (Set `ADMIN_PASSWORD` in `.env` or Streamlit Secrets to customize).")
        return

    # 2. Authenticated Admin View
    header_col1, header_col2 = st.columns([4, 1])
    with header_col1:
        st.success("🔓 Authenticated as Administrator")
    with header_col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()

    st.divider()

    manager = ChromaManager()
    stats = manager.get_db_stats()
    processed_videos = manager.list_processed_videos()

    # 3. Key Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="📦 Total Indexed Videos", value=stats["total_collections"])
    with m2:
        st.metric(label="📄 Total Vector Chunks", value=f"{stats['total_chunks']:,}")
    with m3:
        st.metric(label="💾 Storage Path", value=stats["db_path"])

    st.divider()

    # 4. Collection Inspector
    st.markdown("### 🔍 ChromaDB Collection Inspector")

    if not processed_videos:
        st.info("ℹ️ No video collections currently stored in ChromaDB. Process a video in Tab 2 (RAG Chatbot) to create vector embeddings.")
        return

    selected_video = st.selectbox(
        "Select a Video Collection to Inspect:",
        options=processed_videos,
        format_func=lambda x: f"Video ID: {x}",
        key="admin_selected_video"
    )

    if selected_video:
        col_data = manager.get_collection_data(selected_video)
        meta = get_video_metadata(selected_video)

        # Video Card Header
        card_col1, card_col2 = st.columns([1, 3])
        with card_col1:
            if meta.get("thumbnail"):
                st.image(meta["thumbnail"], use_container_width=True)
        with card_col2:
            st.subheader(meta.get("title", "Video Title"))
            st.markdown(f"**Channel:** {meta.get('channel', 'N/A')} | **Duration:** {meta.get('duration', 'N/A')}")
            st.markdown(f"**Vector Collection Name:** `{ChromaManager.collection_name(selected_video)}`")
            st.markdown(f"**Total Stored Chunks:** `{col_data['count']}` chunks")

        st.divider()

        # Chunk Filter / Search
        search_query = st.text_input(
            "🔎 Filter Chunks Text:",
            placeholder="Type keyword to filter chunks...",
            key="admin_chunk_search"
        )

        st.markdown(f"#### 📜 Chunks in Vector Collection ({col_data['count']} Total)")

        docs = col_data["documents"]
        metadatas = col_data["metadatas"]
        ids = col_data["ids"]

        filtered_indices = []
        for idx, doc_text in enumerate(docs):
            if not search_query.strip() or search_query.lower() in doc_text.lower():
                filtered_indices.append(idx)

        if not filtered_indices:
            st.warning("No chunks matched your search filter.")
        else:
            for idx in filtered_indices:
                chunk_id = ids[idx] if idx < len(ids) else f"chunk_{idx}"
                chunk_meta = metadatas[idx] if idx < len(metadatas) else {}
                chunk_text = docs[idx]

                with st.expander(f"🧩 Chunk #{idx + 1} — ID: `{chunk_id}` ({len(chunk_text)} chars)"):
                    st.markdown("**Chunk Metadata:**")
                    st.json(chunk_meta)
                    st.markdown("**Chunk Content:**")
                    st.code(chunk_text, language="text")

        st.divider()

        # Collection Actions
        st.markdown("### ⚙️ Collection Actions")
        col_act1, col_act2 = st.columns(2)

        with col_act1:
            if st.button("🗑️ Delete Selected Video Collection", type="secondary", use_container_width=True):
                manager.delete_collection(selected_video)
                st.toast(f"Deleted vector index for video '{selected_video}'!")
                st.rerun()

        with col_act2:
            with st.popover("⚠️ Purge Entire ChromaDB Vector Database"):
                st.error("Warning: This will delete ALL stored vector collections for all videos!")
                confirm = st.checkbox("Yes, I understand this will permanently delete all vector data.", key="confirm_purge")
                if st.button("🔥 Confirm Purge All Data", type="primary", disabled=not confirm):
                    if manager.purge_database():
                        st.success("Successfully purged entire vector database!")
                        st.rerun()
                    else:
                        st.error("Failed to purge database.")
