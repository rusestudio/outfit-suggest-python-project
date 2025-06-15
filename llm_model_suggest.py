import base64
import json
import re
import uuid

import google.generativeai as genai
import requests

from data_to_be_prompt import clothes_data
from prompt import build_prompt, image_prompt
from database import userData
from img_gen import generate_images

# gemini text api define
genai.configure(api_key="AIzaSyC8YOsoIj5YuWex1muFSwXCGwcDOaAUUAY")

# api define picture
#api_key = "sk-JMYyFEVPfYvhzmfZmh3i5YRB7oEAM2DUYl7oTXfLANbGltQ1"
#api_url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"


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
    for block in blocks[:3]:
        block = block.strip()

        # Step 1: Find the start of the outfit explanation
        start_index = block.find("Outfit")
        if start_index == -1:
            explanations.append("No outfit explanation found.")
            continue

        # Step 2: Cut off before "Image Generation Prompt:"
        end_index = block.find("Image Generation Prompt:")
        if end_index == -1:
            end_index = len(block)

        explanation = block[start_index:end_index].strip()

        # Step 3: Remove all * characters
        explanation = explanation.replace("*", "")

        # Step 4: Add \n before key headers
        explanation = re.sub(r'(Materials, Types, and Colors:)', r'\n\1', explanation)
        explanation = re.sub(r'(Why it fits:)', r'\n\1', explanation)

        # Step 5: Remove double spaces and strip
        explanation = re.sub(r'\s+', ' ', explanation).strip()

        # Optional: Fix newline formatting for visual clarity
        explanation = explanation.replace('\n ', '\n')  # fix space after newline

        explanations.append(explanation)

    while len(explanations) < 3:
        explanations.append("No outfit suggestion available.")

    return explanations

def main(user, weather_data, clothes_data, user_input):
    # call def build prompt
    prompt = build_prompt(user, weather_data, clothes_data, user_input)
    # call gemini
    result = get_result(prompt)
    #print(result)
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