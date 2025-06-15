from datetime import datetime
import urllib.request
import base64
import json
import time
import os

webui_server_url = 'http://59.30.158.50:7860/'

out_dir = 'api_out'
out_dir_t2i = os.path.join(out_dir, 'txt2img')
os.makedirs(out_dir_t2i, exist_ok=True)

def timestamp():
    return datetime.fromtimestamp(time.time()).strftime("%Y%m%d-%H%M%S")

def decode_and_save_base64(base64_str, save_path):
    with open(save_path, "wb") as file:
        file.write(base64.b64decode(base64_str))

def call_api(api_endpoint, **payload):
    data = json.dumps(payload).encode('utf-8')
    url = webui_server_url.rstrip('/') + '/' + api_endpoint.lstrip('/')
    request = urllib.request.Request(
        url,
        headers={'Content-Type': 'application/json'},
        data=data,
    )
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode('utf-8'))

def generate_images(image_prompts: list):
    images = []

    for prompt_text in image_prompts:
        payload = {
            "prompt": prompt_text,
            "negative_prompt": "",
            "seed": -1,
            "steps": 28,
            "width": 896,
            "height": 1152,
            "cfg_scale": 5,
            "sampler_name": "DPM++ 2M SDE Karras",
            "n_iter": 1,
            "batch_size": 1,
        }

        try:
            response = call_api('sdapi/v1/txt2img', **payload)
            base64_image = response.get('images', [])[0]
            filename = f"txt2img-{timestamp()}.png"
            save_path = os.path.join(out_dir_t2i, filename)
            decode_and_save_base64(base64_image, save_path)

            # return base64 for frontend display (optional)
            images.append(f"data:image/png;base64,{base64_image}")
        except Exception as e:
            print("Image generation failed:", e)
            images.append("image not available")

    return images