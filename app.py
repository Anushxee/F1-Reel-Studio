import streamlit as st
import whisper
import os
import subprocess
from captioner import extract_highlights, get_highlight_times

st.set_page_config(page_title="F1 AI Reels Generator", layout="centered")
st.title("🎥🏁 F1 AI Reels Generator")
st.subheader("Upload a race video")

uploaded_file = st.file_uploader("Upload Video", type=["mp4", "mov", "mkv", "mpeg4"])

def extract_audio_with_ffmpeg(video_path, audio_path):
    # Extract audio using ffmpeg
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite output file
        '-i', video_path,
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ar', '16000',
        '-ac', '1',
        audio_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)

if uploaded_file:
    with st.spinner("Processing video..."):
        input_path = os.path.join("temp", uploaded_file.name)
        os.makedirs("temp", exist_ok=True)
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        # You can customize get_highlight_times to implement your own logic
        highlights = get_highlight_times(input_path)
        # highlights should be a list of (start, end) tuples in seconds, e.g., [(10, 20), (30, 40)]
        highlight_paths = extract_highlights(input_path, highlights)

        st.success(f"Found {len(highlight_paths)} highlight(s)")

        # Load Whisper model
        model = whisper.load_model("base")

        for idx, clip_path in enumerate(highlight_paths):
            st.video(clip_path)
            audio_path = f"temp/temp_audio_{idx}.wav"
            extract_audio_with_ffmpeg(clip_path, audio_path)

            # Transcribe using Whisper
            result = model.transcribe(audio_path)
            st.markdown(f"**Clip {idx+1} Caption:** {result['text']}")

        st.success("Done! Transcriptions generated ✅")