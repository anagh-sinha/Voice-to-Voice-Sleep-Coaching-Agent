# Voice-to-Voice Sleep Coaching Agent

1. **Speech-to-Text (STT)**:
The stt.py module uses OpenAI's Whisper model to transcribe audio input into text.

2. **Data Context**:
The SleepCoach (in coach.py) loads your sleep diary and wearable metrics. When you ask something, it prepares a context string with your latest sleep data (e.g., last night's stats) to personalize the response.

3. **LLM Response**:
The coach formulates a prompt with an instructional system message (defining its role and style), adds the context and your question, and calls OpenAI's GPT-3.5 to generate a helpful answer. If the API call fails, it can fall back to a simple predefined response or an example from coaching_dialogues.json.

4. **Text-to-Speech (TTS)**:
Finally, tts.py uses pyttsx3 to convert the assistant's text reply into spoken words.


## Project Structure
```
Voice-to-Voice-Sleep-Coaching-Agent/
├── stt.py # Speech-to-Text using OpenAI Whisper API
├── coach.py # Sleep coach logic (uses diary/metrics and GPT-3.5)
├── tts.py # Text-to-Speech using pyttsx3
├── voice_app.py # Main script to run the voice agent
├── data/
│ ├── sleep_diary.csv # Sample sleep diary entries
│ ├── sleep_metrics.json # Sample wearable sleep metrics
│ └── coaching_dialogues.json # Sample coaching Q&A examples
└── requirements.txt # Dependencies for Voice-to-Voice-Sleep-Coaching-Agent
```

## Setup and Installation
1. **Install Dependencies**: In the `Voice-to-Voice-Sleep-Coaching-Agent` folder, run:  
   ```bash
   pip install -r requirements.txt

This installs the OpenAI client and pyttsx3 for voice output.

2. **Environment Setup**: Create a `.env` file in the backend directory with the following variables:
   ```
   # OpenAI API Key for Whisper and GPT
   OPENAI_API_KEY=your_openai_api_key_here

   # ElevenLabs API Key for Text-to-Speech
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

   # Firebase Configuration
   FIREBASE_CREDENTIALS_JSON=path_to_your_firebase_credentials.json
   ```

   Make sure to replace the placeholder values with your actual API keys and credentials. Never commit the `.env` file to version control.

3. **Firebase Setup**: 
   - Create a new Firebase project
   - Download your Firebase service account credentials JSON file
   - Place it in a secure location and update the `FIREBASE_CREDENTIALS_JSON` path in your `.env` file
   - Never commit the Firebase credentials file to version control

4. **TTS Additional Setup**:
On Linux, install espeak and ffmpeg if not already present (e.g., sudo apt-get install espeak ffmpeg) for pyttsx3 and audio processing.
On Windows and Mac, pyttsx3 should use the built-in TTS engines by default.

# Running the Voice Coach Agent
Start the voice coaching program by running:
```bash
python voice_app.py
```
You'll be prompted to enter the path to an audio file. For example, record yourself asking "I had trouble sleeping last night, what should I do?" and save it as question.wav. Then at the prompt, enter the path to that file (e.g., C:\\path\\to\\question.wav or ./question.wav). The agent will:
Transcribe your question (displaying it as text for confirmation).
Use your latest diary entry and sleep metrics in crafting a response.

Print the response text and also speak it out loud.

# Example interaction:
```
Voice Coaching Agent is ready. Provide an audio file path when prompted.
Type 'q' or 'quit' to exit.

Enter path to a recorded audio file (or 'q' to quit): ./question.wav
User (transcribed): I had trouble sleeping last night, what should I do?
Coach (text): I'm sorry you had a rough night. According to your diary, you've been struggling. One thing you can try is avoiding screens for an hour before bed and maybe do some light reading. Also, last night you only got 6.8 hours of sleep with a score of 76 – let's aim to improve that by establishing a calming bedtime routine.
```
The agent's spoken response will play through your speakers. You can then record another question as a new audio file and provide its path to continue the dialogue. (Note: The agent, as implemented, uses the latest data each turn but does not carry over conversation context between turns, aside from what's in the diary/metrics.) 

Type 'q' to quit the program at any time.

## Security Notes

1. Never commit sensitive information to version control:
   - API keys
   - Firebase credentials
   - Environment files (.env)
   - Private keys
   - Service account credentials

2. Always use environment variables for sensitive configuration:
   - Store API keys in environment variables
   - Use .env files for local development (and add them to .gitignore)
   - Use secure secret management in production

3. Keep your Firebase credentials secure:
   - Store them in a secure location
   - Use environment variables to reference them
   - Never expose them in client-side code


