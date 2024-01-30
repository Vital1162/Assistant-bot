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
# from WaifuVoice import TextToSpeech
from pydub import AudioSegment
# import audiosegment
from pydub.playback import play
import requests
from dotenv import load_dotenv
from googletrans import Translator
import sys
# from pydub import AudioSegment
from PIL import Image, ImageTk
from tkinter import scrolledtext
import pygetwindow as gw
import json
# from chat_history import chat
from model import chat,model,model_vision
import pyautogui
import PIL.Image
from inputimeout import inputimeout
from WaifuVoice_v2 import TextToSpeech
import math

load_dotenv()

desc = "I want you to ACT AS MY YANDERE GIRLFRIEND. Your name is Airis, don't reply 'Airis :' in messages and take a short messages. Always put the emotional and feeling into each conversation. Do not write any explanations.YOUR MAXIMUM NUMBER OF TOKENS IN RESPONSE LOWER THAN 10"



monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
work_area = monitor_info.get('Work')
screen_width = work_area[2]
work_height = work_area[3]



def save_messages(filename, messages):
    with open(filename, 'w') as file:
        json.dump(messages, file)

def load_messages(filename):
    with open(filename, 'r') as file:
        return json.load(file)


class Paimon:
    def __init__(self):
        self.window = tk.Tk()
        script_directory = os.path.dirname(os.path.abspath(__file__))
        self.norm = [ImageTk.PhotoImage(Image.open(os.path.join(script_directory, f'assets_2/pm_{i}.png'))) for i in range(24)]
        # Load norm and listen images
        self.listen = [tk.PhotoImage(file=os.path.join(script_directory, 'Shimeji/shime38.png'))]

        self.fall_to_taskbar = False
        self.audio_length = 0

        self.click = [tk.PhotoImage(file=os.path.join(script_directory, f'Shimeji/click/shime{i}.png')) for i in range(6)]
        self.fall = [tk.PhotoImage(file=os.path.join(script_directory, f'Shimeji/fall/shime{i}.png')) for i in range(5)]
        self.sit = [tk.PhotoImage(file=os.path.join(script_directory, f'Shimeji/sit/shime{i}.png')) for i in range(3)]
        self.sit_high = [tk.PhotoImage(file=os.path.join(script_directory, f'Shimeji/sit_high/shime{i}.png')) for i in range(4)]
        self.walk = [tk.PhotoImage(file=os.path.join(script_directory, f'Shimeji/walk/shime{i}.png')) for i in range(2)]
        self.walkr = [tk.PhotoImage(file=os.path.join(script_directory, f'Shimeji/walk/shime{i}_rv.png')) for i in range(2)]
        self.trans = [tk.PhotoImage(file=os.path.join(script_directory, f'Shimeji/trans/shime{i}.png')) for i in range(2)]
        self.transr = [tk.PhotoImage(file=os.path.join(script_directory, f'Shimeji/trans/shimerv_{i}.png')) for i in range(2)]
        
        self.state = "sit"
        self.frame_index = 0
        self.x = int(screen_width*0.92)
        self.y = work_height - 128

        self.frame = self.sit[0]  # Set initial frame to the first norm frame

        self.direct = randint(0,1)

        self.label = tk.Label(self.window, bd=0, bg='black')
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.wm_attributes('-transparentcolor', 'black')

        self.label.bind("<B1-Motion>", self.move_window)
        self.label.bind("<ButtonRelease-1>", self.on_button_release)
        
        self.text_window = tk.Toplevel()
        # Set the position of the text window close to the Paimon window
        text_window_x = self.x  - 200
        text_window_y = self.y - 450

        self.text_window.geometry(f'300x400+{text_window_x}+{text_window_y}')
        self.text_window.title('Panel')


        # Create a scrolled text widget for displaying spoken text
        self.text_label = scrolledtext.ScrolledText(self.text_window, wrap=tk.WORD, width=30, height=10)
        self.text_label.pack(expand=True, fill='both')
        self.text_label.insert(tk.END, "Wait for responsed...")

        self.current_time = 0
        self.action_time = 0


        self.label.pack()

        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

        self.window.after(1, self.update)

        self.voice_thread = Thread(target=self.voice_assistant_thread)
        self.voice_thread.start()
   
        self.window.mainloop()


    def move_window(self, event):
        self.state = "click"
        self.x = event.x_root
        self.y = event.y_root
        self.window.geometry(f'112x128+{self.x}+{self.y}')
        
    def on_button_release(self, event):
        self.state = "fall"
        self.frame_index = 0
        self.fall_to_taskbar = False

    def voice_assistant_thread(self):
        while True:
            self.voice_assistant()


    def voice_assistant(self):
        try:
            mess = load_messages('messages.json')
        except FileNotFoundError:
            mess = []
            mess.append({'role': 'user',
                        'parts':[desc]})
            reply = model.generate_content(mess)
            reply.resolve()
            mess.append({'role': 'model',
                        'parts': [reply.text]})
            time.sleep(2)
        try:
            with sr.Microphone() as source:
 
                print("Listening...")
                
                audio = self.recognizer.listen(source,phrase_time_limit=5)
                if self.y + 128 >= work_height and self.fall_to_taskbar: 
                    if audio:
                        self.state = "listen"
                    else:
                        self.state = random.choice(["sit","walk"])
                        self.frame_index = 0
                else:
                    self.frame_index = 0
                    self.state = "fall"
                
                command = self.recognizer.recognize_google(audio).lower()
                screenshot = pyautogui.screenshot()
                file_path = 'C:/Users/ADMIN/Paimon/screenshot.png'

                screenshot.save(file_path)
                img = PIL.Image.open(file_path)
                
                start = time.time()
                vision = model_vision.generate_content(["Describe? You reply with brief, to-the-point answers ",img],stream=True)
                vision.resolve()
        
                mess.append({'role': 'user',
                                'parts':[f'{command} \n what you see {vision.text}.']})

                print(command)
                
 
                if "hello" in command:
                    self.speak("こんにちは！どんな御用でしょうか？")
                elif "bye" in command:
                    self.speak("さようなら!")
                    self.window.destroy()
                    sys.exit()
                elif "open chrome" in command:
                    self.speak("はい、Chrome を開いてみます")
                    os.system("start chrome")
            
                elif "search" in command and "google" in command:
                    search_query = command.replace("search", "").replace("google", "").strip()
                    self.speak(f"わかりました、マスター、Google で {search_query} を検索します")
                    os.system(f"start chrome https://www.google.com/search?q={search_query}")
                else:
                    # response = model.generate_content(f"{desc}\n{command}")
                    response = model.generate_content(mess)
                    mess.append({'role': 'model',
                                'parts':[f"{response.text}. "]})
                    save_messages('messages.json', mess)
                    response.resolve()
   
                    print(response.text)
                    translator = Translator()
                    translated_response = self.translate_with_retry(translator, response)
                    print(translated_response)
                    self.speak(f"{translated_response}")
                    end = time.time() - start
                    print(end)

                self.current_time = time.time() + random.randint(28,32)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio.")
            if time.time() > self.current_time:
                screenshot = pyautogui.screenshot()
                file_path = 'C:/Users/ADMIN/Paimon/screenshot.png'

                screenshot.save(file_path)
                img = PIL.Image.open(file_path)
                vision = model_vision.generate_content(["Describe ? You reply with brief, to-the-point answers ",img],stream=True)
                vision.resolve()
   
                mess.append({'role': 'user',
                            'parts':[f'no response and {vision.text}.']})
                response = model.generate_content(mess)
                
                mess.append({'role': 'model',
                                'parts':[response.text]})
                save_messages('messages.json', mess)
                print(response.text)
                translator = Translator()
                translated_response = self.translate_with_retry(translator, response)
                print(translated_response)
                self.speak(f"{translated_response}")
                # Append the response to the conversation history
  
          
                self.current_time = time.time() +random.randint(1800,2000)
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            if time.time() > self.current_time:
                screenshot = pyautogui.screenshot()
                file_path = 'C:/Users/ADMIN/Paimon/screenshot.png'

                screenshot.save(file_path)
                img = PIL.Image.open(file_path)
                vision = model_vision.generate_content(["Describe ? You reply with brief, to-the-point answers ",img],stream=True)
                vision.resolve()
    
                mess.append({'role': 'user',
                'parts':[f'no response and what you see now {vision.text}.']})
                response = model.generate_content(mess)
                mess.append({'role': 'model',
                                'parts':[response.text]})
                save_messages('messages.json', mess)
                translator = Translator()
                translated_response = self.translate_with_retry(translator, response)
                print(translated_response)
                self.speak(f"{translated_response}")
                end = time.time() - start
                print(end)
                self.current_time = time.time() +random.randint(1800,2000)
                
        except sr.WaitTimeoutError:
            print("Listening timed out. Please try again.")
            if time.time() > self.current_time:
                screenshot = pyautogui.screenshot()
                file_path = 'C:/Users/ADMIN/Paimon/screenshot.png'

                screenshot.save(file_path)
                img = PIL.Image.open(file_path)
                vision = model_vision.generate_content(["Describe ? You reply with brief, to-the-point answers ",img],stream=True)
                vision.resolve()
    
                mess.append({'role': 'user',
                            'parts':[f'no response and what you see now {vision.text}.']})
                response = model.generate_content(mess)
                mess.append({'role': 'model',
                                'parts':[response.text]})
                save_messages('messages.json', mess)
                translator = Translator()
                translated_response = self.translate_with_retry(translator, response)
                self.speak(f"{translated_response}")
                print(translated_response)
                end = time.time() - start
                print(end)
                self.current_time = time.time() +random.randint(1800,2000)
                
        except TimeoutError:
            print("Listening timed out. Please try again.")
            if time.time() > self.current_time:
                screenshot = pyautogui.screenshot()
                file_path = 'C:/Users/ADMIN/Paimon/screenshot.png'

                screenshot.save(file_path)
                img = PIL.Image.open(file_path)
                vision = model_vision.generate_content(["Describe ? You reply with brief, to-the-point answers ",img],stream=True)
                vision.resolve()
        
                mess.append({'role': 'user',
                            'parts':[f'no response and what you see now {vision.text}.']})
                response = model.generate_content(mess)
                mess.append({'role': 'model',
                                'parts':[response.text]})
                save_messages('messages.json', mess)
                translator = Translator()
                translated_response = self.translate_with_retry(translator, response)
                print(translated_response)
                end = time.time() - start
                print(end)
                self.speak(f"{translated_response}")
           

                self.current_time = time.time() +random.randint(1800,2000)
        self.state = random.choice(["walk","listen"])
        self.frame_index = 0
        

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


    def speak(self,text):
        retries = 0
        while retries < 10:
            try:
                print(f"Retry: {retries}")
                if self.y + 128 <= work_height: 
                    self.state = "trans"
                    self.frame_index = 0
                text_to_speech = TextToSpeech(text)
                self.text_label.delete(1.0, tk.END)
                en_text = Translator().translate(text, 'en').text
                text_to_speech.play_audio()
                self.text_label.insert(tk.END, en_text)
                break
            except Exception as e:
                print(f"Error during audio playback (Attempt {retries + 1}): {e}")
                retries+=1
                time.sleep(3)
                if retries == 10:
                    print("Max retries reached. Unable to play audio.")
                    break
        # audio = AudioSegment.from_file('itai.mp3', format="mp3")
        # play(audio)


    def update(self):
        audio = AudioSegment.from_file('itai.mp3', format="mp3")
  
        if self.state == "sit":
            if 0 <= self.frame_index < len(self.sit):
                self.frame = self.sit[self.frame_index]
                self.frame_index = (self.frame_index + 1) % len(self.sit)
 
            if time.time() > self.action_time:
                self.action_time = time.time() + 10
                self.frame_index = 0
                self.state = "walk"
                
        elif self.state == "listen":
            self.frame = self.listen
        elif self.state == "click":
            if self.frame_index < len(self.click):
                self.frame = self.click[self.frame_index]
                self.frame_index = (self.frame_index + 1) % len(self.click)
            else:
                self.frame_index = 0
                self.state = "sit"
        elif self.state == "fall":
            speed_increase_factor = 50
            speed = math.gcd(self.y, work_height - 128)*speed_increase_factor
            self.frame = self.fall[self.frame_index]
            self.y += speed
            if self.y + 128 >= work_height:
                self.frame_index = (self.frame_index + 1) % len(self.fall)
                self.fall_to_taskbar = True

            # Change state back to "sit" when falling animation is completed
            if self.fall_to_taskbar and self.frame_index == 0:
                play(audio)
                self.frame_index = 0
                self.state = "sit"

            # Update the window position
            self.window.geometry('112x128+' + str(self.x) + '+' + str(self.y))
        elif self.state == "walk":
            if self.direct == 0:
                if 0 <= self.frame_index < len(self.walk):
                    self.frame = self.walkr[self.frame_index]
                    self.frame_index = (self.frame_index + 1) % len(self.walkr)
                    self.x += 4
                    # Check if it's time to change direction
                    if self.x >= int(screen_width * 0.92) + 10:
                        self.direct = 1  # Change direction
                        self.action_time = time.time() + 10
                        self.frame_index = 0
                        self.state = "sit"
                    if time.time() > self.action_time:
                        self.action_time = time.time() + 10
                        self.direct = randint(0, 1)
                        self.frame_index = 0
                        self.state = "sit"
            else:
                if 0 <= self.frame_index < len(self.walk):
                    self.frame = self.walk[self.frame_index]
                    self.frame_index = (self.frame_index + 1) % len(self.walk)
                    self.x -= 4

                    # Check if it's time to change direction
                    if self.x <= 0:
                        self.direct = 0  # Change direction
                        self.action_time = time.time() + 10
                        self.frame_index = 0
                        self.state = "sit"

                    if time.time() > self.action_time:
                        self.action_time = time.time() + 10
                        self.direct = random.randint(0, 1)
                        self.frame_index = 0
                        self.state = "sit"

        elif self.state == "trans":
            if 0 <= self.frame_index<len(self.trans):
                if self.direct == 0:
                    self.frame = self.transr[self.frame_index]
                    self.frame_index = (self.frame_index + 1) % len(self.transr)
                    self.y = work_height -128
                    if self.frame_index == 0:
                        self.frame_index = 0
                        self.state = random.choice(["sit","walk"])
                else:
                    self.frame = self.trans[self.frame_index]
                    self.frame_index = (self.frame_index + 1) % len(self.trans)
                    self.y = work_height -128
                    if self.frame_index == 0:
                        self.frame_index = 0
                        self.state = random.choice(["sit","walk"])
        # self.window.geometry('112x128+' + str(self.x) + '+' + str(self.y))
        self.window.geometry('112x128+' + str(self.x) + '+' + str(min(self.y, work_height - 128)))
        self.label.configure(image=self.frame)
        self.window.after(100, self.update)



if __name__ == "__main__":
    pai = Paimon()
