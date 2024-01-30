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
from WaifuVoice import TextToSpeech
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
from model import chat,model,model_vision,generate_response
import pyautogui
import PIL.Image
from inputimeout import inputimeout
load_dotenv()

desc = "I want you to act as my friend, your name is Paimon, don't reply 'Paimon:' in messages and take a really short messages. I will tell you what is happening in my life and you will reply with something helpful and supportive to help me through the difficult times or you can make joke and make me happy, you will always acting as cute as possible like a anime girl in real life. Messages not too long.Do not write any explanations, maximum number of tokens in response lower than 20."



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
    def __init__(self,mode):
        self.mode = mode
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


        self.text_window = tk.Toplevel()
        # Set the position of the text window close to the Paimon window
        text_window_x = self.x  - 300
        text_window_y = self.y - 450

        self.text_window.geometry(f'400x400+{text_window_x}+{text_window_y}')
        self.text_window.title('Panel')

# Create a frame to contain the text input and the send button
        input_frame = tk.Frame(self.text_window)
        input_frame.pack(pady=20,padx=20)

        # Create a scrolled text widget for multiline input
        self.text_input = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, width=30, height=1)
        self.text_input.pack(side=tk.LEFT)

        # # Set a hint for the text input
        # self.text_input.insert(tk.END, "Chat to Pai...")  # Hint text
        # self.text_input.bind("<FocusIn>", self.clear_hint)  # Bind FocusIn event
        
        self.send_button = tk.Button(self.text_window, text="Send", command=self.send_command)
        self.send_button.pack(pady=1)


        response_frame = tk.Frame(self.text_window)
        response_frame.pack(padx=20,pady=20)
        # Create a scrolled text widget for displaying spoken text
        self.text_label = scrolledtext.ScrolledText(response_frame, wrap=tk.WORD, width=30, height=10)
        self.text_label.pack(expand=True, fill='both')
        self.text_label.insert(tk.END, "Wait for responsed...")

        self.current_time = 0
        self.active_windown_cooldown = 0



        self.label.pack()

        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

        self.window.after(1, self.update)

        self.voice_thread = Thread(target=self.voice_assistant_thread)
        self.voice_thread.start()
   
        self.window.mainloop()


    def voice_assistant_thread(self):
        while True:
            if self.mode == 'listen':
                self.voice_assistant()
            else:
                self.send_command()
            
    # def clear_hint(self,event):
    #     # Clear the hint text when the user clicks on the text input
    #     if self.text_input.get("1.0", tk.END).strip() == "Chat to Pai...":
    #         self.text_input.delete("1.0", tk.END)

    def send_command(self):
        # Get the text from the entry widget
        command_text = self.text_input.get("1.0", tk.END)  # Provide start and end indices

        # Call the voice_assistant method with the entered command
        self.text_assistant(command_text)

        # Clear the text input after sending the command
        self.text_input.delete("1.0", tk.END)  # Clear the entire content of the Text widget

    def text_assistant(self,cmd):
        if not cmd:
            try:
                mess = load_messages('messages.json')
            except FileNotFoundError:
                mess = []
                mess.append({'role':'user','parts':[desc]})
                reply = model.generate_content(mess)
                reply.resolve()
                mess.append({'role': 'model',
                            'parts': [reply.text]})
                time.sleep(2)
            
            command = str(cmd).lower()
            screenshot = pyautogui.screenshot()
            file_path = 'C:/Users/ADMIN/Paimon/screenshot.png'

            screenshot.save(file_path)
            img = PIL.Image.open(file_path)
            vision = model_vision.generate_content(["What is master doing right now, take a short describe no details about what is master doing right now? You reply with brief or funny, to-the-point answers with no elaboration",img],stream=True)
            vision.resolve()
            time.sleep(2)
            mess.append({'role': 'user',
                            'parts':[f'{command} {vision.text}']})

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
                            'parts':[response.text]})
                save_messages('messages.json', mess)
                response.resolve()
                time.sleep(2)
                print(response.text)
                translator = Translator()
                translated_response = self.translate_with_retry(translator, response)
                print(translated_response)
                self.speak(f"はい {translated_response}")

            self.current_time = time.time() + random.randint(28,32)
        else:
            if time.time() > self.current_time:
                screenshot = pyautogui.screenshot()
                file_path = 'C:/Users/ADMIN/Paimon/screenshot.png'

                screenshot.save(file_path)
                img = PIL.Image.open(file_path)
                vision = model_vision.generate_content(["What is master doing right now, take a short describe no details about what is master doing right now? You reply with brief or funny, to-the-point answers with no elaboration, maximum number of tokens in response lower than 20",img],stream=True)
                vision.resolve()
                time.sleep(2)
                mess.append({'role': 'user',
                            'parts':[f'no response and {vision.text}']})
                response = model.generate_content(mess)
                mess.append({'role': 'model',
                                'parts':[response.text]})
                save_messages('messages.json', mess)
                translator = Translator()
                translated_response = self.translate_with_retry(translator, response)
                print(translated_response)
                self.speak(f"はい {translated_response}")

                self.current_time = time.time() +random.randint(1,3)
        
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
                
                audio = self.recognizer.listen(source,timeout=3)
                
                if audio:
                    self.state = "listen"

                else:
                    self.state = "norm" 

                command = self.recognizer.recognize_google(audio).lower()
                screenshot = pyautogui.screenshot()
                file_path = 'C:/Users/ADMIN/Paimon/screenshot.png'

                screenshot.save(file_path)
                img = PIL.Image.open(file_path)
                vision = model_vision.generate_content(["What is master doing right now, take a short describe no details about what is master doing right now? You reply with brief or funny, to-the-point answers with no elaboration",img],stream=True)
                vision.resolve()
                time.sleep(2)
                mess.append({'role': 'user',
                                'parts':[f'{command} {vision.text}']})

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
                                'parts':[response.text]})
                    save_messages('messages.json', mess)
                    response.resolve()
                    time.sleep(2)
                    print(response.text)
                    translator = Translator()
                    translated_response = self.translate_with_retry(translator, response)
                    print(translated_response)
                    self.speak(f"はい {translated_response}")
                    
            
                self.current_time = time.time() + random.randint(28,32)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio.")
            if time.time() > self.current_time:
                screenshot = pyautogui.screenshot()
                file_path = 'C:/Users/ADMIN/Paimon/screenshot.png'

                screenshot.save(file_path)
                img = PIL.Image.open(file_path)
                vision = model_vision.generate_content(["What is master doing right now, take a short describe no details about what is master doing right now? You reply with brief or funny, to-the-point answers with no elaboration, maximum number of tokens in response lower than 20",img],stream=True)
                vision.resolve()
                time.sleep(2)
                mess.append({'role': 'user',
                            'parts':[f'no response and {vision.text}']})
                response = model.generate_content(mess)
                
                mess.append({'role': 'model',
                                'parts':[response.text]})
                save_messages('messages.json', mess)
                print(response.text)
                translator = Translator()
                translated_response = self.translate_with_retry(translator, response)
                print(translated_response)
                self.speak(f"はい {translated_response}")
                # Append the response to the conversation history
  
          
                self.current_time = time.time() +random.randint(1000,3000)
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            if time.time() > self.current_time:
                screenshot = pyautogui.screenshot()
                file_path = 'C:/Users/ADMIN/Paimon/screenshot.png'

                screenshot.save(file_path)
                img = PIL.Image.open(file_path)
                vision = model_vision.generate_content(["What is master doing right now, take a short describe no details about what is master doing right now? You reply with brief or funny, to-the-point answers with no elaboratio, maximum number of tokens in response lower than 20n",img],stream=True)
                vision.resolve()
                time.sleep(2)
                mess.append({'role': 'user',
                'parts':[f'no response and {vision.text}']})
                response = model.generate_content(mess)
                mess.append({'role': 'model',
                                'parts':[response.text]})
                save_messages('messages.json', mess)
                translator = Translator()
                translated_response = self.translate_with_retry(translator, response)
                print(translated_response)
                self.speak(f"はい {translated_response}")


                self.current_time = time.time() +random.randint(1000,3000)
                
        except sr.WaitTimeoutError:
            print("Listening timed out. Please try again.")
            if time.time() > self.current_time:
                screenshot = pyautogui.screenshot()
                file_path = 'C:/Users/ADMIN/Paimon/screenshot.png'

                screenshot.save(file_path)
                img = PIL.Image.open(file_path)
                vision = model_vision.generate_content(["What is master doing right now, take a short describe no details about what is master doing right now? You reply with brief or funny, to-the-point answers with no elaboration, maximum number of tokens in response lower than 20",img],stream=True)
                vision.resolve()
                time.sleep(2)
                mess.append({'role': 'user',
                            'parts':[f'no response and {vision.text}']})
                response = model.generate_content(mess)
                mess.append({'role': 'model',
                                'parts':[response.text]})
                save_messages('messages.json', mess)
                translator = Translator()
                translated_response = self.translate_with_retry(translator, response)
                print(translated_response)
                self.speak(f"はい {translated_response}")

                self.current_time = time.time() +random.randint(1000,3000)
                
        self.state = "norm"

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
        text_to_speech = TextToSpeech(text)
        if text_to_speech.generate_audio():
            self.text_label.delete(1.0, tk.END)
            en_text = Translator().translate(text, 'en').text
            self.text_label.insert(tk.END, en_text)
            text_to_speech.play_audio()


    def update(self):
        if self.state == "norm":
            self.frame = self.norm[self.frame_index]
            self.frame_index = (self.frame_index + 1) % len(self.norm)
                
        elif self.state == "listen":
            self.frame = self.listen[0]


        self.window.geometry('112x128+' + str(self.x) + '+' + str(self.y))
        self.label.configure(image=self.frame)
        self.window.after(100, self.update)


if __name__ == "__main__":
    input = inputimeout('Texting or listening mode ? (only type "text" or "listen")\n')
    if input in ['text','listen']:
        mode = str(input).lower()
        pai = Paimon(mode)
    else:
        audio = AudioSegment.from_file('wrong_command', format="mp3")
        play(audio)
