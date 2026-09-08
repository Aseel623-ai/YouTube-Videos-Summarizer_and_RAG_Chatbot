"""
agents/crew.py
--------------
CrewAI Orchestration: bundles Agents & Tasks into reusable Crews.
"""

from crewai import Crew, Task, Process
from agents.transcript_analyst import create_transcript_analyst
from agents.summarizer_agent import create_summarizer_agent
from agents.qa_agent import create_qa_agent
from prompts.summarizer_prompts import get_summarizer_prompt
from prompts.rag_prompts import get_qa_prompt


def run_summarizer_crew(
    transcript: str,
    metadata: dict,
    language: str = "English",
    mode: str = "general"
) -> str:
    """
    Run CrewAI crew to analyze transcript and produce a structured summary.
    """
    analyst = create_transcript_analyst()
    summarizer = create_summarizer_agent()

    task_analysis = Task(
        description=(
            f"Analyze the transcript for video '{metadata.get('title', 'Video')}'. "
            f"Identify main themes, key terminology, and structure.\n\nTranscript snippet:\n{transcript[:3000]}"
        ),
        expected_output="A list of core topics, main themes, and key terms found in the transcript.",
        agent=analyst,
    )

    prompt_template = get_summarizer_prompt(language, mode)
    formatted_prompt = prompt_template.format(
        title=metadata.get("title", "Video"),
        channel=metadata.get("channel", "Unknown Channel"),
        transcript=transcript
    )

    task_summary = Task(
        description=f"Produce the final summary using this template instruction:\n\n{formatted_prompt}",
        expected_output=f"A complete, beautifully formatted summary in {language}.",
        agent=summarizer,
    )

    crew = Crew(
        agents=[analyst, summarizer],
        tasks=[task_analysis, task_summary],
        process=Process.sequential,
        verbose=False
    )

    result = crew.kickoff()
    return str(result)


def run_qa_crew(
    question: str,
    context: str,
    metadata: dict,
    language: str = "English"
) -> str:
    """
    Run CrewAI crew to answer a user question using retrieved context.
    """
    qa_agent = create_qa_agent()
    prompt_template = get_qa_prompt(language)

    formatted_prompt = prompt_template.format(
        title=metadata.get("title", "Video"),
        channel=metadata.get("channel", "Unknown Channel"),
        duration=metadata.get("duration", "N/A"),
        context=context,
        question=question
    )

    task_qa = Task(
        description=f"Answer the user question based strictly on the retrieved context:\n\n{formatted_prompt}",
        expected_output=f"A direct, context-grounded answer in {language}.",
        agent=qa_agent,
    )

    crew = Crew(
        agents=[qa_agent],
        tasks=[task_qa],
        process=Process.sequential,
        verbose=False
    )

    result = crew.kickoff()
    return str(result)
