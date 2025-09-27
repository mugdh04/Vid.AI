import os
import json
from difflib import SequenceMatcher
import re

def normalize_topic(topic):
    """Normalize topic for comparison by removing special chars and converting to lowercase"""
    return re.sub(r'[^a-zA-Z0-9\s]', '', topic.lower().strip())

def calculate_similarity(topic1, topic2):
    """Calculate similarity between two topics using sequence matching"""
    norm_topic1 = normalize_topic(topic1)
    norm_topic2 = normalize_topic(topic2)
    
    # Check for exact match
    if norm_topic1 == norm_topic2:
        return 1.0
    
    # Check for substring match
    if norm_topic1 in norm_topic2 or norm_topic2 in norm_topic1:
        return 0.9
    
    # Calculate sequence similarity
    similarity = SequenceMatcher(None, norm_topic1, norm_topic2).ratio()
    
    # Check for common keywords (boost similarity if many words match)
    words1 = set(norm_topic1.split())
    words2 = set(norm_topic2.split())
    common_words = words1.intersection(words2)
    
    if len(common_words) > 0 and (len(words1) > 0 and len(words2) > 0):
        keyword_similarity = len(common_words) / max(len(words1), len(words2))
        similarity = max(similarity, keyword_similarity * 0.8)
    
    return similarity

def load_video_metadata():
    """Load existing video metadata from JSON file"""
    metadata_file = "output/video_metadata.json"
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading metadata: {e}")
    return {}

def save_video_metadata(metadata):
    """Save video metadata to JSON file"""
    os.makedirs("output", exist_ok=True)
    metadata_file = "output/video_metadata.json"
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving metadata: {e}")

def search_existing_video(topic, similarity_threshold=0.75):
    """Search for existing videos with similar topics"""
    if not os.path.exists("output"):
        return None
    
    # Load metadata
    metadata = load_video_metadata()
    
    # Check existing video files
    video_files = [f for f in os.listdir("output") if f.endswith('.mp4')]
    
    best_match = None
    best_similarity = 0
    
    for video_file in video_files:
        video_path = os.path.join("output", video_file)
        
        # Get topic from metadata or filename
        if video_file in metadata:
            stored_topic = metadata[video_file].get('topic', '')
        else:
            # Extract topic from filename (remove _video.mp4 suffix)
            stored_topic = video_file.replace('_video.mp4', '').replace('_', ' ')
        
        # Calculate similarity
        similarity = calculate_similarity(topic, stored_topic)
        
        if similarity > best_similarity and similarity >= similarity_threshold:
            best_similarity = similarity
            best_match = {
                'filename': video_file,
                'path': video_path,
                'topic': stored_topic,
                'similarity': similarity
            }
    
    return best_match

def register_new_video(topic, filename):
    """Register a newly created video in metadata"""
    metadata = load_video_metadata()
    
    metadata[filename] = {
        'topic': topic,
        'created_at': str(os.path.getctime(os.path.join("output", filename))),
        'normalized_topic': normalize_topic(topic)
    }
    
    save_video_metadata(metadata)
