# F1 Reel Studio

An explainable local-first Streamlit app for finding active moments in video footage and exporting vertical 1080×1920 MP4 reels.

## Run it

1. Install FFmpeg and make `ffmpeg` and `ffprobe` available on your PATH.
2. Create and activate a Python 3.10+ virtual environment.
3. Run `pip install -r requirements.txt`.
4. Optional: set `OPENAI_API_KEY` to refine the publishing copy.
5. Start with `streamlit run app.py`.

## Deploy a public demo

This repository includes a production Docker image and is ready for a Streamlit-compatible container host. Render is a good fit for a recruiter demo because it can build directly from the `Dockerfile`, deploy from a connected Git repository, and give the service an HTTPS `onrender.com` URL.

1. Push this project to a private or public GitHub repository. Confirm that `.streamlit/secrets.toml` is **not** committed.
2. In Render, create **New → Web Service**, connect the repository, and select the Docker runtime. Render builds the included `Dockerfile` automatically.
3. Select an instance with enough memory for OpenCV and Whisper. The first Whisper transcription can download the selected model, so a paid always-on instance is recommended for a public demonstration.
4. Set these environment variables in the Render dashboard:

   - `OPENAI_API_KEY` — optional; enables AI-refined publishing copy.
   - `WHISPER_MODEL=base` — optional; this is the default and balances speed with accuracy.
   - `PORT=10000` — optional; the container already defaults to it.

5. Deploy and use the generated HTTPS URL in your portfolio. Render requires public services to bind to `0.0.0.0` and its `PORT`; the Docker command already does both.

The deployed app has a 300 MB upload limit and uses temporary container storage. That is appropriate for an interactive demo: the creator uploads a clip, downloads the finished reel, and the host can discard temporary files after a restart. Do not present it as a multi-user production SaaS yet.

### Before accepting public users

Add authentication, rate limiting, virus/media validation, object storage for uploads/exports, a background job queue, a database, and deletion/retention controls. Those upgrades turn this into a scalable product rather than a portfolio demo.

## What it does

- Scores sampled frames by visual motion and presents non-overlapping highlight candidates.
- Lets you choose a candidate and provide a concise, accurate caption.
- Optionally transcribes the uploaded footage locally with Whisper (the model downloads on first use).
- Offers three reusable visual templates, with a custom headline and creator handle.
- Renders Whisper word-timed animated captions or a creator-edited static caption.
- Creates a single branded highlight or a multi-clip vertical montage.
- Exports a matching 1080×1920 JPEG Reel cover with the same headline and handle.
- Renders H.264/AAC, 1080×1920, 30fps MP4 with captions in Instagram's safe lower area.
- Creates a download-ready video plus caption and hashtag copy. OpenAI is optional; it has a useful offline fallback.

## Important publishing notes

Use footage you own or have licensed. F1 broadcasts, team marks, driver likenesses, and commercial songs can require permissions; this app deliberately does not download third-party videos or add unlicensed music. Select licensed audio in Instagram's library or use a royalty-free licence suitable for commercial social media use. Earnings and reach also depend on platform eligibility and content rights, so no tool can guarantee monetisation.
