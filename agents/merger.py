from moviepy.editor import VideoFileClip, AudioFileClip
import os

def merge_clip_with_music(clip_path, music_path, clip_index, output_dir='output/final_reels'):
    os.makedirs(output_dir, exist_ok=True)
    video = VideoFileClip(clip_path)
    music = AudioFileClip(music_path).subclip(0, video.duration).volumex(0.6)

    final = video.set_audio(music)
    output_path = os.path.join(output_dir, f"reel_{clip_index}.mp4")
    final.write_videofile(output_path, codec="libx264")
    return output_path
