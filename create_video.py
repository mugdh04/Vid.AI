from moviepy.editor import *
import os
from fetch_media import fetch_media  # Import fetch_media instead of fetch_images
import re
from PIL import Image
import random
import shutil

# ✅ Fix for PIL’s deprecated ANTIALIAS
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

def extract_keywords(image_script):
    return re.findall(r'\[(.*?)\]', image_script)

def split_sentences(script):
    return re.split(r'(?<=[.!?]) +', script)

def split_subtitles(script, max_words=14):
    """Split script into subtitle chunks of up to max_words words."""
    words = script.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i+max_words])
        chunks.append(chunk)
    return chunks

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

def is_video_file(file_path):
    """Check if a file is a video based on its extension"""
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    return os.path.splitext(file_path)[1].lower() in video_extensions

def is_portrait_video(video_clip):
    """Check if video is in portrait orientation (height > width)"""
    return video_clip.h > video_clip.w

def create_video(narration_script, image_script, audio_path, topic):
    print("🔍 Extracting keywords from image script...")
    keywords = extract_keywords(image_script)
    print("🔍 Splitting narration script into sentences...")
    sentences = split_sentences(narration_script)

    print("🔊 Loading audio file...")
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    print("📥 Fetching media (videos/images) for each keyword...")
    media_paths = []
    for keyword in keywords:
        print(f"   - Fetching media for keyword: {keyword}")
        media_paths += fetch_media(keyword, count=1, prefer_video=True)

    print("📝 Splitting narration into subtitle chunks...")
    subtitle_chunks = split_subtitles(narration_script, max_words=14)
    n_subs = len(subtitle_chunks)

    print("📦 Ensuring enough media for all subtitle chunks...")
    if len(media_paths) < n_subs:
        print(f"   - Fetching additional media for topic: {topic}")
        media_paths += fetch_media(topic, count=(n_subs - len(media_paths)), prefer_video=True)
    media_paths = media_paths[:n_subs]  # Only as many as needed

    sub_duration = audio_duration / n_subs
    clips = []

    print("🎞️ Creating video/image clips and adding subtitles...")
    for i in range(n_subs):
        media_path = media_paths[i]
        content_clip = None
        video_clip = None
        if is_video_file(media_path):
            try:
                print(f"   - Processing video: {media_path}")
                video_clip = VideoFileClip(media_path)
                if is_portrait_video(video_clip):
                    print(f"     ⚠️ Portrait video detected, switching to image for subtitle {i+1}")
                    video_clip.close()
                    keyword = keywords[i % len(keywords)] if i < len(keywords) else topic
                    replacement_paths = fetch_media(keyword, count=1, prefer_video=False)
                    if replacement_paths:
                        media_path = replacement_paths[0]
                        print(f"     ➡️ Using image: {media_path}")
                        content_clip = apply_ken_burns_effect(media_path, sub_duration)
                    else:
                        print(f"     ⚠️ No image found, using center-cropped video.")
                        video_clip = VideoFileClip(media_path)
                        video_clip = (video_clip
                                     .resize(width=720)
                                     .set_position("center")
                                     .set_duration(sub_duration))
                        content_clip = video_clip
                else:
                    if video_clip.duration > sub_duration:
                        max_start = max(0, video_clip.duration - sub_duration)
                        start_time = random.uniform(0, max_start)
                        print(f"     ✂️ Trimming video to {sub_duration:.2f}s from {start_time:.2f}s")
                        subclip = video_clip.subclip(start_time, start_time + sub_duration)
                        video_clip.close()
                        video_clip = subclip
                    if video_clip.duration < sub_duration:
                        print(f"     🔁 Looping video to {sub_duration:.2f}s")
                        video_clip = video_clip.fx(vfx.loop, duration=sub_duration)
                    video_clip = (video_clip
                                 .resize(height=720)
                                 .set_position("center")
                                 .set_duration(sub_duration))
                    content_clip = video_clip
            except Exception as e:
                print(f"   ❌ Error processing video {media_path}: {e}, falling back to image")
                if video_clip:
                    video_clip.close()
                replacement_paths = fetch_media(keywords[i % len(keywords)], count=1, prefer_video=False)
                if replacement_paths:
                    media_path = replacement_paths[0]
                    print(f"     ➡️ Using image: {media_path}")
                content_clip = apply_ken_burns_effect(media_path, sub_duration)
        else:
            print(f"   - Processing image: {media_path}")
            content_clip = apply_ken_burns_effect(media_path, sub_duration)

        txt_clip = (TextClip(subtitle_chunks[i], fontsize=38, font="Arial-Bold", color='white',
                            bg_color="rgba(0,0,0,0.5)", size=(1000, None), method='caption')
                    .set_position(("center", "bottom"))
                    .set_duration(sub_duration)
                    .margin(bottom=60, opacity=0)
                    .fadein(0.2).fadeout(0.2))
        
        composite = CompositeVideoClip([content_clip, txt_clip])
        clips.append(composite)
        if video_clip:
            video_clip.close()

    print("🧩 Concatenating all clips and adding audio...")
    video = concatenate_videoclips(clips, method="compose").set_audio(audio)

    print("💾 Saving final video to output folder...")
    os.makedirs("output", exist_ok=True)
    output_path = f"output/{topic.replace(' ', '_')}_video.mp4"
    video.write_videofile(output_path, fps=24)

    print(f"\n✅ Video Successfully created at: {output_path}")

    print("🧹 Cleaning up: deleting audio, images, and videos folders...")
    for folder in ["audio", "images", "videos"]:
        try:
            shutil.rmtree(folder)
            print(f"   - Deleted folder: {folder}")
        except Exception as e:
            print(f"   ⚠️ Could not delete folder {folder}: {e}")
