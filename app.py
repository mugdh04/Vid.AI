from generate_script import generate_script
from generate_audio import generate_audio
from create_video import create_video

import sys

def main(topic):
    print(f"\n🎯 Generating script for topic: {topic}")
    script_data = generate_script(topic)
    narration_script = script_data["narration_script"]
    image_script = script_data["image_script"]

    print("\n🎤 Generating audio...")
    audio_path = generate_audio(narration_script, topic)

    print("\n🎬 Creating video...")
    create_video(narration_script, image_script, audio_path, topic)

if __name__ == "__main__":
    topic = " ".join(sys.argv[1:])
    main(topic)