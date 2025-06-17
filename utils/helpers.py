import os
import datetime

def create_output_filename(prefix="clip", extension=".mp4"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{timestamp}{extension}"

def ensure_dirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)
