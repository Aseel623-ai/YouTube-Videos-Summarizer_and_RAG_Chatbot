"""
agents/summarizer_agent.py
--------------------------
CrewAI agent that generates high-quality summaries from transcript analysis.
"""

from crewai import Agent, LLM
from config.settings import get_gemini_api_key, LLM_MODEL


def create_summarizer_agent() -> Agent:
    llm = LLM(model=LLM_MODEL, api_key=get_gemini_api_key(), temperature=0.3)

    return Agent(
        role="Expert YouTube Content Summarizer",
        goal=(
            "Transform raw video transcripts into structured, high-value summaries "
            "tailored to the user's preferred language (English or Arabic) and summary mode "
            "(General or Educational). Ensure zero fluff and strict factual consistency."
        ),
        backstory=(
            "You are an acclaimed instructional designer and technical editor. "
            "You possess the rare ability to extract core takeaways from complex video content "
            "and articulate them clearly, accurately, and compellingly in both Arabic and English."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

