from google import genai
import json
import google.generativeai as genai
import re
import requests
import base64

from prompt import build_prompt, image_prompt
from data_to_be_prompt import weather_data, user_data, clothes_data

#gemini text api define
genai.configure(api_key="AIzaSyC8YOsoIj5YuWex1muFSwXCGwcDOaAUUAY")

#api define picture
api_key ="sk-pANMxceDTa4mKb2zmYeAVE3aFYUhsD5ODjVkhw4ZnIWydXMa"
api_url ="https://api.stability.ai/v2beta/stable-image/generate/sd3"

#send prompt to gemini
def get_result(prompt: str):
    model=genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    return response.text

#call def build prompt
prompt = build_prompt(user_data, weather_data, clothes_data)

#call gemini
result = get_result(prompt)

print(result)

#prompt_text
imageprompts =image_prompt(result)

#header
headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json",
}

for n, prompt_text in enumerate(imageprompts, start=1):
    files ={
        "prompt": (None, prompt_text),
        "output_format": (None, "png"),
    }
    #send api
    #make respone in list append then request post
    response = requests.post(api_url, files=files, headers=headers)


    #exception handle
    if response.status_code == 200:
        image_data = response.json()["image"]

     #save image
        filename = f"../generated_img_data/generated_image{n}.png"
        with open( filename, "wb") as f:
            f.write(base64.b64decode(image_data))
        print(f" {n} image saved")
    else:
        print(f" Error:image {n}, {response.status_code} - {response.text}")

