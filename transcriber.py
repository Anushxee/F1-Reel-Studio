import os
import whisper

def transcribe_clip(clip_path):
    model = whisper.load_model("base")
    result = model.transcribe(clip_path)
    return result['text']
