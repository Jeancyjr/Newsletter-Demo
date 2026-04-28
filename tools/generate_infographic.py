#!/usr/bin/env python3
"""Generate an infographic using Nano Banana via Key.ai. Saves to .tmp/infographic.png."""

import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

KEY_AI_API_KEY = os.getenv("KEY_AI_API_KEY")
KEY_AI_BASE_URL = os.getenv("KEY_AI_BASE_URL", "https://api.key.ai/v1")


def generate_infographic() -> str:
    with open(".tmp/content.json") as f:
        content = json.load(f)

    prompt = content["infographic_prompt"]

    headers = {
        "Authorization": f"Bearer {KEY_AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "nano-banana",
        "prompt": prompt,
        "width": 800,
        "height": 500,
        "format": "png",
    }

    response = requests.post(
        f"{KEY_AI_BASE_URL}/images/generations",
        headers=headers,
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()

    # Key.ai returns either a URL or base64 image data
    os.makedirs(".tmp", exist_ok=True)
    image_path = ".tmp/infographic.png"

    if "url" in data.get("data", [{}])[0]:
        image_url = data["data"][0]["url"]
        img_response = requests.get(image_url, timeout=60)
        img_response.raise_for_status()
        with open(image_path, "wb") as f:
            f.write(img_response.content)
    elif "b64_json" in data.get("data", [{}])[0]:
        import base64
        b64 = data["data"][0]["b64_json"]
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(b64))
    else:
        raise ValueError(f"Unexpected Key.ai response format: {data}")

    print(f"Infographic saved to {image_path}")
    return image_path


if __name__ == "__main__":
    generate_infographic()
