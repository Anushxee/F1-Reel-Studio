"""Social copy generation with an offline fallback and optional OpenAI refinement."""
from __future__ import annotations

import os


def create_metadata(transcript: str, topic: str, use_ai: bool = True, api_key: str | None = None) -> dict[str, str]:
    safe_topic = topic.strip() or "Formula 1 race highlight"
    fallback = {
        "title": safe_topic,
        "caption": f"{safe_topic} 🏁\n\nWhich moment had you on the edge of your seat?",
        "hashtags": "#F1 #Formula1 #F1Reels #Motorsport #RaceDay #FormulaOne #F1Fans #Racing",
        "music_note": "Choose a licensed track from Instagram's music library or a royalty-free provider before publishing.",
    }
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not use_ai or not api_key:
        return fallback
    try:
        from openai import OpenAI
        response = OpenAI(api_key=api_key).responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=("Write concise Instagram metadata for a race highlight. Avoid claims that are not in the input, "
                   "do not imply affiliation with Formula 1, and return title, caption, and 8 relevant hashtags.\n"
                   f"Topic: {safe_topic}\nTranscript: {transcript[:2500]}"),
        )
        text = response.output_text.strip()
        if text:
            fallback["caption"] = text
    except Exception:
        pass
    return fallback
