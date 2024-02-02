import requests
from pydub import AudioSegment
from pydub.playback import play
import io
import time

####################################
#        NO API REQUIREMENT        #
####################################
class TextToSpeech:
    def __init__(self, text):
        self.text = text
        self.audio = None

    def generate_audio(self, speaker_id=20):
        try:
            url = f"https://api.tts.quest/v3/voicevox/synthesis?text={self.text}&speaker={speaker_id}"
            response = requests.get(url).json()
            print(f"Text-to-Speech API Response: {response}")

            if response.get("success", False):
                audio_url = response["mp3StreamingUrl"]  # Change to wavStreamingUrl
                print(audio_url)

                # Download the audio file
                audio_content = requests.get(audio_url).content

                # Create an AudioSegment from the content
                self.audio = AudioSegment.from_mp3(io.BytesIO(audio_content))

                return True
            else:
                print("Failed to generate audio URL.")
                return False
        except Exception as e:
            print(f"Error during audio generation: {e}")
            return False

    def play_audio(self):
        if self.audio:
            play(self.audio)
        else:
            print("No audio available to play. Please generate audio first using generate_audio method.")
