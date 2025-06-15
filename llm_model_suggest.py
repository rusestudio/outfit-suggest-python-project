import base64
import json
import re
import uuid

import google.generativeai as genai
import requests

from data_to_be_prompt import clothes_data
from prompt import build_prompt, image_prompt
from database import userData

# gemini text api define
genai.configure(api_key="AIzaSyC8YOsoIj5YuWex1muFSwXCGwcDOaAUUAY")

# api define picture
api_key = "sk-JMYyFEVPfYvhzmfZmh3i5YRB7oEAM2DUYl7oTXfLANbGltQ1"
api_url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"


# send prompt to gemini
def get_result(prompt: str):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

#save explaination
def save_explaination(result):
    # Split the result by image prompts (should separate each outfit block)
    blocks = result.strip().split("**Image Prompt:**")

    explanations = []
    for block in blocks[:3]:  # Only first 3 outfits
        cleaned = block.strip()

        # Optional cleanup of markdown-style asterisks
        cleaned = cleaned.replace("*", "").strip()

        explanations.append(cleaned)

    # Ensure we always return 3 entries
    while len(explanations) < 3:
        explanations.append("No outfit suggestion available.")

    return explanations


def generate_images(image_prompts: list):
    images = []
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    for prompt_text in image_prompts:
        files = {
            "prompt": (None, prompt_text),
            "output_format": (None, "png"),
        }
        response = requests.post(api_url, files=files, headers=headers)
        if response.status_code == 200:
            image_base64 = response.json()["image"]
            images.append(f"data:image/png;base64,{image_base64}")
        else:
            images.append("image not available")  # Placeholder for failed image

    return images


def main(user, weather_data, clothes_data, user_input):
    # call def build prompt
    prompt = build_prompt(user, weather_data, clothes_data, user_input)
    # call gemini
    result = get_result(prompt)
    #save explanation
    explanations = save_explaination(result)
    # prompt_text
    imageprompts = image_prompt(result)
    image_base64_list = generate_images(imageprompts)

    suggestions = []
    for i in range(3):
        suggestions.append({
            "image_base64": image_base64_list[i] if i < len(image_base64_list) else "",
            "explanation": explanations[i] if i < len(explanations) else ""
        })

    return suggestions


# Only run this if the file is executed directly
if __name__ == "__main__":
    suggest = main()
    for s in suggest:
        print(json.dumps(s, indent=2))