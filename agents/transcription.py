"""Optional local Whisper transcription. The model is loaded only on request."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile


@dataclass(frozen=True)
class CaptionCue:
    """A timed caption fragment relative to the exported highlight."""

    start: float
    end: float
    text: str


def transcribe_with_cues(
    video_path: str | Path, start: float | None = None, duration: float | None = None
) -> tuple[str, list[CaptionCue]]:
    """Transcribe a source segment and return Whisper's word-level timings."""
    try:
        import whisper
    except ImportError as exc:
        raise RuntimeError("Whisper is not installed. Run: pip install openai-whisper") from exc
    input_path = str(video_path)
    temporary_audio: Path | None = None
    if start is not None and duration is not None:
        file_descriptor, audio_name = tempfile.mkstemp(suffix=".wav")
        os.close(file_descriptor)
        temporary_audio = Path(audio_name)
        command = ["ffmpeg", "-y", "-ss", f"{start:.2f}", "-t", f"{duration:.2f}", "-i", input_path,
                   "-vn", "-ac", "1", "-ar", "16000", str(temporary_audio)]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            input_path = str(temporary_audio)
        except Exception as exc:
            temporary_audio.unlink(missing_ok=True)
            raise RuntimeError("FFmpeg could not prepare audio for Whisper.") from exc
    model_name = os.getenv("WHISPER_MODEL", "base")
    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(input_path, fp16=False, verbose=False, word_timestamps=True)
    except Exception as exc:
        raise RuntimeError(f"Whisper could not transcribe this file: {exc}") from exc
    finally:
        if temporary_audio:
            temporary_audio.unlink(missing_ok=True)
    text = str(result.get("text", "")).strip()
    cues: list[CaptionCue] = []
    for segment in result.get("segments", []):
        for word in segment.get("words", []):
            word_text = str(word.get("word", "")).strip()
            if word_text:
                cues.append(
                    CaptionCue(
                        max(0.0, float(word.get("start", 0.0))),
                        max(0.1, float(word.get("end", 0.1))),
                        word_text,
                    )
                )
    # Older Whisper backends can omit word data. Keep the creator workflow
    # useful by distributing the words across the detected segment duration.
    if not cues and text:
        words = text.split()
        total = duration or max(1.0, len(words) * 0.38)
        step = total / len(words)
        cues = [CaptionCue(index * step, min(total, (index + 1) * step), word) for index, word in enumerate(words)]
    return text, cues


def transcribe(video_path: str | Path, start: float | None = None, duration: float | None = None) -> str:
    """Backward-compatible text-only transcription helper."""
    return transcribe_with_cues(video_path, start, duration)[0]
