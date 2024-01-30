import requests
from pydub import AudioSegment
from pydub.playback import play
import io
import time
#faster response with api
class TextToSpeech:
    def __init__(self, text):
        self.text = text

    def play_audio(self,speaker_id=20):
        try:
            url = f"https://deprecatedapis.tts.quest/v2/voicevox/audio/?key=y650753772948-c&speaker={speaker_id}&pitch=0&intonationScale=1&speed=1&text={self.text}"

            audio_content = requests.get(url).content
            # Load the WAV file using AudioSegment
            audio_data = AudioSegment.from_wav(io.BytesIO(audio_content))

            play(audio_data)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching or playing audio: {e}")