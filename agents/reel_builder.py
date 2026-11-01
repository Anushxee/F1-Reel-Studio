"""FFmpeg-based vertical reel rendering and optional burned-in captions."""
from __future__ import annotations

from pathlib import Path
import subprocess
import textwrap
from dataclasses import dataclass
from typing import Iterable

from .highlights import Highlight
from .transcription import CaptionCue


@dataclass(frozen=True)
class ReelTheme:
    name: str
    accent: str
    caption_colour: str


THEMES: dict[str, ReelTheme] = {
    "Race Red": ReelTheme("Race Red", "&H002222FF", "&H00FFFFFF"),
    "Neon Night": ReelTheme("Neon Night", "&H00FFB000", "&H0000FFFF"),
    "Monochrome": ReelTheme("Monochrome", "&H00202020", "&H00FFFFFF"),
}


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


def _ass_time(seconds: float) -> str:
    centiseconds = max(0, round(seconds * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    secs, fraction = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{fraction:02d}"


def _ass_text(value: str) -> str:
    return " ".join(value.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}").split())


def write_ass_overlay(
    cues: Iterable[CaptionCue],
    duration: float,
    destination: str | Path,
    headline: str = "F1 REEL",
    handle: str = "@yourhandle",
    theme_name: str = "Race Red",
) -> Path:
    """Create an animated, word-timed ASS overlay for a 9:16 reel."""
    theme = THEMES.get(theme_name, THEMES["Race Red"])
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    header_end = min(duration, 2.4)
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
        f"Style: Title,Arial,50,&H00FFFFFF,{theme.accent},&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,3,0,8,40,40,80,1",
        f"Style: Handle,Arial,27,{theme.accent},{theme.accent},&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,2,0,8,40,40,155,1",
        f"Style: Caption,Arial,66,{theme.caption_colour},{theme.accent},&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,4,0,2,65,65,255,1",
        "",
        "[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
        f"Dialogue: 0,0:00:00.00,{_ass_time(header_end)},Title,,0,0,0,,{{\\an8\\pos(540,180)\\fad(100,250)}}{_ass_text(headline or 'F1 REEL')}",
        f"Dialogue: 0,0:00:00.00,{_ass_time(duration)},Handle,,0,0,0,,{{\\an8\\pos(540,285)}}{_ass_text(handle or '@yourhandle')}",
    ]
    for cue in cues:
        start = max(0.0, min(cue.start, duration))
        end = max(start + 0.08, min(cue.end, duration))
        if start >= duration:
            continue
        lines.append(
            f"Dialogue: 1,{_ass_time(start)},{_ass_time(end)},Caption,,0,0,0,,{{\\an2\\pos(540,1510)\\fad(60,60)}}{_ass_text(cue.text.upper())}"
        )
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
    return destination


def _filter_path(path: str | Path) -> str:
    return str(Path(path).resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def render_reel(
    source: str | Path,
    highlight: Highlight,
    destination: str | Path,
    caption_srt: str | Path | None = None,
    overlay_ass: str | Path | None = None,
) -> Path:
    """Create a standards-compliant 1080x1920 MP4 with audio and safe caption placement."""
    ensure_ffmpeg()
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    filters = [
        "scale=1080:1920:force_original_aspect_ratio=increase",
        "crop=1080:1920",
        "fps=30",
        "setpts=PTS-STARTPTS",
        "format=yuv420p",
    ]
    if overlay_ass:
        filters.append(f"ass='{_filter_path(overlay_ass)}'")
    if caption_srt:
        srt_path = _filter_path(caption_srt)
        filters.append(f"subtitles='{srt_path}':force_style='FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Alignment=2,MarginV=260'")
    command = ["ffmpeg", "-y", "-ss", f"{highlight.start:.2f}", "-t", f"{highlight.end-highlight.start:.2f}", "-i", str(source), "-vf", ",".join(filters), "-map", "0:v:0", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(destination)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    return destination


def render_montage(
    source: str | Path,
    highlights: list[Highlight],
    destination: str | Path,
    overlay_ass: str | Path | None = None,
) -> Path:
    """Render a consistent vertical montage from two or more selected highlights."""
    if not highlights:
        raise ValueError("Select at least one highlight for a montage.")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_segments: list[Path] = []
    manifest = destination.with_suffix(".concat.txt")
    try:
        for index, highlight in enumerate(highlights):
            segment = destination.parent / f".{destination.stem}_segment_{index}.mp4"
            render_reel(source, highlight, segment, overlay_ass=overlay_ass)
            temporary_segments.append(segment)
        manifest.write_text("\n".join(f"file '{segment.resolve().as_posix()}'" for segment in temporary_segments), encoding="utf-8")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(manifest), "-c", "copy", "-movflags", "+faststart", str(destination)],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        manifest.unlink(missing_ok=True)
        for segment in temporary_segments:
            segment.unlink(missing_ok=True)
    return destination


def render_cover(
    source: str | Path,
    highlight: Highlight,
    destination: str | Path,
    overlay_ass: str | Path | None = None,
) -> Path:
    """Export a matching 9:16 JPEG cover from a rendered branded preview."""
    # Extracting directly after input seeking gives subtitle renderers source-time
    # timestamps. Rendering a short preview first makes the cover exactly match
    # the visible title/handle treatment of the finished reel.
    ensure_ffmpeg()
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    preview = destination.parent / f".{destination.stem}_preview.mp4"
    preview_highlight = Highlight(
        highlight.start,
        min(highlight.end, highlight.start + 1.5),
        highlight.score,
        highlight.reason,
    )
    try:
        render_reel(source, preview_highlight, preview, overlay_ass=overlay_ass)
        command = ["ffmpeg", "-y", "-ss", "0.50", "-i", str(preview), "-frames:v", "1", "-vf", "format=yuvj420p", "-q:v", "2", str(destination)]
        subprocess.run(command, check=True, capture_output=True, text=True)
    finally:
        preview.unlink(missing_ok=True)
    return destination
