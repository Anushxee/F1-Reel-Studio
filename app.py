from __future__ import annotations

import os
from pathlib import Path
import tempfile
import hashlib

import streamlit as st

from agents.highlights import detect_highlights
from agents.metadata import create_metadata
from agents.reel_builder import render_reel, write_srt
from agents.transcription import transcribe

api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

st.set_page_config(page_title="F1 Reel Studio", page_icon="🏁", layout="wide")
st.title("🏁 F1 Reel Studio")
st.caption("Turn footage you own or are licensed to use into a vertical, Instagram-ready highlight reel.")

with st.sidebar:
    st.header("Reel settings")
    clip_count = st.slider("Highlights to review", 1, 5, 3)
    clip_seconds = st.slider("Length per reel", 8, 45, 18)
    topic = st.text_input("Context", placeholder="e.g. Last-lap overtake at Monza")
    use_ai = st.toggle("Refine social copy with OpenAI", value=bool(api_key))

uploaded = st.file_uploader("Upload MP4, MOV, or MKV footage", type=["mp4", "mov", "mkv"])
if not uploaded:
    st.info("Use footage you created, own, or have permission to repurpose. Uploading a reel does not grant rights to Formula 1 broadcast footage or commercial music.")
    st.stop()

work_dir = Path(tempfile.gettempdir()) / "f1_reel_studio"
work_dir.mkdir(exist_ok=True)
upload_id = hashlib.sha256(uploaded.getbuffer()).hexdigest()[:12]
source = work_dir / f"source_{upload_id}_{uploaded.name}"
if not source.exists():
    source.write_bytes(uploaded.getbuffer())

if "highlights" not in st.session_state or st.session_state.get("source") != str(source):
    if st.button("Find the best moments", type="primary"):
        with st.spinner("Scanning visual activity in your footage…"):
            try:
                st.session_state.highlights = detect_highlights(source, clip_count, clip_seconds)
                st.session_state.source = str(source)
            except Exception as exc:
                st.error(f"Could not analyse this video: {exc}")

highlights = st.session_state.get("highlights", [])
if highlights:
    st.success(f"Found {len(highlights)} candidate moments. Select one and render it below.")
    labels = [f"Moment {i + 1}: {item.start:.1f}s–{item.end:.1f}s · {item.reason}" for i, item in enumerate(highlights)]
    index = st.radio("Candidate", range(len(labels)), format_func=lambda i: labels[i])
    selected = highlights[index]
    caption_key = f"caption_{index}"
    if st.button("Transcribe selected moment with Whisper"):
        # Whisper accepts the source video. It is intentionally opt-in because the
        # first model download can take time and requires a network connection.
        with st.spinner("Transcribing locally with Whisper…"):
            try:
                st.session_state[caption_key] = transcribe(source, selected.start, selected.end - selected.start)
                st.success("Transcript ready. Edit it down to the strongest line for the reel.")
            except Exception as exc:
                st.warning(str(exc))
    transcript = st.text_area(
        "Caption text (optional)",
        value=st.session_state.get(caption_key, ""),
        key=f"caption_input_{index}",
        placeholder="Add a short, accurate caption. Keep it concise for mobile viewing.",
    )
    if st.button("Render Instagram Reel", type="primary"):
        final_path = work_dir / f"f1_reel_{index + 1}.mp4"
        srt = write_srt(transcript, selected.end - selected.start, work_dir / "caption.srt")
        with st.spinner("Rendering 1080 × 1920 MP4…"):
            try:
                render_reel(source, selected, final_path, srt)
                st.session_state.final_path = str(final_path)
                st.session_state.metadata = create_metadata(transcript, topic, use_ai, api_key)
            except Exception as exc:
                st.error(f"Render failed: {exc}")

final_path = st.session_state.get("final_path")
if final_path and Path(final_path).exists():
    st.divider()
    st.subheader("Your finished reel")
    st.video(final_path)
    with open(final_path, "rb") as video_file:
        st.download_button("Download MP4", video_file, file_name="instagram-ready-f1-reel.mp4", mime="video/mp4")
    metadata = st.session_state.get("metadata", {})
    st.subheader("Publish pack")
    st.text_area("Caption", value=metadata.get("caption", ""), height=110)
    st.code(metadata.get("hashtags", ""), language=None)
    st.caption(metadata.get("music_note", ""))
