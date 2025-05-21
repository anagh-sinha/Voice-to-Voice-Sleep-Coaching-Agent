import os
import openai
from stt import transcribe_audio
from coach import SleepCoach
from tts import speak_text

if __name__ == "__main__":
    # Ensure OpenAI API key is available for STT and LLM
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("Error: OpenAI API key not set. Set OPENAI_API_KEY to use the voice agent.")
        exit(1)
    # Paths to data files
    base_dir = os.path.dirname(os.path.abspath(__file__))
    diary_file = os.path.join(base_dir, "data", "sleep_diary.csv")
    metrics_file = os.path.join(base_dir, "data", "sleep_metrics.json")
    dialogues_file = os.path.join(base_dir, "data", "coaching_dialogues.json")
    # Initialize the coach with data
    coach = SleepCoach(diary_csv_path=diary_file, metrics_json_path=metrics_file, dialogues_json_path=dialogues_file)
    print("Voice Coaching Agent is ready. Provide an audio file path when prompted.")
    print("Type 'q' or 'quit' to exit.")
    while True:
        try:
            audio_path = input("\nEnter path to a recorded audio file (or 'q' to quit): ").strip()
        except KeyboardInterrupt:
            print("\nExiting voice agent.")
            break
        if audio_path.lower() in ['q', 'quit', 'exit']:
            print("Exiting voice agent. Goodbye!")
            break
        if not audio_path:
            continue
        if not os.path.exists(audio_path):
            print("File not found. Please try again.")
            continue
        # Transcribe user speech to text
        user_text = transcribe_audio(audio_path)
        if not user_text:
            print("Transcription failed or resulted in empty text. Try again.")
            continue
        print(f"User (transcribed): {user_text}")
        # Generate coach's response based on the text
        response_text = coach.generate_coach_response(user_text)
        print(f"Coach (text): {response_text}")
        # Speak out the response
        speak_text(response_text)
