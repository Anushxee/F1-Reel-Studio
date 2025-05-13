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

f1-reels-generator/
├── main.py
├── agents/
│   ├── downloader.py
│   ├── clip_extractor.py
│   ├── captioner.py
│   ├── music_suggester.py
│   └── merger.py
├── utils/
│   ├── video_utils.py
│   ├── audio_utils.py
│   └── helpers.py
├── static/
│   └── music/
├── output/
│   └── final_reels/
├── requirements.txt
└── README.md
