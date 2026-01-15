import asyncio
import json
import os
import base64
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import websockets
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store active connections
active_connections = {}

class TelnyxSTTClient:
    def __init__(self, api_key, engine="Telnyx", language="en-US"):
        self.api_key = api_key
        self.engine = engine
        self.language = language
        self.ws = None
        self.is_connected = False

    async def connect(self):
        """Connect to Telnyx STT WebSocket"""
        url = f"wss://api.telnyx.com/v2/speech-to-text/transcription?transcription_engine={self.engine}&input_format=raw&sample_rate=16000&encoding=linear16&language={self.language}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            self.ws = await websockets.connect(url, extra_headers=headers)
            self.is_connected = True
            print(f"Connected to Telnyx STT with engine: {self.engine}, language: {self.language}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    async def send_audio(self, audio_data):
        """Send audio data to Telnyx STT"""
        if self.ws and self.is_connected:
            try:
                await self.ws.send(audio_data)
            except Exception as e:
                print(f"Error sending audio: {e}")
                self.is_connected = False

    async def receive_messages(self, callback):
        """Receive transcription results"""
        if not self.ws:
            return

        try:
            async for message in self.ws:
                data = json.loads(message)
                await callback(data)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            print(f"Error receiving messages: {e}")
            self.is_connected = False

    async def disconnect(self):
        """Disconnect from Telnyx STT"""
        if self.ws:
            await self.ws.close()
            self.is_connected = False
            print("Disconnected from Telnyx STT")


async def handle_stt_connection(session_id, api_key, engine, language):
    """Handle STT connection for a session"""
    client = TelnyxSTTClient(api_key, engine, language)

    if not await client.connect():
        socketio.emit('error', {'message': 'Failed to connect to Telnyx STT'}, room=session_id)
        return

    active_connections[session_id] = client
    socketio.emit('connected', {'message': 'Connected to Telnyx STT'}, room=session_id)

    async def on_transcript(data):
        """Callback for transcript data"""
        socketio.emit('transcript', data, room=session_id)

    # Listen for transcripts
    await client.receive_messages(on_transcript)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/save-transcript', methods=['POST'])
def save_transcript():
    """Save transcript to file"""
    try:
        data = request.json
        transcript = data.get('transcript', '')
        filename = data.get('filename', f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

        # Create transcripts directory if it doesn't exist
        os.makedirs('transcripts', exist_ok=True)

        filepath = os.path.join('transcripts', filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(transcript)

        return jsonify({'success': True, 'filepath': filepath})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('ready', {'message': 'Connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    session_id = request.sid

    # Clean up connection
    if session_id in active_connections:
        client = active_connections[session_id]
        asyncio.run(client.disconnect())
        del active_connections[session_id]


@socketio.on('start_stt')
def handle_start_stt(data):
    """Start STT session"""
    session_id = request.sid
    api_key = data.get('api_key')
    engine = data.get('engine', 'Telnyx')
    language = data.get('language', 'en-US')

    if not api_key:
        emit('error', {'message': 'API key is required'})
        return

    # Map engine names
    engine_map = {
        'Telnyx STT': 'Telnyx',
        'AWS': 'Deepgram',
        'Azure': 'Azure',
        'Google': 'Google'
    }
    engine = engine_map.get(engine, engine)

    # Start STT connection in background
    def start_connection():
        asyncio.run(handle_stt_connection(session_id, api_key, engine, language))

    import threading
    thread = threading.Thread(target=start_connection)
    thread.daemon = True
    thread.start()


@socketio.on('stop_stt')
def handle_stop_stt():
    """Stop STT session"""
    session_id = request.sid

    if session_id in active_connections:
        client = active_connections[session_id]
        asyncio.run(client.disconnect())
        del active_connections[session_id]
        emit('stopped', {'message': 'STT stopped'})


@socketio.on('audio_data')
def handle_audio_data(data):
    """Receive audio data from client"""
    session_id = request.sid

    if session_id in active_connections:
        client = active_connections[session_id]

        # Decode base64 audio data
        audio_bytes = base64.b64decode(data['audio'])

        # Send to Telnyx STT
        asyncio.run(client.send_audio(audio_bytes))


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
