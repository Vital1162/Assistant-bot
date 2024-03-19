from PIL import Image, ImageTk
import google.generativeai as genai
import json
import pyautogui
import PIL.Image
genai.configure(api_key="AIzaSyDmod61h5FHXa-9v368ZJ1GtjkWhCWeGc8")




# Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 1000,
}

safety_settings = {
    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
    "HARM_CATEGORY_SEXUAL":"BLOCK_NONE",
    # "HARM_CATEGORY_DEROGATORY":"BLOCK_NONE",
    # "HARM_CATEGORY_TOXICITY":"BLOCK_NONE",
    # "HARM_CATEGORY_UNSPECIFIED":"BLOCK_NONE",
    # "HARM_CATEGORY_VIOLENCE":"BLOCK_NONE",
    # "HARM_CATEGORY_DANGEROUS":"BLOCK_NONE",
    # "HARM_CATEGORY_MEDICAL":"BLOCK_NONE"
}
model = genai.GenerativeModel(model_name="gemini-pro", 
                            generation_config=generation_config,
                              safety_settings=safety_settings)




model_vision = genai.GenerativeModel(model_name='gemini-pro-vision',
                                    generation_config=generation_config,
                                     safety_settings=safety_settings)

chat = model.start_chat(history=[])
