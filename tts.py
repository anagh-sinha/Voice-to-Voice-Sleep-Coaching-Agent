import pyttsx3

def speak_text(text):
    """
    Convert text to speech and play it aloud using pyttsx3.
    """
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # set speaking rate (words per minute)
        # Optionally, change voice if multiple voices are available:
        # voices = engine.getProperty('voices')
        # engine.setProperty('voice', voices[1].id)  # e.g., use female voice if index 1 exists
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
