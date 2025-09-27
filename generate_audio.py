import os
import pyttsx3
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AudioGenerator")

def generate_audio(script, topic):
    os.makedirs("audio", exist_ok=True)
    filename = f"audio/{topic.replace(' ', '_')}.mp3"
    
    try:
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty("voices")
        
        # Try to select a female voice if available
        female_voice = None
        for i, v in enumerate(voices):
            if "female" in v.name.lower() or "female" in v.id.lower() or "zira" in v.name.lower():
                female_voice = v.id
                logger.info(f"Selected female voice: {v.name}")
                break
        
        # If no female voice found, try to select a voice with ID containing 'en'
        if not female_voice:
            for v in voices:
                if 'en' in v.id.lower():
                    female_voice = v.id
                    logger.info(f"Selected English voice: {v.name}")
                    break
        
        # Set the voice if found, otherwise use default
        if female_voice:
            engine.setProperty("voice", female_voice)
        else:
            logger.warning("No suitable voice found, using default")
            
        # Adjust quality settings for better audio
        engine.setProperty("rate", 150)     # Speed of speech
        engine.setProperty("volume", 1.0)   # Volume (0.0 to 1.0)
        
        # Save to file
        logger.info(f"Generating audio to {filename}")
        engine.save_to_file(script, filename)
        engine.runAndWait()
        
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            logger.info("✅ Audio generated successfully.")
            return filename
        else:
            logger.error("Audio file was created but is empty or missing")
            raise RuntimeError("Generated audio file is empty or missing")
            
    except Exception as e:
        logger.error(f"Failed to generate audio: {e}")
        raise RuntimeError(f"Audio generation failed: {e}")
