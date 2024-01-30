from PIL import Image, ImageTk
import google.generativeai as genai
import json
import pyautogui
import PIL.Image
genai.configure(api_key="")




# Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 10,
}

safety_settings = {
    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
}
model = genai.GenerativeModel(model_name="gemini-pro",
                            #   generation_config=generation_config,
                              safety_settings=safety_settings)




model_vision = genai.GenerativeModel(model_name='gemini-pro-vision',
                                    #  generation_config=generation_config,
                                     safety_settings=safety_settings)

chat = model.start_chat(history=[])

def save_messages(filename, messages):
    with open(filename, 'w') as file:
        json.dump(messages, file)

def load_messages(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def generate_response(request):
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
      vision = generate_response_vision()
      mess.append({'role': 'user',
                    'parts':[f'{request} and {vision}']})
  return mess


def generate_response_vision():
  screenshot = pyautogui.screenshot()
  file_path = 'C:/Users/ADMIN/Paimon/screenshot.png'
  screenshot.save(file_path)
  img = PIL.Image.open(file_path)
  vision = model_vision.generate_content(["What is user doing right now, take a short describe no details about what is user doing right now? You reply with brief or funny, to-the-point answers with no elaboration",img],stream=True)
  vision.resolve()
  return vision.text


# response = model.generate_content("Hello ?")
# print(response.text)
