from pydub import AudioSegment
import numpy as np

def get_audio_volume(path):
    try:
        audio = AudioSegment.from_file(path)
        samples = np.array(audio.get_array_of_samples())
        volume = np.linalg.norm(samples)
        return volume
    except Exception as e:
        print("Error calculating volume:", e)
        return 0
