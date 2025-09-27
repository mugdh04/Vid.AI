from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import threading
import os
import time
import random
from generate_script import generate_script
from generate_audio import generate_audio
from create_video import create_video
from video_search import search_existing_video, register_new_video

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vidai_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Random facts for entertainment during processing
RANDOM_FACTS = [
    "The human brain processes visual information 60,000 times faster than text!",
    "YouTube users upload over 500 hours of video content every minute.",
    "The first video ever uploaded to YouTube was 'Me at the zoo' in 2005.",
    "Colors can affect emotions - that's why we chose violet for Vid.AI!",
    "AI can now generate videos in seconds that would take humans hours to create.",
    "The average attention span for online videos is just 8 seconds.",
    "Videos generate 1200% more shares than text and images combined.",
    "85% of Facebook videos are watched without sound - subtitles matter!",
    "The word 'video' comes from the Latin word 'videre' meaning 'to see'.",
    "Humans can process a visual scene in as little as 13 milliseconds."
]

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('generate_video')
def handle_video_generation(data):
    topic = data['topic']
    session_id = request.sid
    
    def generate_video_process():
        try:
            # Step 0: Search for existing video
            socketio.emit('progress', {'step': 0, 'message': 'Searching for existing videos...', 'percentage': 5}, room=session_id)
            time.sleep(0.5)
            
            existing_video = search_existing_video(topic)
            
            if existing_video:
                # Found existing video
                socketio.emit('progress', {'step': 6, 'message': f'Found existing video! (Similarity: {existing_video["similarity"]:.1%})', 'percentage': 100}, room=session_id)
                time.sleep(1)
                socketio.emit('video_found', {
                    'filename': existing_video['filename'],
                    'path': existing_video['path'],
                    'original_topic': existing_video['topic'],
                    'similarity': existing_video['similarity']
                }, room=session_id)
                return
            
            # No existing video found, proceed with generation
            socketio.emit('progress', {'step': 1, 'message': 'No existing video found. Generating new content...', 'percentage': 10}, room=session_id)
            
            # Step 1: Generate Script
            socketio.emit('progress', {'step': 1, 'message': 'Generating creative script...', 'percentage': 15}, room=session_id)
            time.sleep(1)
            script_data = generate_script(topic)
            
            if not script_data['narration_script']:
                socketio.emit('error', {'message': 'Failed to generate script. Please try again.'}, room=session_id)
                return
            
            socketio.emit('progress', {'step': 2, 'message': 'Script generated successfully!', 'percentage': 35}, room=session_id)
            
            # Step 2: Generate Audio
            socketio.emit('progress', {'step': 3, 'message': 'Creating natural voice narration...', 'percentage': 55}, room=session_id)
            time.sleep(1)
            audio_path = generate_audio(script_data['narration_script'], topic)
            
            socketio.emit('progress', {'step': 4, 'message': 'Audio generated successfully!', 'percentage': 75}, room=session_id)
            
            # Step 3: Create Video
            socketio.emit('progress', {'step': 5, 'message': 'Combining media and creating final video...', 'percentage': 80}, room=session_id)
            time.sleep(1)
            
            try:
                create_video(script_data['narration_script'], script_data['image_script'], audio_path, topic)
                
                # Video completed - show 100% first
                socketio.emit('progress', {'step': 6, 'message': 'Video assembly complete!', 'percentage': 100}, room=session_id)
                
                # Generate path and filename
                video_filename = f"{topic.replace(' ', '_')}_video.mp4"
                video_path = f"output/{video_filename}"
                
                # Wait to ensure the file exists
                time.sleep(1)
                if os.path.exists(os.path.join("output", video_filename)):
                    # Then send completion event with explicit data
                    socketio.emit('video_complete', {
                        'filename': video_filename,
                        'path': video_path,
                        'status': 'success'
                    }, room=session_id)
                    print(f"Sent video_complete event for: {video_filename}")
                else:
                    socketio.emit('error', {'message': f'Video file not found after generation: {video_filename}'}, room=session_id)
                    
            except Exception as video_error:
                print(f"Error in video creation: {video_error}")
                socketio.emit('error', {'message': f'Failed to create video: {str(video_error)}'}, room=session_id)
        
        except Exception as e:
            print(f"Error in video generation: {e}")
            socketio.emit('error', {'message': f'An error occurred: {str(e)}'}, room=session_id)
    
    # Start video generation in a separate thread
    thread = threading.Thread(target=generate_video_process)
    thread.daemon = True
    thread.start()

@socketio.on('get_random_fact')
def handle_random_fact():
    fact = random.choice(RANDOM_FACTS)
    emit('random_fact', {'fact': fact})

@app.route('/download/<filename>')
def download_video(filename):
    try:
        file_path = os.path.join('output', filename)
        if os.path.exists(file_path):
            # Get file size for Content-Length header
            file_size = os.path.getsize(file_path)
            
            def generate():
                with open(file_path, 'rb') as f:
                    while True:
                        data = f.read(4096)  # Read in chunks
                        if not data:
                            break
                        yield data
            
            response = app.response_class(
                generate(),
                mimetype='video/mp4',
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    'Content-Length': str(file_size),
                    'Content-Type': 'video/mp4'
                }
            )
            return response
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
