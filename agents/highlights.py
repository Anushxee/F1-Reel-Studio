"""Local, explainable highlight detection for uploaded race footage."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

import cv2
import numpy as np


@dataclass(frozen=True)
class Highlight:
    start: float
    end: float
    score: float
    reason: str


def probe_duration(video_path: str | Path) -> float:
    command = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return float(completed.stdout.strip())


def _pick_non_overlapping(candidates: list[tuple[float, float]], count: int, clip_seconds: int) -> list[Highlight]:
    selected: list[Highlight] = []
    for score, moment in sorted(candidates, reverse=True):
        start = max(0.0, moment - clip_seconds * 0.45)
        end = start + clip_seconds
        if all(end <= item.start or start >= item.end for item in selected):
            selected.append(Highlight(start, end, float(score), "High visual activity"))
        if len(selected) == count:
            break
    return sorted(selected, key=lambda item: item.start)


def detect_highlights(video_path: str | Path, count: int = 3, clip_seconds: int = 18) -> list[Highlight]:
    """Score sampled frames by motion; gracefully falls back to evenly spaced clips."""
    duration = probe_duration(video_path)
    if duration <= 1:
        raise ValueError("The uploaded video is too short to create a reel.")

    capture = cv2.VideoCapture(str(video_path))
    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    sample_every = max(int(fps * 1.5), 1)
    previous: np.ndarray | None = None
    candidates: list[tuple[float, float]] = []
    index = 0
    max_samples = 450
    step = max(sample_every, int(frame_count / max_samples) if frame_count else sample_every)
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if index % step == 0:
                gray = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (160, 90))
                if previous is not None:
                    motion = float(np.mean(cv2.absdiff(gray, previous)))
                    candidates.append((motion, index / fps))
                previous = gray
            index += 1
    finally:
        capture.release()

    found = _pick_non_overlapping(candidates, count, clip_seconds)
    if len(found) < count:
        latest_start = max(0.0, duration - clip_seconds)
        positions = np.linspace(0.0, latest_start, count).tolist()
        found = [Highlight(float(start), min(duration, float(start) + clip_seconds), 0.0, "Evenly sampled for review") for start in positions]
    return found
