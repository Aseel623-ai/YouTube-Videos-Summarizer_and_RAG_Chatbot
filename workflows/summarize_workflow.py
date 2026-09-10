"""
workflows/summarize_workflow.py
-------------------------------
LangGraph state machine for YouTube processing, indexing to ChromaDB, and Groq Summarization.
Includes automatic TPM rate-limit handling and graceful model fallback.
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

from config.settings import (
    get_groq_api_key,
    get_groq_model,
    FALLBACK_GROQ_MODEL,
    GROQ_TEMPERATURE,
    get_max_transcript_chars
)
from core.guardrails import validate_youtube_url
from core.video_processor import extract_video_id, get_transcript, get_video_metadata
from core.text_utils import truncate_transcript, chunk_transcript, clean_llm_response
from rag.vector_store import ChromaManager
from rag.embedder import embed_and_store
from prompts.summarizer_prompts import get_summarizer_prompt


class SummarizeState(TypedDict):
    url: str
    language: str
    mode: str
    manual_transcript: Optional[str]
    video_id: Optional[str]
    metadata: Optional[dict]
    transcript: Optional[str]
    truncated_transcript: Optional[str]
    summary: Optional[str]
    is_indexed: Optional[bool]
    model_used: Optional[str]
    error: Optional[str]


def validate_input_node(state: SummarizeState) -> SummarizeState:
    url = state.get("url", "").strip()
    if not validate_youtube_url(url):
        return {**state, "error": "Invalid YouTube URL. Please enter a valid YouTube link."}
    
    video_id = extract_video_id(url)
    if not video_id:
        return {**state, "error": "Could not extract video ID from URL."}
    
    return {**state, "video_id": video_id}


def extract_data_node(state: SummarizeState) -> SummarizeState:
    if state.get("error"):
        return state

    video_id = state["video_id"]
    lang = state.get("language", "English")
    manual = (state.get("manual_transcript") or "").strip()

    metadata = get_video_metadata(video_id)

    if manual:
        transcript = manual
        detected_lang = lang
    else:
        transcript, detected_lang = get_transcript(video_id, preferred_lang=lang)

    if not transcript:
        return {
            **state,
            "error": (
                f"Could not fetch transcript automatically for video '{video_id}'. "
                "YouTube may have restricted subtitle access or the video lacks captions. "
                "Please use the 'Paste Manual Transcript' expander below."
            )
        }

    max_chars = get_max_transcript_chars()
    truncated_transcript = truncate_transcript(transcript, max_chars=max_chars)

    return {
        **state,
        "metadata": metadata,
        "transcript": transcript,
        "truncated_transcript": truncated_transcript,
        "language": detected_lang or lang
    }


def index_vector_node(state: SummarizeState) -> SummarizeState:
    """Pre-index transcript into ChromaDB so RAG Q&A is immediately active."""
    if state.get("error"):
        return state

    video_id = state["video_id"]
    transcript = state.get("transcript", "")
    manager = ChromaManager()

    if not manager.collection_exists(video_id) and transcript:
        try:
            chunks = chunk_transcript(transcript, video_id=video_id)
            embed_and_store(chunks, video_id=video_id)
        except Exception as e:
            print(f"[Warning] Vector indexing error: {e}")

    return {**state, "is_indexed": True}


def generate_summary_node(state: SummarizeState) -> SummarizeState:
    """Generate structured summary using Groq LLM with TPM safety and model fallback."""
    if state.get("error"):
        return state

    groq_api_key = get_groq_api_key()
    if not groq_api_key:
        return {**state, "error": "Groq API Key missing. Please provide your Groq API key in the sidebar."}

    lang = state.get("language", "English")
    mode = state.get("mode", "general")
    metadata = state.get("metadata", {})
    transcript_text = state.get("truncated_transcript") or state.get("transcript", "")

    prompt_template_str = get_summarizer_prompt(lang, mode)
    prompt = PromptTemplate.from_template(prompt_template_str)

    primary_model = get_groq_model()
    models_to_try = [primary_model]
    if primary_model != FALLBACK_GROQ_MODEL:
        models_to_try.append(FALLBACK_GROQ_MODEL)

    last_error = None

    for model_name in models_to_try:
        try:
            # If trying gpt-oss-120b, ensure context length is strictly under its 8k TPM limit
            current_transcript = transcript_text
            if "gpt-oss-120b" in model_name:
                current_transcript = truncate_transcript(transcript_text, max_chars=12_000)

            llm = ChatGroq(
                model_name=model_name,
                groq_api_key=groq_api_key,
                temperature=GROQ_TEMPERATURE,
            )

            chain = prompt | llm
            response = chain.invoke({
                "title": metadata.get("title", "Video"),
                "channel": metadata.get("channel", "Unknown Channel"),
                "transcript": current_transcript
            })

            summary_content = clean_llm_response(response)
            return {
                **state,
                "summary": summary_content,
                "model_used": model_name
            }
        except Exception as e:
            last_error = e
            err_str = str(e)
            # If rate limit / TPM limit 413 exceeded, attempt fallback model
            if "413" in err_str or "rate_limit_exceeded" in err_str or "tokens per minute" in err_str:
                continue
            else:
                break

    return {**state, "error": f"Groq Summarization Error: {str(last_error)}"}


def should_continue(state: SummarizeState) -> str:
    if state.get("error"):
        return "end"
    return "next"


def build_summarize_workflow():
    workflow = StateGraph(SummarizeState)

    workflow.add_node("validate", validate_input_node)
    workflow.add_node("extract", extract_data_node)
    workflow.add_node("index", index_vector_node)
    workflow.add_node("summarize", generate_summary_node)

    workflow.set_entry_point("validate")

    workflow.add_conditional_edges("validate", should_continue, {"next": "extract", "end": END})
    workflow.add_conditional_edges("extract", should_continue, {"next": "index", "end": END})
    workflow.add_conditional_edges("index", should_continue, {"next": "summarize", "end": END})
    workflow.add_edge("summarize", END)

    return workflow.compile()


summarize_app = build_summarize_workflow()


def run_summarize_pipeline(
    url: str,
    language: str = "English",
    mode: str = "general",
    manual_transcript: str = ""
) -> SummarizeState:
    initial_state: SummarizeState = {
        "url": url,
        "language": language,
        "mode": mode,
        "manual_transcript": manual_transcript,
        "video_id": None,
        "metadata": None,
        "transcript": None,
        "truncated_transcript": None,
        "summary": None,
        "is_indexed": False,
        "model_used": None,
        "error": None
    }
    return summarize_app.invoke(initial_state)
