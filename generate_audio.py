import os
import pyttsx3

def generate_audio(script, topic):
    os.makedirs("audio", exist_ok=True)
    filename = f"audio/{topic.replace(' ', '_')}.mp3"

    engine = pyttsx3.init()
    # Try to select a female voice if available
    voices = engine.getProperty("voices")
    female_voice = None
    for v in voices:
        if "female" in v.name.lower() or "female" in v.id.lower():
            female_voice = v.id
            break
    if female_voice:
        engine.setProperty("voice", female_voice)
    # Adjust rate for smoother, more natural sound
    engine.setProperty("rate", 155)
    # Save to file
    engine.save_to_file(script, filename)
    engine.runAndWait()
    print("✅ Audio generated successfully.")
    return filename
