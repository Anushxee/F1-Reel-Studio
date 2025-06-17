from moviepy.editor import VideoFileClip

def get_video_duration(path):
    try:
        clip = VideoFileClip(path)
        return clip.duration
    except Exception as e:
        print("Error getting video duration:", e)
        return 0
