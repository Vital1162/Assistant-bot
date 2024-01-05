import httpcore
import tkinter as tk
import time
import random
from random import randint
from win32api import GetMonitorInfo, MonitorFromPoint
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from threading import Thread
import threading
import os
from WaifuVoice import TextToSpeech,TextTranslator
from pydub import AudioSegment
# import audiosegment
from pydub.playback import play
import requests
import google.generativeai as genai
from googletrans import Translator
import sys
# from pydub import AudioSegment
from PIL import Image, ImageTk
from tkinter import scrolledtext
import pygetwindow as gw
import json
genai.configure(api_key="AIzaSyAqNmllczUTlKBq7GbXCDe5NpiIR2hVETU")




# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  }
]

model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

desc = "You are my voice assistant name Paimon. No matter what you responsed to me only must below 100 words.\n "
monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
work_area = monitor_info.get('Work')
screen_width = work_area[2]
work_height = work_area[3]



class Paimon:
    def __init__(self):
        self.window = tk.Tk()
        script_directory = os.path.dirname(os.path.abspath(__file__))
        self.norm = [ImageTk.PhotoImage(Image.open(os.path.join(script_directory, f'assets_2/pm_{i}.png'))) for i in range(24)]
        self.audio_length = 0

        # Load norm and listen images
        self.listen = [tk.PhotoImage(file=os.path.join(script_directory, 'assets_2/listen.png'))]

        # Set initial state to norm
        self.state = "norm"
        self.frame_index = 0
        self.is_speaking = False
        self.x = int(screen_width*0.92)
        self.y = work_height - 128

        self.frame = self.norm[0]  # Set initial frame to the first norm frame

        self.label = tk.Label(self.window, bd=0, bg='black')
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.wm_attributes('-transparentcolor', 'black')
        
        
        self.conversation_history = []
        self.conversation_file_path = os.path.join(os.path.dirname(__file__), "conversation_history.txt")
        # Create the conversation_history.txt file if it doesn't exist
        # Load existing conversation history from file if it exists
        if os.path.exists(self.conversation_file_path):
            with open(self.conversation_file_path, "r", encoding="utf-8") as file:
                self.conversation_history = [line.strip() for line in file.readlines()]
        else:
            self.conversation_history = []
        # Create a new window for displaying spoken text
        self.text_window = tk.Toplevel()
        # Set the position of the text window close to the Paimon window
        text_window_x = self.x  - 200# Adjust this value as needed
        text_window_y = self.y - 130

        self.text_window.geometry(f'300x100+{text_window_x}+{text_window_y}')
        self.text_window.title('Response')

        # Create a scrolled text widget for displaying spoken text
        self.text_label = scrolledtext.ScrolledText(self.text_window, wrap=tk.WORD, width=30, height=5)
        self.text_label.pack(expand=True, fill='both')
        self.text_label.insert(tk.END, "Wait for responsed...")


        self.random_speech_cooldown = 0
        self.active_windown_cooldown = 0

        # Bind mouse click event on the cat image
        self.label.bind("<Button-1>", self.toggle_listening)

        self.label.pack()

        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.window.after(1, self.update)
   
        self.window.mainloop()

    def toggle_listening(self, event):
        # Check if the current state is "listen" and ignore the click event
        if self.state == "listen":
            return

        # Toggle the listening state when the cat image is clicked
        if self.state == "norm":
            self.state = "listen"
            self.is_speaking = False

        else:
            self.state = "norm"

        if self.state == "listen":
            threading.Thread(target=self.voice_assistant).start()

            
    def voice_assistant(self):
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=5)
                command = self.recognizer.recognize_google(audio).lower()
                print(command)
                command = f"Our last conservation {self.conversation_history[-5:]} "+ command 
                # Append the command to the conversation history
                self.conversation_history.append(f"User: {command}")

                if "hello" in command:
                    self.speak("こんにちは！どんな御用でしょうか？")
                    # Append the response to the conversation history
                    self.conversation_history.append("Paimon: Hello! how can i help you?")
                elif "bye" in command:
                    self.speak("さようなら!")
                    self.window.destroy()
                    sys.exit()
                elif "open chrome" in command:
                    self.speak("はい、Chrome を開いてみます")
                    os.system("start chrome")
                    self.conversation_history.append("Paimon: OK, I'll open Chrome.")
                elif "search" in command and "google" in command:
                    search_query = command.replace("search", "").replace("google", "").strip()
                    self.speak(f"わかりました、マスター、Google で {search_query} を検索します")
                    os.system(f"start chrome https://www.google.com/search?q={search_query}")
                    self.conversation_history.append(f"Paimon: Okay, Master, search for {search_query} in Google.")
                else:
                    response = model.generate_content(str(desc + command))
                    print(response.text)
                    translator = Translator()
                    translated_response = self.translate_with_retry(translator, response)
                    print(translated_response)
                    self.speak(f"はい {translated_response}")
                    # Append the response to the conversation history
                    self.conversation_history.append(f"Paimon: はい {response.text}")
                     # Save conversation history to file
                    
                self.save_conversation_to_file()
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio.")
     
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
      
        except sr.WaitTimeoutError:
            print("Listening timed out. Please try again.")
       

        self.state = "norm"
        self.random_speech_cooldown = time.time() + 30


        

    def save_conversation_to_file(self):
        with open(self.conversation_file_path, "w", encoding="utf-8") as file:
            for line in self.conversation_history:
                file.write(line + "\n")

    def translate_with_retry(self, translator, response, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                translated_response = translator.translate(response.text, dest='ja').text
                return translated_response
            except httpcore._exceptions.ReadTimeout:
                print("Translation timed out. Retrying...")
                retries += 1

        print("Max retries reached. Unable to translate.")
        return ""


    def translate_response(self, response):
        translator = Translator()
        translated_response = translator.translate(response.text, dest='ja')
        return translated_response.text


    # def speak(self, text):
    
    #     text_to_speech = TextToSpeech(text)
    #     audio_url = text_to_speech.generate_audio()
    #     if audio_url:
    #         # Save the audio file using a unique filename with a WAV extension
    #         # timestamp = int(time.time())
    #         # unique_filename = f"output_{timestamp}.wav"
    #         unique_filename = "output.wav"
    #         unique_file_path = os.path.join(os.path.dirname(__file__), unique_filename)
    #         print(unique_file_path)
    #         if text_to_speech.save_audio(audio_url, unique_file_path):
    #             try:
    #                 # Use pydub to load and play the audio
    #                 audio = AudioSegment.from_file(unique_file_path,"wav")
                    
    #                 play(audio)
    #                 self.text_label.delete(1.0, tk.END)
    #                 old_text = Translator().translate(text,'en').text
    #                 self.text_label.insert(tk.END, old_text)
                   
                 

    #             except Exception as e:
    #                 print(f"Error during audio playback: {e}")
    #         else:
    #             print("[Failed] Failed to generate audio")
    #     else:
    #         print("[Failed] Failed to generate audio URL")
            
    def speak(self, text):
        retry_count = 0

        while retry_count < 10:
            text_to_speech = TextToSpeech(text)
            audio_url = text_to_speech.generate_audio()

            if audio_url:
                # Save the audio file using a unique filename with a WAV extension
                unique_filename = "output.wav"
                unique_file_path = os.path.join(os.path.dirname(__file__), unique_filename)

                if text_to_speech.save_audio(audio_url, unique_file_path):
                    try:
                        # Use pydub to load and play the audio
                        audio = AudioSegment.from_file(unique_file_path, format="wav")
                        play(audio)
                        self.text_label.delete(1.0, tk.END)
                        old_text = Translator().translate(text, 'en').text
                        self.text_label.insert(tk.END, old_text)
                        break  # Break out of the loop if playback is successful
                    except Exception as e:
                        print(f"Error during audio playback (Attempt {retry_count + 1}): {e}")
                        retry_count += 1
                        time.sleep(5)
                        if retry_count == 10:
                            print("Max retries reached. Unable to play audio.")
                            break
                else:
                    print("[Failed] Failed to generate audio")
                    time.sleep(5)
            else:
                print("[Failed] Failed to generate audio URL")
                time.sleep(5)



    def update(self):
        if self.state == "norm":
            self.frame = self.norm[self.frame_index]
            self.frame_index = (self.frame_index + 1) % len(self.norm)
            if not self.is_speaking and random.randint(1, 100) <= 5 and time.time() > self.random_speech_cooldown:
                self.is_speaking= True
                threading.Thread(target=self.speak_random).start()
                self.random_speech_cooldown = time.time() + random.randint(120, 360)
        elif self.state == "listen":
            self.frame = self.listen[0]

        self.window.geometry('112x128+' + str(self.x) + '+' + str(self.y))
        self.label.configure(image=self.frame)
        self.window.after(100, self.update)


    def speak_random(self):
        # print(self.conversation_history)
        response = model.generate_content(f"From our last converstation {self.conversation_history[-5:]} .talk 1 senseless sentence for me, or you can tease me or compliment me or say cute thing for me. In general, just choose one ")
        print(response.text)
        translator = Translator()
        translated_response = translator.translate(response.text,'ja').text
        print(translated_response)
        # Use text-to-speech to speak the random phrase
        self.speak(translated_response)
        self.conversation_history.append(f"Paimon:{response.text}")
        
        self.save_conversation_to_file()
        self.is_speaking = False


if __name__ == "__main__":
    ket = Paimon()