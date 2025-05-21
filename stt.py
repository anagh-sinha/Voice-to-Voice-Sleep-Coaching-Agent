
import openai

def transcribe_audio(audio_path):
    """
    Transcribe an audio file to text using OpenAI's Whisper model.
    Returns the transcribed text.
    """
    try:
        with open(audio_path, "rb") as audio_file:
            # Use OpenAI Whisper ASR via API
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        # Extract text from the result
        text = transcript.get("text") if isinstance(transcript, dict) else str(transcript)
        return text.strip()
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""
