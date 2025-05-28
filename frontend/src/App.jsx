import { useState, useRef, useEffect } from 'react';
import { Button, Container, Typography, Box, TextField, Select, MenuItem, InputLabel, FormControl, AppBar, Toolbar, IconButton, Avatar, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { getAuth, signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
import { initializeApp } from 'firebase/app';
import { getStorage, ref, uploadBytes } from 'firebase/storage';
import RecordRTC from 'recordrtc';
import Snackbar from '@mui/material/Snackbar';

// Firebase config (replace with your config)
const firebaseConfig = {
  apiKey: "YOUR_FIREBASE_API_KEY",
  authDomain: "YOUR_FIREBASE_AUTH_DOMAIN",
  projectId: "YOUR_FIREBASE_PROJECT_ID",
  storageBucket: "YOUR_FIREBASE_STORAGE_BUCKET",
  messagingSenderId: "YOUR_FIREBASE_MESSAGING_SENDER_ID",
  appId: "YOUR_FIREBASE_APP_ID"
};

initializeApp(firebaseConfig);
const auth = getAuth();
const storage = getStorage();

export default function App() {
  const [user, setUser] = useState(null);
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState('');
  const [chat, setChat] = useState([]);
  const [recording, setRecording] = useState(false);
  const [recorder, setRecorder] = useState(null);
  const [contextDialog, setContextDialog] = useState(false);
  const [contextText, setContextText] = useState('');
  const [file, setFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const wsRef = useRef(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '' });
  const lastTranscriptRef = useRef('');
  const lastAssistantRef = useRef('');

  // WebSocket setup
  useEffect(() => {
    if (!user) return;
    const ws = new window.WebSocket('ws://localhost:8000/ws/audio');
    ws.binaryType = 'arraybuffer';
    ws.onmessage = async (event) => {
      if (event.data instanceof ArrayBuffer) {
        // Received audio from backend
        const blob = new Blob([event.data], { type: 'audio/mp3' });
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        // Optionally auto-play
        const audio = document.getElementById('audio-player');
        if (audio) {
          audio.src = url;
          audio.play();
        }
        // Add assistant response to chat if available
        if (lastAssistantRef.current) {
          setChat((prev) => [...prev, { role: 'assistant', text: lastAssistantRef.current }]);
          lastAssistantRef.current = '';
        }
      } else if (typeof event.data === 'string') {
        // Optionally handle text messages from backend
      }
    };
    wsRef.current = ws;
    return () => {
      ws.close();
    };
  }, [user]);

  // Send selected voice to backend
  useEffect(() => {
    if (wsRef.current && selectedVoice) {
      wsRef.current.send(JSON.stringify({ voice_id: selectedVoice }));
    }
  }, [selectedVoice]);

  // Google Sign-In
  const signIn = async () => {
    const provider = new GoogleAuthProvider();
    const result = await signInWithPopup(auth, provider);
    setUser(result.user);
    // Fetch voices after login
    fetchVoices();
  };

  // Fetch available voices from backend
  const fetchVoices = async () => {
    // TODO: Add auth token to request
    const res = await fetch('http://localhost:8000/voices');
    const data = await res.json();
    setVoices(data.voices);
    setSelectedVoice(data.voices[0] || '');
  };

  // Start/stop recording
  const handleMic = async () => {
    if (!recording) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const newRecorder = new RecordRTC(stream, { type: 'audio' });
      newRecorder.startRecording();
      setRecorder(newRecorder);
      setRecording(true);
    } else {
      recorder.stopRecording(async () => {
        const blob = recorder.getBlob();
        // Transcribe locally for chat display (optional, or use backend)
        // For now, just show 'You spoke...' placeholder
        const transcript = 'You spoke a message.';
        setChat((prev) => [...prev, { role: 'user', text: transcript }]);
        lastTranscriptRef.current = transcript;
        // Send audio to backend via WebSocket
        if (wsRef.current && blob) {
          const arrayBuffer = await blob.arrayBuffer();
          wsRef.current.send(arrayBuffer);
        }
        setRecording(false);
      });
    }
  };

  // Helper to get Firebase ID token
  const getIdToken = async () => {
    if (auth.currentUser) {
      return await auth.currentUser.getIdToken();
    }
    return null;
  };

  // Upload file for RAG
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    setFile(file);
    if (!file) return;
    const token = await getIdToken();
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch('http://localhost:8000/upload-data', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const data = await res.json();
      setSnackbar({ open: true, message: data.status === 'uploaded' ? 'File uploaded!' : 'Upload failed.' });
    } catch (err) {
      setSnackbar({ open: true, message: 'Upload failed.' });
    }
  };

  // Set context from text
  const handleSetContext = async () => {
    setContextDialog(false);
    if (!contextText) return;
    const token = await getIdToken();
    try {
      const res = await fetch('http://localhost:8000/set-context', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ text: contextText }),
      });
      const data = await res.json();
      setSnackbar({ open: true, message: data.status === 'context set' ? 'Context set!' : 'Failed to set context.' });
    } catch (err) {
      setSnackbar({ open: true, message: 'Failed to set context.' });
    }
  };

  return (
    <Container maxWidth="sm">
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>Sleep Assistant</Typography>
          {user ? (
            <Avatar src={user.photoURL} alt={user.displayName} />
          ) : (
            <Button color="inherit" onClick={signIn}>Sign in with Google</Button>
          )}
        </Toolbar>
      </AppBar>
      <Box mt={4}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel id="voice-select-label">Voice</InputLabel>
          <Select
            labelId="voice-select-label"
            value={selectedVoice}
            label="Voice"
            onChange={e => setSelectedVoice(e.target.value)}
          >
            {voices.map(voice => (
              <MenuItem key={voice} value={voice}>{voice}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <Box display="flex" alignItems="center" gap={2}>
          <IconButton color={recording ? 'error' : 'primary'} onClick={handleMic} size="large">
            <MicIcon />
          </IconButton>
          <Button variant="outlined" component="label" startIcon={<UploadFileIcon />}>
            Upload Doc
            <input type="file" hidden onChange={handleFileUpload} />
          </Button>
          <Button variant="outlined" onClick={() => setContextDialog(true)}>
            Paste Text
          </Button>
        </Box>
        <audio id="audio-player" controls style={{ width: '100%', marginTop: 16 }} />
        <Box mt={4}>
          <Typography variant="h6">Chat</Typography>
          <Box sx={{ minHeight: 200, border: '1px solid #ccc', borderRadius: 2, p: 2, mb: 2 }}>
            {chat.map((msg, i) => (
              <Box key={i} mb={1}>
                <b>{msg.role}:</b> {msg.text}
              </Box>
            ))}
          </Box>
        </Box>
      </Box>
      <Dialog open={contextDialog} onClose={() => setContextDialog(false)}>
        <DialogTitle>Paste Custom Data</DialogTitle>
        <DialogContent>
          <TextField
            multiline
            minRows={4}
            fullWidth
            value={contextText}
            onChange={e => setContextText(e.target.value)}
            label="Custom Data"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setContextDialog(false)}>Cancel</Button>
          <Button onClick={handleSetContext}>Set Context</Button>
        </DialogActions>
      </Dialog>
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ open: false, message: '' })}
        message={snackbar.message}
      />
    </Container>
  );
}
