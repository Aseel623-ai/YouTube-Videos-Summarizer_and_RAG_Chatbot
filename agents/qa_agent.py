"""
agents/qa_agent.py
------------------
CrewAI agent for context-grounded video Q&A.
"""

from crewai import Agent, LLM
from config.settings import get_gemini_api_key, LLM_MODEL


def create_qa_agent() -> Agent:
    llm = LLM(model=LLM_MODEL, api_key=get_gemini_api_key(), temperature=0.1)

    return Agent(
        role="Video Q&A Specialist",
        goal=(
            """Answer user questions accurately, concisely, and exclusively using 
            the provided video context. Never hallucinate or use external knowledge."""
        ),
        backstory=(
            "You are a meticulous research analyst specialising in factual verification. "
            "You answer questions using ONLY retrieved context from video transcripts, "
            "maintaining strict fidelity to the source text in both English and Arabic."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

