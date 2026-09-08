# 🎬 YouTube AI Suite: Multilingual Summarizer & RAG Chatbot

A production-grade AI platform that transforms YouTube video content into structured summaries and enables context-grounded conversational Q&A in English and Arabic.

Built with **CrewAI**, **LangChain**, **LangGraph**, **ChromaDB**, and **Google Gemini**.

---

## 🌟 Key Features

- **📝 AI Video Summarizer (Tab 1)**:
  - Supports General Summaries & Educational Analysis (Bloom's Taxonomy).
  - Multilingual support: English & Arabic (with native RTL styling).
  - Rich metadata extraction via `yt-dlp` (thumbnail, channel, view count, duration).

- **💬 Multilingual RAG Chatbot (Tab 2)**:
  - Context-grounded Q&A strictly based on video transcript content.
  - **Permanent Vector Memory**: ChromaDB persists vector indexes per `video_id`. Videos are embedded once and cached forever across sessions.
  - **Zero API Limit Local Embeddings**: Powered by `BAAI/bge-m3` via HuggingFace (runs locally on CPU/GPU).

- **⚙️ User API Key Configuration**:
  - Sidebar configuration allowing any user to input their own **Google Gemini API Key**.
  - Built-in interactive guide on how to get a FREE Gemini API key from Google AI Studio.
  - Session-scoped privacy: API keys remain in user browser memory and are never persisted on disk.

- **🏗️ Enterprise Architecture**:
  - **CrewAI**: Role-based agents (`Transcript Analyst`, `Summarizer Agent`, `Video Q&A Specialist`).
  - **LangGraph**: Stateful graph orchestrator with error handling and cache hit detection.
  - **LangChain**: Retrieval chains, document splitters, and model integrations.

---

## 📁 Project Structure

```
YouTube-Videos-Summarizer_and_RAG_Chatbot/
├── app.py                          # Streamlit application entry point
├── config/
│   └── settings.py                 # Centralized configuration & dynamic API key resolution
├── core/
│   ├── video_processor.py          # YouTube ID extraction, transcript & metadata
│   ├── text_utils.py               # Chunking, transcript truncation, RTL formatting
│   └── guardrails.py               # Strict URL validation & input sanitization
├── rag/
│   ├── vector_store.py             # ChromaDB persistent manager
│   ├── embedder.py                 # Local BGE-M3 embeddings & embedding pipeline
│   └── retriever.py                # Similarity search context retriever
├── agents/
│   ├── transcript_analyst.py       # CrewAI analyst agent
│   ├── summarizer_agent.py         # CrewAI summarizer agent
│   ├── qa_agent.py                 # CrewAI Q&A agent
│   └── crew.py                     # CrewAI crew definitions
├── workflows/
│   ├── summarize_workflow.py       # LangGraph state machine for summarization
│   └── rag_workflow.py             # LangGraph state machine for RAG Q&A
├── prompts/
│   ├── summarizer_prompts.py       # General & Educational prompts (EN & AR)
│   └── rag_prompts.py              # Context-grounded Q&A prompts (EN & AR)
└── ui/
    ├── sidebar.py                  # API Key configuration & user instructions
    ├── summarizer_tab.py           # Tab 1 UI renderer
    └── chatbot_tab.py              # Tab 2 UI renderer
```

---

## 🚀 Local Setup

### 1. Installation

```bash
cd YouTube-Videos-Summarizer_and_RAG_Chatbot
pip install -r requirements.txt
```

### 2. Environment Setup (Optional)

You can configure a default `GEMINI_API_KEY` in `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

*Note: Users can also input their key directly in the Streamlit web UI sidebar.*

### 3. Run Application

```bash
streamlit run app.py
```

---

## 🌐 Deploying to Streamlit Community Cloud (Public Link)

To make your application publicly available to anyone via a web link:

### Step 1: Push Code to GitHub
1. Create a repository on GitHub (e.g., `youtube-ai-suite`).
2. Push your project code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.name
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
2. Click **"New App"** (or **"Create App"**).
3. Select your GitHub repository, branch (`main`), and set Main file path to `app.py` (or `YouTube-Videos-Summarizer_and_RAG_Chatbot/app.py` if nested).
4. *(Optional)* Click **"Advanced Settings..."** -> **"Secrets"** and enter your fallback API key:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```
5. Click **"Deploy!"**.

Once deployed, Streamlit Cloud will generate a unique public URL (e.g. `https://your-app.streamlit.app`) that you can share with anyone!
