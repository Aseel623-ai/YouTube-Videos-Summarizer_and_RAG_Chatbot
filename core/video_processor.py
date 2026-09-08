"""
core/video_processor.py
-----------------------
All YouTube data extraction: video ID parsing, transcript fetching (with
language fallback), and metadata retrieval via yt-dlp.
"""

import re
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, VideoUnavailable, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter


# ── Video ID ─────────────────────────────────────────────────────────────────

def extract_video_id(url: str) -> str | None:
    """
    Extract the 11-character YouTube video ID from any supported URL format.
    Supports: youtube.com/watch?v=, youtu.be/, /embed/, /shorts/
    """
    if not url:
        return None

    patterns = [
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"[?&]v=([a-zA-Z0-9_-]{11})",
        r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


# ── Transcript ────────────────────────────────────────────────────────────────

_LANG_CODE_MAP = {"english": ["en", "en-US", "en-GB"], "arabic": ["ar"]}
_CODE_TO_LANG  = {"en": "english", "en-US": "english", "en-GB": "english", "ar": "arabic"}

def get_transcript(video_id: str, preferred_lang: str = "english") -> tuple[str | None, str | None]:
    """
    Fetch the transcript for a given video.

    Args:
        video_id       : 11-character YouTube video ID
        preferred_lang : "english" or "arabic"

    Returns:
        (transcript_text, detected_language) — both None on failure.
        Falls back to the other language if preferred is unavailable.
    """
    api       = YouTubeTranscriptApi()
    formatter = TextFormatter()
    lang_pref = preferred_lang.lower()

    primary_codes  = _LANG_CODE_MAP.get(lang_pref, ["en"])
    fallback_codes = _LANG_CODE_MAP.get("arabic" if lang_pref == "english" else "english", ["ar"])

    for codes in [primary_codes, fallback_codes]:
        try:
            transcript = api.fetch(video_id, languages=codes)
            text       = formatter.format_transcript(transcript)
            detected   = _CODE_TO_LANG.get(codes[0], lang_pref)
            return text, detected
        except (NoTranscriptFound, VideoUnavailable):
            continue
        except Exception:
            continue

    return None, None


# ── Metadata ──────────────────────────────────────────────────────────────────

def get_video_metadata(video_id: str) -> dict:
    """
    Retrieve rich video metadata using yt-dlp (no download).

    Returns a dict with: title, thumbnail, channel, duration,
    view_count, upload_date, video_id.
    Falls back to sensible defaults on any error.
    """
    fallback = {
        "title":       "Unknown Title",
        "thumbnail":   f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        "channel":     "Unknown Channel",
        "duration":    "N/A",
        "view_count":  "N/A",
        "upload_date": "N/A",
        "video_id":    video_id,
    }
    try:
        ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}", download=False
            )

        raw_date = info.get("upload_date", "")
        formatted_date = (
            f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
            if len(raw_date) == 8
            else "N/A"
        )

        return {
            "title":       info.get("title", fallback["title"]),
            "thumbnail":   info.get("thumbnail", fallback["thumbnail"]),
            "channel":     info.get("uploader", fallback["channel"]),
            "duration":    info.get("duration_string", "N/A"),
            "view_count":  f"{info.get('view_count', 0):,}",
            "upload_date": formatted_date,
            "video_id":    video_id,
        }
    except Exception:
        return fallback
