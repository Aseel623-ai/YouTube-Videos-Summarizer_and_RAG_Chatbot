"""
core/guardrails.py
------------------
Input validation and sanitization — called at workflow entry points
to reject bad input early before any expensive API calls are made.
"""

import re


# ── URL Validation ────────────────────────────────────────────────────────────

_YOUTUBE_PATTERNS = [
    r"youtu\.be/[a-zA-Z0-9_-]{11}",
    r"youtube\.com/watch\?.*v=[a-zA-Z0-9_-]{11}",
    r"youtube\.com/embed/[a-zA-Z0-9_-]{11}",
    r"youtube\.com/shorts/[a-zA-Z0-9_-]{11}",
]

def validate_youtube_url(url: str) -> bool:
    """
    Return True only if the URL is a valid, recognisable YouTube link.
    """
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    return any(re.search(p, url) for p in _YOUTUBE_PATTERNS)


# ── Question Sanitization ─────────────────────────────────────────────────────

def sanitize_question(question: str, max_length: int = 500) -> str:
    """
    Normalize whitespace and enforce a character limit on user questions.
    Returns an empty string if the input is blank.
    """
    if not question or not isinstance(question, str):
        return ""
    cleaned = " ".join(question.split())   # collapse whitespace
    return cleaned[:max_length]
