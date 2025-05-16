from google import genai
import json
import google.generativeai as genai

genai.configure(api_key="AIzaSyC8YOsoIj5YuWex1muFSwXCGwcDOaAUUAY")


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
with open("all_clothing_types.json", "r") as f1:
    clothing_types = json.load(f1)

with open("all_material_data.json", "r") as f2:
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


def get_result(prompt: str):
    model=genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    return response.text

#call def build prompt
prompt = build_prompt(weather_data, clothes_data)

#call gemini
result = get_result(prompt)

print(result)