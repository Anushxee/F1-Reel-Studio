import streamlit as st


#from moviepy import VideoFileClip
from moviepy.editor import VideoFileClip

clip = VideoFileClip("your_test_video.mp4")
subclip = clip.subclip(0, 5)
subclip.write_videofile("test_output.mp4")

st.title("🔐 Secrets Test")
st.write("OpenAI key:", st.secrets["OPENAI_API_KEY"])
