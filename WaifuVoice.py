import translators.server as tss
import requests
import speech_recognition as sr
import httpcore

class AudioToText:
    def __init__(self, audio_file, debug):
        self.audio_file = audio_file
        self.recognizer = sr.Recognizer()
        self.debug = debug

    def convert(self):
        try:
            with sr.AudioFile(self.audio_file) as audio:
                audio_data = self.recognizer.record(audio)
            text = self.recognizer.recognize_google(audio_data, language='en-EN')
            print(f"[Success] You say: {text}")
            return text
        except Exception as e:
            if self.debug == "y":
                print(e)
            return None


class MicToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def convert(self):
        try:
            with sr.Microphone() as audio:
                print("Speak now...")
                audio_data = self.recognizer.listen(audio)
                print(f"Received audio data: {audio_data}")
            text = self.recognizer.recognize_google(audio_data, language='en-EN')
            print(f"[Success] You say: {text}")
            return text
        except:
            return None


class TextTranslator:
    def __init__(self, text):
        self.text = text

    def translate(self, source, target):
        try:
            translated_text = tss.google(self.text, source, target)
            print(f"[Success] Translated: {translated_text}")
            return translated_text
        except:
            return None


import time

class TextToSpeech:
    def __init__(self, text):
        self.text = text

    def generate_audio(self, speaker_id=4):
        try:
            url = f"https://api.tts.quest/v3/voicevox/synthesis?text={self.text}&speaker={speaker_id}"
            response = requests.get(url).json()
            print(f"Text-to-Speech API Response: {response}")
            # time.sleep(20)
            if response.get("success", False):
                audio_url = response["wavDownloadUrl"]
                print(audio_url)

                return audio_url
            else:
                print("Failed to generate audio URL.")
                return None
        except Exception as e:
            print(f"Error during audio generation: {e}")
            return None


    # def save_audio(self, audio_url, file_name, max_retries=3, retry_interval=5):
    #     for attempt in range(1, max_retries + 1):
    #         try:
    #             audio_content = requests.get(audio_url).content
    #             with open(file_name, "wb") as file:
    #                 file.write(audio_content)
    #             return True
    #         except httpcore._exceptions.ReadTimeout as e:
    #             print(f"Error during audio saving (Attempt {attempt}/{max_retries}): {e}")
    #             if attempt < max_retries:
    #                 print(f"Retrying in {retry_interval} seconds...")
    #                 time.sleep(retry_interval)
    #     print(f"Failed to save audio after {max_retries} attempts.")
    #     return False

    def save_audio(self, audio_url, file_name):
        try:
            audio_content = requests.get(audio_url).content
            with open(file_name, "wb") as file:
                file.write(audio_content)
            return True
        except:
            return False


