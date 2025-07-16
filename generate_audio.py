import pyttsx3
import os

def generate_audio(script, topic):
    os.makedirs("audio", exist_ok=True)
    filename = f"audio/{topic.replace(' ', '_')}.mp3"
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    # pick a female voice (on Windows index 1 is typically Zira)
    if len(voices) > 1:
        engine.setProperty("voice", voices[1].id)
    # optional: adjust rate for natural tone
    engine.setProperty("rate", 150)
    if script:
        engine.save_to_file(script, filename)
        engine.runAndWait()
    else:
        print("❌ No script to generate audio from.")
        return None
    print("✅ Audio generated successfully.")
    return filename
