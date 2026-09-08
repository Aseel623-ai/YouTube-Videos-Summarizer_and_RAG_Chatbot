"""
ui/sidebar.py
--------------
Streamlit Sidebar rendering: API key configuration & user instructions.
"""

import streamlit as st
import os


def render_sidebar():
    """Render the sidebar configuration and API key guide."""
    with st.sidebar:
        st.markdown("## ⚙️ Configuration / الإعدادات")
        st.markdown("Provide your own Google Gemini API key to run the app.")

        # API Key input
        custom_key = st.text_input(
            "🔑 Gemini API Key",
            type="password",
            placeholder="AIzaSy...",
            help="Enter your personal Google Gemini API key. It remains private to your browser session.",
            key="custom_gemini_api_key"
        )

        # Status Pill
        active_key = custom_key.strip() or os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
        if not active_key:
            try:
                if "GEMINI_API_KEY" in st.secrets:
                    active_key = str(st.secrets["GEMINI_API_KEY"])
            except Exception:
                pass

        if custom_key.strip():
            st.success("🟢 Using Custom User API Key")
        elif active_key:
            st.info("🔵 Using Default System API Key")
        else:
            st.warning("⚠️ No API Key Detected. Please enter a key above.")

        st.divider()

        # How to get API Key expander
        with st.expander("❓ How to get a FREE Gemini API Key? / كيف تحصل على مفتاح API مجاني؟", expanded=False):
            st.markdown("""
            ### 🇸🇦 بالعربية:
            1. توجه إلى [Google AI Studio](https://aistudio.google.com/app/apikey).
            2. قم بتسجيل الدخول باستخدام حساب **Google** الخاص بك.
            3. اضغط على زر **"Create API Key"** (إنشاء مفتاح API).
            4. اختر المشروع أو أنشئ مشروعاً جديداً ثم انسخ المفتاح المتولد.
            5. الصق المفتاح في خانة **Gemini API Key** بالأعلى.

            ---

            ### 🇬🇧 In English:
            1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
            2. Sign in with your **Google Account**.
            3. Click on the **"Create API Key"** button.
            4. Select your Google Cloud project (or let it auto-create) and copy the generated key.
            5. Paste your key into the **Gemini API Key** box above.

            ---

            🔒 **Privacy Note / ملاحظة خصوصية:**
            - Your API key is stored only in your temporary browser session memory.
            - It is **never** saved, logged, or shared anywhere.
            """)

        st.divider()
        st.caption("🚀 **YouTube AI Suite v1.0** | Powered by CrewAI, LangChain, LangGraph & Gemini")
