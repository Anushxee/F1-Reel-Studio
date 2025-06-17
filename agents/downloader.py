import os
import yt_dlp

def download_video(url, output_dir='output'):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'downloaded.mp4')
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': output_path,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path
