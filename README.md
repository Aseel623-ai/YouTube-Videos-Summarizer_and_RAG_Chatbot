# 🎬 YouTube AI Suite: Multilingual Summarizer & RAG Chatbot

A fast, lightweight, and production-grade AI platform that transforms YouTube videos into structured summaries and enables context-grounded conversational Q&A in English and Arabic.

Built with **LangGraph**, **Groq (`openai/gpt-oss-120b`)**, **Google Gemini (`gemini-2.5-flash`)**, **LangChain**, and **ChromaDB**.

---

## 🌟 Key Features

- **⚡ Dual-LLM Architecture**:
  - **Summarization**: Powered by **Groq** using `openai/gpt-oss-120b` for blazing-fast inference (~500 tokens/sec) on long transcripts.
  - **RAG Q&A**: Powered by **Google Gemini** (`gemini-2.5-flash`) for nuanced, multilingual, and context-grounded question answering.

- **🔄 Unified Single-View Workspace**:
  - Summarize and Chat in one continuous flow: enter a YouTube URL, generate the summary at the top, and immediately chat with the video below.
  - **Human-Readable Video Titles**: Dropdowns and cards display full YouTube Video Titles instead of cryptic video IDs.

- **💬 Multilingual RAG Chatbot**:
  - Context-grounded Q&A strictly based on the video transcript.
  - **Permanent Vector Memory**: ChromaDB persists vector indexes per video. Videos are embedded once and cached forever across sessions.
  - **Ultra-Fast & Lightweight Local Embeddings**: Powered by `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (~470MB, 50+ languages including Arabic and English, runs fast on CPU with zero API costs).

- **🛡️ Resilient Dual-Engine Transcript Extractor**:
  - **Primary**: `youtube-transcript-api` for fast caption retrieval.
  - **Secondary Fallback**: `yt-dlp` automatic subtitle extraction & WebVTT cleaner (bypasses YouTube anti-scraping limits & IP bans).
  - **Manual Fallback**: Integrated UI expander allowing users to paste transcript text directly if auto-captions are disabled.

- **⚡ Token & Context Optimization**:
  - **LangGraph State Machine**: Deterministic, lightweight graph replacing heavy agent frameworks with zero overhead.
  - **Context Processing Modes**:
    - ⚡ **Token Saver**: ~15,000 chars (~3.5k tokens) — Fast & low token usage.
    - ⚖️ **Balanced (Recommended)**: ~25,000 chars (~6k tokens) — Optimal context & quality.
    - 📜 **Detailed**: ~45,000 chars (~11k tokens) — For long lectures and courses.

- **⚙️ User API Key Configuration & Privacy**:
  - Sidebar inputs for both **Groq API Key** and **Google Gemini API Key**.
  - In-app guides on obtaining 100% free keys from Groq Console and Google AI Studio.
  - Session-scoped privacy: API keys stay in browser memory and are never persisted to disk.

---

## 📁 Project Structure

```
YouTube-Videos-Summarizer_and_RAG_Chatbot/
├── app.py                          # Streamlit application entry point (Unified Workspace)
├── config/
│   ├── __init__.py                 # Exported settings & helpers
│   └── settings.py                 # Dynamic API key resolution, models & config
├── core/
│   ├── video_processor.py          # YouTube ID extraction, dual-engine transcript parser & metadata
│   ├── text_utils.py               # Chunking, dynamic transcript truncation, RTL formatting
│   └── guardrails.py               # Strict URL validation & input sanitization
├── rag/
│   ├── vector_store.py             # ChromaDB persistent manager & title resolver
│   ├── embedder.py                 # Local BGE-M3 embeddings & vectorstore builder
│   └── retriever.py                # Similarity search context retriever
├── workflows/
│   ├── summarize_workflow.py       # LangGraph state machine for video processing, indexing & Groq summary
│   └── rag_workflow.py             # LangGraph state machine for Gemini RAG Q&A
├── prompts/
│   ├── summarizer_prompts.py       # General & Educational prompts (EN & AR)
│   └── rag_prompts.py              # Strict context-grounded Q&A prompts (EN & AR)
└── ui/
    ├── sidebar.py                  # Groq & Gemini API key configuration & user guide
    └── unified_view.py             # Unified single-tab workspace (Summary + Interactive Chat)
```

---

## 🚀 Local Setup

### 1. Installation

```bash
cd YouTube-Videos-Summarizer_and_RAG_Chatbot
pip install -r requirements.txt
```

### 2. Environment Setup (Optional)

You can configure default credentials in `.env`:

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run Application

```bash
streamlit run app.py
```

---

## 🌐 Deploying to Streamlit Community Cloud

1. Push your repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and create a new app pointing to `app.py`.
3. *(Optional)* Add secrets under **Advanced Settings > Secrets**:
   ```toml
   GROQ_API_KEY = "gsk_..."
   GEMINI_API_KEY = "AIzaSy..."
   ```
4. Click **Deploy**!
