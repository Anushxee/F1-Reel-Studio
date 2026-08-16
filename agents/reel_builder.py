"""FFmpeg-based vertical reel rendering and optional burned-in captions."""
from __future__ import annotations

from pathlib import Path
import subprocess
import textwrap

from .highlights import Highlight


def ensure_ffmpeg() -> None:
    for binary in ("ffmpeg", "ffprobe"):
        try:
            subprocess.run([binary, "-version"], check=True, capture_output=True)
        except FileNotFoundError as exc:
            raise RuntimeError("FFmpeg is required. Install it and add its bin folder to PATH.") from exc


def write_srt(text: str, duration: float, destination: str | Path) -> Path | None:
    clean = " ".join(text.split())
    if not clean:
        return None
    lines = textwrap.wrap(clean, width=34)[:2]
    destination = Path(destination)
    destination.write_text("1\n00:00:00,000 --> 00:00:%02d,000\n%s\n" % (max(1, int(duration)), "\\n".join(lines)), encoding="utf-8")
    return destination


def render_reel(source: str | Path, highlight: Highlight, destination: str | Path, caption_srt: str | Path | None = None) -> Path:
    """Create a standards-compliant 1080x1920 MP4 with audio and safe caption placement."""
    ensure_ffmpeg()
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    filters = [
        "scale=1080:1920:force_original_aspect_ratio=increase",
        "crop=1080:1920",
        "fps=30",
        "format=yuv420p",
    ]
    if caption_srt:
        srt_path = str(Path(caption_srt).resolve()).replace('\\', '/').replace(':', '\\:')
        filters.append(f"subtitles='{srt_path}':force_style='FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Alignment=2,MarginV=260'")
    command = ["ffmpeg", "-y", "-ss", f"{highlight.start:.2f}", "-t", f"{highlight.end-highlight.start:.2f}", "-i", str(source), "-vf", ",".join(filters), "-map", "0:v:0", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(destination)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    return destination
