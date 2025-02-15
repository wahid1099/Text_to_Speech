from gtts import gTTS
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get absolute path of current file
AUDIO_DIR = "/app/static/audio"
def generate_audio(text, voice):
    os.makedirs(AUDIO_DIR, exist_ok=True)  # Ensure directory exists
    tld = "com.au" if voice == "male" else "com"

    tts = gTTS(text=text, lang="en", tld=tld)
    file_name = f"speech_{int(time.time())}.mp3"
    file_path = os.path.join(AUDIO_DIR, file_name)

    tts.save(file_path)  # Save audio properly
    return file_name

