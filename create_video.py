from moviepy.editor import *
import os
from fetch_images import fetch_images
import re
from PIL import Image
import random
from moviepy.video.fx.all import speedx

# ✅ Fix for PIL’s deprecated ANTIALIAS
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

def extract_keywords(image_script):
    return re.findall(r'\[(.*?)\]', image_script)

def split_sentences(script):
    return re.split(r'(?<=[.!?]) +', script)

def apply_ken_burns_effect(img_path, duration):
    zoom_factor = random.uniform(1.1, 1.3)
    x_start = random.uniform(0, 0.2)
    y_start = random.uniform(0, 0.2)
    return (ImageClip(img_path)
            .resize(height=800)  # slightly zoomed in
            .set_position("center")
            .crop(x1=int(x_start * 1280), y1=int(y_start * 720), width=1280, height=720)
            .resize(lambda t: 1 + (zoom_factor - 1) * t / duration)
            .set_duration(duration))

def create_video(narration_script, image_script, audio_path, topic):
    keywords = extract_keywords(image_script)
    sentences = split_sentences(narration_script)

    # keep original audio speed
    audio = AudioFileClip(audio_path).fx(speedx, 1.5)
    audio_duration = audio.duration

    image_paths = []
    for keyword in keywords:
        image_paths += fetch_images(keyword, count=1)

    if len(image_paths) < len(sentences):
        image_paths += fetch_images(topic, count=(len(sentences) - len(image_paths)))

    img_duration = audio_duration / len(sentences)
    clips = []

    for i, sentence in enumerate(sentences):
        img_path = image_paths[i] if i < len(image_paths) else image_paths[-1]
        img_clip = apply_ken_burns_effect(img_path, img_duration)

        # Subtitle overlay
        txt_clip = (TextClip(sentence, fontsize=36, font="Arial-Bold", color='white', bg_color="black", size=(1200, None), method='caption')
                    .set_position(("center", "bottom"))
                    .set_duration(img_duration)
                    .fadein(0.5).fadeout(0.5))

        composite = CompositeVideoClip([img_clip, txt_clip])
        clips.append(composite)

    video = concatenate_videoclips(clips, method="compose").set_audio(audio)

    os.makedirs("output", exist_ok=True)
    output_path = f"output/{topic.replace(' ', '_')}_video.mp4"
    video.write_videofile(output_path, fps=24)

    print(f"\n✅ Video Successfully created at: {output_path}")
