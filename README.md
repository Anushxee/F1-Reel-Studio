# F1_AI_Reels_Generator

☘️AI-Powered Instagram Reel Generator for F1 Highlights

Developed a LangChain-based agentic application that automatically processes F1 race videos to extract highlights, suggests trending music and hashtags using OpenAI’s GPT-4, and produces Instagram-ready Reels. Implemented video/audio processing, AI-based content creation, and an end-to-end media pipeline.

☘️Initial Ideas:
→ Automated detection of interesting video segments from uploaded race videos/URLs

→ Integration with GPT-4 for content analysis

→ Utilizes FFmpeg and OpenCV for video processing

→ Supports image and video editing

→ Generates Reels from simple text prompts☘


☘️Features/Uses:
☞ Takes F1 race media (YouTube links, uploads, etc.)

☞ Extracts highlights (e.g. overtakes, crashes)

☞ Suggests music + generates hashtags/captions

☞ Outputs an Instagram-ready reel


☘️Folder Structure:

F1_AI_Reels/
├── .devcontainer/
├── .streamlit/
│   └── secrets.toml
├── .venv/
├── __pycache__/
├── agents/
│   ├── downloader.py
│   ├── merger.py
│   └── spotify_trending.py
├── output/
│   └── (highlighted clips & final reels go here)
├── temp/
├── utils/
│   ├── video_utils.py
│   └── audio_utils.py
├── app.py                     # Main Streamlit app
├── captioner.py              # Highlight extractor
├── hashtag_generator.py      # Hashtag suggester
├── index.html                
├── main.py                   
├── music_recommender.py      # Music suggestion logic (Spotify)
├── README.md
├── requirements.txt
└── test_app.py               # Optional test script

