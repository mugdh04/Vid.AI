import requests
import os
import shutil
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.environ['PEXELS_API_KEY']
PEXELS_API_URL = "https://api.pexels.com/v1/search"

headers = {
    "Authorization": PEXELS_API_KEY
}

def fetch_images(query, count=1):
    response = requests.get(PEXELS_API_URL, headers=headers, params={"query": query, "per_page": count})
    data = response.json()
    image_urls = [photo["src"]["landscape"] for photo in data.get("photos", [])]

    os.makedirs("images", exist_ok=True)
    image_paths = []
    for url in image_urls:
        img_name = f"images/{uuid4().hex}.jpg"
        with requests.get(url, stream=True) as r:
            with open(img_name, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        image_paths.append(img_name)

    return image_paths
