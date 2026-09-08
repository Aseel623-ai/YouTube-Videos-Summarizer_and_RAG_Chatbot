"""
agents/transcript_analyst.py
----------------------------
CrewAI agent that analyses the transcript before summarisation.
Identifies main topics, tone, language, and quality issues.
"""

from crewai import Agent, LLM
from config.settings import get_gemini_api_key, LLM_MODEL


def create_transcript_analyst() -> Agent:
    llm = LLM(model=LLM_MODEL, api_key=get_gemini_api_key(), temperature=0.1)

    return Agent(
        role="YouTube Transcript Analyst",
        goal=(
            "Analyse YouTube video transcripts to identify main topics, "
            "validate content quality, detect the primary language, and extract "
            "structured insights that guide the summarisation process."
        ),
        backstory=(
            "You are a senior NLP researcher and content strategist with deep "
            "experience across YouTube content in multiple domains and languages. "
            "You specialise in Arabic and English content, quickly identifying "
            "the key themes, tone, and structure of any video transcript. "
            "Your rigorous analysis forms the foundation for high-quality summaries."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

