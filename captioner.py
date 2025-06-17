import os
import subprocess

def extract_highlights(video_path, highlights, output_dir='output/highlights'):
    """
    Extracts subclips from the video at the given highlight intervals using ffmpeg.
    Args:
        video_path: Path to the input video.
        highlights: List of (start, end) tuples in seconds.
        output_dir: Directory to save highlight clips.
    Returns:
        List of file paths to the created highlight clips.
    """
    os.makedirs(output_dir, exist_ok=True)
    highlight_paths = []
    for i, (start, end) in enumerate(highlights):
        out_path = os.path.join(output_dir, f"highlight_{i+1}.mp4")
        # ffmpeg requires start and duration, not end
        duration = end - start
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-i', video_path,
            '-ss', str(start),
            '-t', str(duration),
            '-c', 'copy',
            out_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
        highlight_paths.append(out_path)
    return highlight_paths

def get_highlight_times(video_path):
    """
    Insert your highlight detection logic here.
    For now, this returns two demo highlights (10-20s, 30-40s).
    """
    # TODO: replace this with real logic (e.g., detect high audio, scene changes, etc.)
    return [(10, 20), (30, 40)]