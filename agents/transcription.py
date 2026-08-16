"""Optional local Whisper transcription. The model is loaded only on request."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile


def transcribe(video_path: str | Path, start: float | None = None, duration: float | None = None) -> str:
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
        result = model.transcribe(input_path, fp16=False, verbose=False)
    except Exception as exc:
        raise RuntimeError(f"Whisper could not transcribe this file: {exc}") from exc
    finally:
        if temporary_audio:
            temporary_audio.unlink(missing_ok=True)
    return str(result.get("text", "")).strip()
