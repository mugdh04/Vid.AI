import requests
import os
import shutil
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
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

def fetch_videos(query, count=1):
    """Fetch videos from Pexels API"""
    video_url = "https://api.pexels.com/videos/search"
    response = requests.get(video_url, headers=headers, params={"query": query, "per_page": count})
    data = response.json()
    
    video_urls = []
    for video in data.get("videos", []):
        # Get the smallest HD video file
        video_files = video.get("video_files", [])
        hd_videos = [vf for vf in video_files if vf.get("quality") == "hd" and vf.get("width", 0) <= 1920]
        if hd_videos:
            video_urls.append(hd_videos[0]["link"])
    
    os.makedirs("videos", exist_ok=True)
    video_paths = []
    for url in video_urls:
        video_name = f"videos/{uuid4().hex}.mp4"
        with requests.get(url, stream=True) as r:
            with open(video_name, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        video_paths.append(video_name)
    
    return video_paths

def fetch_media(query, count=1, prefer_video=True):
    """Fetch both videos and images, preferring videos if available"""
    media_paths = []
    
    try:
        if prefer_video:
            video_paths = fetch_videos(query, count)
            media_paths.extend(video_paths)
        
        # Fill remaining with images if needed
        remaining = count - len(media_paths)
        if remaining > 0:
            image_paths = fetch_images(query, remaining)
            media_paths.extend(image_paths)
    except Exception as e:
        print(f"⚠️  Error fetching media for '{query}': {e}")
        # Fallback to images only
        try:
            image_paths = fetch_images(query, count)
            media_paths.extend(image_paths)
        except Exception as e2:
            print(f"❌ Error fetching fallback images: {e2}")
    
    return media_paths
