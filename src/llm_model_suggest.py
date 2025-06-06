import base64
import json
import re
import uuid

import google.generativeai as genai
import requests

from data_to_be_prompt import user_data,weather_data, clothes_data,user_preference_dday,user_preference_fday
from prompt import build_prompt, image_prompt

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

def main():
    # call def build prompt
    prompt = build_prompt(user_data,weather_data, clothes_data,user_preference_dday,user_preference_fday)

    # call gemini
    result = get_result(prompt)
    print(result)

    #save explaination
    explanations = result.strip().split("**Image Prompt:**")[:3]
    explain1 = explanations[0].strip()
    explain2 = explanations[1].strip() if len(explanations) > 1 else ""
    explain3 = explanations[2].strip() if len(explanations) > 2 else ""

    explain_data = {
        "explain1": explain1,
        "explain2": explain2,
        "explain3": explain3
    }

    fileexpname = f"../explaination.json"
    with open(fileexpname, "w", encoding="utf-8") as f:
        json.dump(explain_data, f, indent=4, ensure_ascii=False)
    print("Explanations saved to:", fileexpname)

    # prompt_text
    imageprompts = image_prompt(result)

    # header
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    for n, prompt_text in enumerate(imageprompts, start=1):
        files = {
            "prompt": (None, prompt_text),
            "output_format": (None, "png"),
        }
        # send api
        # make respone in list append then request post
        response = requests.post(api_url, files=files, headers=headers)

        # exception handle
        if response.status_code == 200:
            image_data = response.json()["image"]

            # save image to database by 용한님님
            filename = f"../database-fast-api-html/img/img{uuid.uuid4()}.png"
            with open(filename, "wb") as f:
                f.write(base64.b64decode(image_data))
            print(f" {n} image saved")
        else:
            print(f" Error:image {n}, {response.status_code} - {response.text}")

# Only run this if the file is executed directly
if __name__ == "__main__":
    main()