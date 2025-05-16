from google import genai
import json
import google.generativeai as genai
import re
import requests
import base64

#gemini text api define
genai.configure(api_key="AIzaSyC8YOsoIj5YuWex1muFSwXCGwcDOaAUUAY")

#api define picture
api_key ="sk-JPMYX9EfEeL81uMolAfYeIjITWe2XORs0HuGtCkyPXFZwhT9"
api_url ="https://api.stability.ai/v2beta/stable-image/generate/sd3"


#weather data, dummy test data
weather_data ={
    "temperature": 19,       # Celsius
    "wind": "4",      # or value in km/h
    "rain": "heavy rain",
    "humidity": 77,
    "air_pressure": 1011,
    "location_type": "outdoor",  # or 'indoor'
}

#clothes data
# Load clothes data from files
with open("../clothes_data/all_clothing_types.json", "r") as f1:
    clothing_types = json.load(f1)

with open("../clothes_data/all_material_data.json", "r") as f2:
    material_data = json.load(f2)

# Combine into a structured dictionary
clothes_data = {
    "types": clothing_types,
    "materials": material_data
}

#create prompt
def build_prompt(weather_data, clothes_data):
        prompt = f"""
        you are a university student age early 20.
        Current weather conditions:
        - Temperature: {weather_data['temperature']}°C
        - Wind: {weather_data['wind']}
        - Rain: {weather_data['rain']}
        - Humidity: {weather_data['humidity']}%
        - Air Pressure: {weather_data['air_pressure']} hPa
        - Location: {weather_data['location_type']}

        Available clothing options include the following types:
        {', '.join(clothes_data['types'])}

        and the following materials:
        {', '.join(clothes_data['materials'])}

        Please suggest 3 outfits suitable for there conditions and location.
        for each outfit, provide:
        -suggestions materials,types, and colors in 3 points
        -simple explain why it fits the weather and location in one sentence
        -a short prompt for an image generation model to draw the outfit.

        Respond in clear text.
        """

        return prompt

#send prompt to gemini
def get_result(prompt: str):
    model=genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    return response.text

#call def build prompt
prompt = build_prompt(weather_data, clothes_data)

#call gemini
result = get_result(prompt)

print(result)

#def return image prompt only
def image_prompt(result):
     imageprompts = re.findall(r'\*\*Image Prompt:\*\*\s*"([^"]+)"', result)
    
     return imageprompts

#prompt_text

imageprompts =image_prompt(result)

joined_prompts =";".join(imageprompts) if imageprompts else "fashion outfits"

prompt_text = f"generate 3 outfit in one picture based on the {joined_prompts}"

#pay load
files = {
    "prompt" : (None, prompt_text),
    "output_format": (None, "png"),
}

#header
headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json",
}

#send api
response = requests.post(api_url, files=files, headers=headers)

#exception handle
if response.status_code == 200:
    image_data = response.json()["image"]

    #save image
    with open("generated_image.png", "wb") as f:
        f.write(base64.b64decode(image_data))
    print("image saved")
else:
    print(f" Error: {response.status_code} - {response.text}")

