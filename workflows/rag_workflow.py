"""
workflows/rag_workflow.py
-------------------------
LangGraph state machine for RAG indexing & Q&A pipeline with ChromaDB permanent memory caching.
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from core.guardrails import validate_youtube_url, sanitize_question
from core.video_processor import extract_video_id, get_transcript, get_video_metadata
from core.text_utils import chunk_transcript
from rag.vector_store import ChromaManager
from rag.embedder import embed_and_store
from rag.retriever import retrieve_context
from agents.crew import run_qa_crew


class RAGState(TypedDict):
    url: str
    question: str
    language: str
    video_id: Optional[str]
    metadata: Optional[dict]
    context: Optional[str]
    answer: Optional[str]
    is_cached: Optional[bool]
    error: Optional[str]


def validate_rag_input(state: RAGState) -> RAGState:
    url = state.get("url", "")
    question = sanitize_question(state.get("question", ""))

    if not validate_youtube_url(url):
        return {**state, "error": "Invalid YouTube URL."}
    
    if not question:
        return {**state, "error": "Please enter a valid question."}

    video_id = extract_video_id(url)
    if not video_id:
        return {**state, "error": "Could not extract video ID."}

    return {**state, "video_id": video_id, "question": question}


def index_video_node(state: RAGState) -> RAGState:
    if state.get("error"):
        return state

    video_id = state["video_id"]
    lang = state.get("language", "English")
    manager = ChromaManager()

    metadata = get_video_metadata(video_id)

    # Permanent memory check
    if manager.collection_exists(video_id):
        return {**state, "metadata": metadata, "is_cached": True}

    # Fetch transcript and embed
    transcript, detected_lang = get_transcript(video_id, preferred_lang=lang)
    if not transcript:
        return {**state, "error": f"No transcript found for video '{video_id}'."}

    chunks = chunk_transcript(transcript, video_id=video_id)
    embed_and_store(chunks, video_id=video_id)

    return {
        **state,
        "metadata": metadata,
        "language": detected_lang or lang,
        "is_cached": False
    }


def retrieve_context_node(state: RAGState) -> RAGState:
    if state.get("error"):
        return state

    video_id = state["video_id"]
    question = state["question"]

    context = retrieve_context(question=question, video_id=video_id)
    if not context:
        return {**state, "error": "Could not retrieve relevant content from video."}

    return {**state, "context": context}


def generate_answer_node(state: RAGState) -> RAGState:
    if state.get("error"):
        return state

    answer = run_qa_crew(
        question=state["question"],
        context=state["context"],
        metadata=state["metadata"],
        language=state.get("language", "English")
    )

    return {**state, "answer": answer}


def should_continue_rag(state: RAGState) -> str:
    if state.get("error"):
        return "end"
    return "next"


def build_rag_workflow():
    workflow = StateGraph(RAGState)

    workflow.add_node("validate", validate_rag_input)
    workflow.add_node("index", index_video_node)
    workflow.add_node("retrieve", retrieve_context_node)
    workflow.add_node("answer", generate_answer_node)

    workflow.set_entry_point("validate")

    workflow.add_conditional_edges("validate", should_continue_rag, {"next": "index", "end": END})
    workflow.add_conditional_edges("index", should_continue_rag, {"next": "retrieve", "end": END})
    workflow.add_conditional_edges("retrieve", should_continue_rag, {"next": "answer", "end": END})
    workflow.add_edge("answer", END)

    return workflow.compile()


rag_app = build_rag_workflow()


def run_rag_pipeline(url: str, question: str, language: str = "English") -> RAGState:
    initial_state: RAGState = {
        "url": url,
        "question": question,
        "language": language,
        "video_id": None,
        "metadata": None,
        "context": None,
        "answer": None,
        "is_cached": None,
        "error": None
    }
    return rag_app.invoke(initial_state)
