"""
workflows/summarize_workflow.py
-------------------------------
LangGraph state machine for the YouTube Summarizer pipeline.
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from core.guardrails import validate_youtube_url
from core.video_processor import extract_video_id, get_transcript, get_video_metadata
from core.text_utils import truncate_transcript
from agents.crew import run_summarizer_crew


class SummarizeState(TypedDict):
    url: str
    language: str
    mode: str
    manual_transcript: Optional[str]
    video_id: Optional[str]
    metadata: Optional[dict]
    transcript: Optional[str]
    summary: Optional[str]
    error: Optional[str]


def validate_input_node(state: SummarizeState) -> SummarizeState:
    url = state.get("url", "")
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
    manual = state.get("manual_transcript", "").strip()

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
                "Please use the 'Paste Manual Transcript' section below."
            )
        }

    truncated_transcript = truncate_transcript(transcript)
    return {
        **state,
        "metadata": metadata,
        "transcript": truncated_transcript,
        "language": detected_lang or lang
    }



def generate_summary_node(state: SummarizeState) -> SummarizeState:
    if state.get("error"):
        return state

    summary = run_summarizer_crew(
        transcript=state["transcript"],
        metadata=state["metadata"],
        language=state["language"],
        mode=state.get("mode", "general")
    )

    return {**state, "summary": summary}


def should_continue(state: SummarizeState) -> str:
    if state.get("error"):
        return "end"
    return "next"


def build_summarize_workflow():
    workflow = StateGraph(SummarizeState)

    workflow.add_node("validate", validate_input_node)
    workflow.add_node("extract", extract_data_node)
    workflow.add_node("summarize", generate_summary_node)

    workflow.set_entry_point("validate")

    workflow.add_conditional_edges(
        "validate",
        should_continue,
        {"next": "extract", "end": END}
    )
    workflow.add_conditional_edges(
        "extract",
        should_continue,
        {"next": "summarize", "end": END}
    )
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
        "summary": None,
        "error": None
    }
    return summarize_app.invoke(initial_state)

