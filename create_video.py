from moviepy.editor import *
import os
from fetch_media import fetch_media  # Import fetch_media instead of fetch_images
import re
from PIL import Image
import random

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

def cleanup_temp_folders():
    """Delete temporary media folders after successful video creation"""
    temp_folders = ["videos", "images", "audio"]
    for folder in temp_folders:
        try:
            if os.path.exists(folder):
                print(f"🧹 Cleaning up temporary folder: {folder}")
                for file in os.listdir(folder):
                    file_path = os.path.join(folder, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"⚠️ Error deleting file {file_path}: {e}")
                # Optional: remove the empty folder itself
                # os.rmdir(folder)
        except Exception as e:
            print(f"⚠️ Error cleaning up {folder} folder: {e}")

def create_video(narration_script, image_script, audio_path, topic):
    keywords = extract_keywords(image_script)
    sentences = split_sentences(narration_script)

    # keep original audio speed
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    # Fetch media (videos and images) for each keyword
    media_paths = []
    for keyword in keywords:
        media_paths += fetch_media(keyword, count=1, prefer_video=True)

    # Split narration into subtitle chunks (1-2 lines each)
    subtitle_chunks = split_subtitles(narration_script, max_words=14)
    n_subs = len(subtitle_chunks)

    # Ensure enough media for all subtitle chunks
    if len(media_paths) < n_subs:
        media_paths += fetch_media(topic, count=(n_subs - len(media_paths)), prefer_video=True)
    media_paths = media_paths[:n_subs]  # Only as many as needed

    sub_duration = audio_duration / n_subs
    clips = []

    for i in range(n_subs):
        media_path = media_paths[i]
        
        # Create appropriate clip based on media type (video or image)
        if is_video_file(media_path):
            try:
                # For videos, load and check orientation
                video_clip = VideoFileClip(media_path)
                
                # If video is portrait, replace with an image instead
                if is_portrait_video(video_clip):
                    print(f"Portrait video detected, switching to image for subtitle {i+1}")
                    video_clip.close()
                    # Fetch a replacement image
                    keyword = keywords[i % len(keywords)] if i < len(keywords) else topic
                    replacement_paths = fetch_media(keyword, count=1, prefer_video=False)
                    if replacement_paths:
                        media_path = replacement_paths[0]
                        content_clip = apply_ken_burns_effect(media_path, sub_duration)
                    else:
                        # If fetching image fails, still use the video but center crop it
                        video_clip = VideoFileClip(media_path)
                        video_clip = (video_clip
                                     .resize(width=720)
                                     .set_position("center")
                                     .set_duration(sub_duration))
                        content_clip = video_clip
                else:
                    # If video is landscape, process normally
                    if video_clip.duration > sub_duration:
                        max_start = max(0, video_clip.duration - sub_duration)
                        start_time = random.uniform(0, max_start)
                        video_clip = video_clip.subclip(start_time, start_time + sub_duration)
                    
                    if video_clip.duration < sub_duration:
                        video_clip = video_clip.fx(vfx.loop, duration=sub_duration)
                        
                    video_clip = (video_clip
                                 .resize(height=720)
                                 .set_position("center")
                                 .set_duration(sub_duration))
                    content_clip = video_clip
            except Exception as e:
                print(f"Error processing video {media_path}: {e}, falling back to image")
                # Fallback to image if video processing fails
                replacement_paths = fetch_media(keywords[i % len(keywords)], count=1, prefer_video=False)
                if replacement_paths:
                    media_path = replacement_paths[0]
                content_clip = apply_ken_burns_effect(media_path, sub_duration)
        else:
            # For images, apply Ken Burns effect as before
            content_clip = apply_ken_burns_effect(media_path, sub_duration)

        # Subtitle overlay (1-2 lines, bottom, not covering whole screen)
        txt_clip = (TextClip(subtitle_chunks[i], fontsize=38, font="Arial-Bold", color='white',
                            bg_color="rgba(0,0,0,0.5)", size=(1000, None), method='caption')
                    .set_position(("center", "bottom"))
                    .set_duration(sub_duration)
                    .margin(bottom=60, opacity=0)
                    .fadein(0.2).fadeout(0.2))
        
        composite = CompositeVideoClip([content_clip, txt_clip])
        clips.append(composite)

    video = concatenate_videoclips(clips, method="compose").set_audio(audio)

    os.makedirs("output", exist_ok=True)
    output_path = f"output/{topic.replace(' ', '_')}_video.mp4"
    video.write_videofile(output_path, fps=24)

    print(f"\n✅ Video Successfully created at: {output_path}")
    
    # Clean up temporary files after successful video creation
    cleanup_temp_folders()
    print("🧹 Temporary files cleaned up successfully.")
