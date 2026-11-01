from __future__ import annotations

import os
from pathlib import Path
import tempfile
import hashlib

import streamlit as st

from agents.highlights import detect_highlights
from agents.metadata import create_metadata
from agents.reel_builder import THEMES, render_cover, render_montage, render_reel, write_ass_overlay, write_srt
from agents.transcription import transcribe_with_cues

api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

st.set_page_config(page_title="F1 Reel Studio", page_icon="🏁", layout="wide")
st.title("🏁 F1 Reel Studio")
st.caption("Turn footage you own or are licensed to use into a vertical, Instagram-ready highlight reel.")

with st.sidebar:
    st.header("Reel settings")
    clip_count = st.slider("Highlights to review", 1, 5, 3)
    clip_seconds = st.slider("Length per reel", 8, 45, 18)
    topic = st.text_input("Context", placeholder="e.g. Last-lap overtake at Monza")
    st.divider()
    st.subheader("Creator template")
    theme_name = st.selectbox("Visual style", list(THEMES), index=0)
    headline = st.text_input("Headline", placeholder="e.g. LAST-LAP CHAOS")
    brand_handle = st.text_input("Brand handle", value="@yourhandle")
    caption_mode = st.selectbox("Caption treatment", ["Word-timed (Whisper)", "Static caption", "No captions"])
    montage_mode = st.toggle("Create a multi-clip montage", value=False)
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
    montage_indices: list[int] = [index]
    if montage_mode:
        montage_indices = st.multiselect(
            "Clips to include in montage",
            range(len(labels)),
            default=list(range(min(3, len(labels)))),
            format_func=lambda item: labels[item],
            help="Montages use the selected branded template. Word-timed captions are exported with the selected single clip.",
        )
    caption_key = f"caption_{index}"
    caption_input_key = f"caption_input_{index}"
    cue_key = f"cues_{index}"
    if st.button("Transcribe selected moment with Whisper"):
        # Whisper accepts the source video. It is intentionally opt-in because the
        # first model download can take time and requires a network connection.
        with st.spinner("Transcribing locally with Whisper…"):
            try:
                transcript_text, cues = transcribe_with_cues(source, selected.start, selected.end - selected.start)
                st.session_state[caption_key] = transcript_text
                st.session_state[caption_input_key] = transcript_text
                st.session_state[cue_key] = cues
                st.success("Word timings are ready. Edit the text if you want a simpler static caption.")
            except Exception as exc:
                st.warning(str(exc))
    transcript = st.text_area(
        "Caption text (optional)",
        key=caption_input_key,
        placeholder="Add a short, accurate caption. Keep it concise for mobile viewing.",
    )
    render_label = "Render branded montage" if montage_mode else "Render branded Instagram Reel"
    if st.button(render_label, type="primary"):
        chosen_highlights = [highlights[item] for item in montage_indices] if montage_mode else [selected]
        if not chosen_highlights:
            st.error("Choose at least one clip for the montage.")
            st.stop()
        render_duration = sum(item.end - item.start for item in chosen_highlights) if montage_mode else selected.end - selected.start
        generated_headline = headline.strip() or topic.strip() or "F1 REEL"
        overlay_ass = write_ass_overlay(
            st.session_state.get(cue_key, []) if caption_mode == "Word-timed (Whisper)" and not montage_mode else [],
            render_duration,
            work_dir / f"overlay_{upload_id}_{index}.ass",
            generated_headline,
            brand_handle,
            theme_name,
        )
        srt = write_srt(transcript, selected.end - selected.start, work_dir / f"caption_{upload_id}_{index}.srt") if caption_mode == "Static caption" and not montage_mode else None
        final_path = work_dir / (f"f1_montage_{upload_id}.mp4" if montage_mode else f"f1_reel_{upload_id}_{index + 1}.mp4")
        cover_path = work_dir / (f"f1_montage_cover_{upload_id}.jpg" if montage_mode else f"f1_reel_cover_{upload_id}_{index + 1}.jpg")
        with st.spinner("Rendering 1080 × 1920 MP4…"):
            try:
                if montage_mode:
                    render_montage(source, chosen_highlights, final_path, overlay_ass)
                else:
                    render_reel(source, selected, final_path, srt, overlay_ass)
                render_cover(source, chosen_highlights[0], cover_path, overlay_ass)
                st.session_state.final_path = str(final_path)
                st.session_state.cover_path = str(cover_path)
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
    cover_path = st.session_state.get("cover_path")
    if cover_path and Path(cover_path).exists():
        st.subheader("Reel cover")
        st.image(cover_path, caption="Vertical cover image")
        with open(cover_path, "rb") as cover_file:
            st.download_button("Download cover image", cover_file, file_name="instagram-reel-cover.jpg", mime="image/jpeg")
    metadata = st.session_state.get("metadata", {})
    st.subheader("Publish pack")
    st.text_area("Caption", value=metadata.get("caption", ""), height=110)
    st.code(metadata.get("hashtags", ""), language=None)
    st.caption(metadata.get("music_note", ""))
