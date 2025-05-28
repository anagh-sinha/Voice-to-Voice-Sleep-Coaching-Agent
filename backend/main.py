import os
import tempfile
import openai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from firebase_admin import auth, credentials, initialize_app
from starlette.responses import JSONResponse
from elevenlabs import ElevenLabs
from coach import SleepCoach
import asyncio
import json

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
eleven_api_key = os.getenv("ELEVENLABS_API_KEY")

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase Admin SDK init
cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_JSON", "firebase.json"))
try:
    initialize_app(cred)
except Exception:
    pass

# In-memory user context (for demo)
user_context = {}

# ElevenLabs client
el_client = ElevenLabs(api_key=eleven_api_key)

# SleepCoach instance (demo data)
coach = SleepCoach(
    diary_csv_path="data/sleep_diary.csv",
    metrics_json_path="data/sleep_metrics.json",
    dialogues_json_path="data/coaching_dialogues.json"
)

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    selected_voice_id = None
    try:
        while True:
            message = await websocket.receive()
            if "bytes" in message:
                audio_bytes = message["bytes"]
                # Use last selected voice or fallback
                voice_id = selected_voice_id
                if not voice_id:
                    voices = el_client.voices.get_all().voices
                    voice_id = voices[0].voice_id if voices else "EXAVITQu4vr4xnSDxMaL"
                # Save to temp file for Whisper
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_bytes)
                    tmp_path = tmp.name
                # STT: Transcribe audio
                transcript = ""
                try:
                    with open(tmp_path, "rb") as audio_file:
                        transcript_obj = openai.Audio.transcribe("whisper-1", audio_file)
                        transcript = transcript_obj.get("text") if isinstance(transcript_obj, dict) else str(transcript_obj)
                except Exception as e:
                    transcript = ""
                os.remove(tmp_path)
                if not transcript:
                    await websocket.send_bytes(b"")
                    continue
                # RAG: Get context (for demo, use SleepCoach)
                response_text = coach.generate_coach_response(transcript)
                # Send transcript and response as JSON text
                await websocket.send_text(json.dumps({"transcript": transcript, "response": response_text}))
                # TTS: Synthesize response
                try:
                    audio_stream = el_client.text_to_speech.stream(
                        voice_id=voice_id,
                        text=response_text,
                        output_format="mp3_44100_128"
                    )
                    audio_bytes = b"".join(audio_stream)
                    await websocket.send_bytes(audio_bytes)
                except Exception as e:
                    await websocket.send_bytes(b"")
            elif "text" in message:
                # Expecting JSON with voice_id
                try:
                    data = json.loads(message["text"])
                    if "voice_id" in data:
                        selected_voice_id = data["voice_id"]
                except Exception:
                    pass
    except WebSocketDisconnect:
        pass

@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...), user=Depends(auth.verify_id_token)):
    # Save file for RAG context (not implemented, demo only)
    user_context[user["uid"]] = {"file": file.filename}
    return {"status": "uploaded"}

@app.post("/set-context")
async def set_context(text: str, user=Depends(auth.verify_id_token)):
    # Save pasted text for RAG context (not implemented, demo only)
    user_context[user["uid"]] = {"context": text}
    return {"status": "context set"}

@app.get("/voices")
async def get_voices(user=Depends(auth.verify_id_token)):
    # Fetch available ElevenLabs voices
    try:
        voices = el_client.voices.get_all().voices
        return {"voices": [{"id": v.voice_id, "name": v.name} for v in voices]}
    except Exception as e:
        return {"voices": []}

@app.get("/health")
def health():
    return JSONResponse({"status": "ok"}) 