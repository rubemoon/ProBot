from gtts import gTTS
from playsound import playsound
import os

def test_gtts():
    try:
        # Generate audio file
        print("[DEBUG] Generating test audio...")
        tts = gTTS("This is a test of the gTTS system.")
        tts.save("test_audio.mp3")
        print("[DEBUG] Audio file generated successfully.")

        # Play the audio file
        print("[DEBUG] Playing test audio...")
        playsound("test_audio.mp3")
        print("[DEBUG] Audio playback completed.")

        # Clean up the audio file
        os.remove("test_audio.mp3")
        print("[DEBUG] Test audio file removed.")
    except Exception as e:
        print(f"[ERROR] gTTS test failed: {e}")

if __name__ == "__main__":
    test_gtts()

