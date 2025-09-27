import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_script(topic):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": "Bearer " + OPENROUTER_API_KEY,
        "Content-Type": "application/json"
    }

    user_prompt = (
        f"Generate an educational narration script on topic '{topic}' for the length of ideal 5 to 10 mins as per the requirement of the topic.\n"
        "Divide the script into two parts: 1st Narration Script and 2nd Visual Cues for Video Generation.\n"
        "Narration Script should be 5 to 10 mins in length and it should not contain any kind of Tags or anything ese then the narration script itself, do not write anything else and strictly follow this not even the word Narrator or Narration script in the starting."
        "Keep it informative and engaging. Make it detailed and easy to understand."
        "Make it engaging and informative, suitable for a general audience and everyone should be able to understand it easily."
        "Include real-life examples where ever needed to explain complex concepts to help students.\n\n"
        "Then provide an image direction script with visual cues in square brackets in the last do not start with Image Script or Visual Directions or anything else, just start with the image directions written in the square brackets."
        "like [Indian Parliament], [Mughal architecture], that align with the narration. and remember to not include any kind of tags or anything else in the image script, just the image directions in square brackets and have to be in the last of the script after one line gap from narration script."
    )

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that generates educational scripts with narration and visual directions."},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "top_p": 1.0,
        "max_tokens": 5000
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        res = response.json()

        full_text = res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        if not full_text:
            print("❌ Warning: Empty response from model.")
            print("🔍 Full response:", res)
            return {"narration_script": "", "image_script": ""}

        # Find where the first square bracketed visual cue appears
        match = re.search(r"\n?\[.*?\]", full_text)
        if match:
            split_index = match.start()
            narration_script = full_text[:split_index].strip()
            image_script = full_text[split_index:].strip()
        else:
            narration_script = full_text
            image_script = ""

        print("✅ Script generated successfully.")
        return {
            "narration_script": narration_script,
            "image_script": image_script
        }

    except requests.exceptions.RequestException as e:
        print("❌ Network error:", e)
    except Exception as e:
        print("❌ Unexpected error:", e)

    return {"narration_script": "", "image_script": ""}
