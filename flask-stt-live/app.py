from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import asyncio
import websockets
import json
import base64
import os
from threading import Thread

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store active WebSocket connections
active_connections = {}

class TelnyxSTTClient:
    def __init__(self, api_key, engine='V2', language='en'):
        self.api_key = api_key
        self.engine = engine
        self.language = language
        self.ws = None
        self.running = False

    async def connect(self):
        """Connect to Telnyx STT WebSocket"""
        url = f"wss://rtc.telnyx.com/v2/speech_analytics/transcription?engine={self.engine}&language={self.language}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            self.ws = await websockets.connect(url, extra_headers=headers)
            self.running = True
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    async def send_audio(self, audio_data):
        """Send audio data to Telnyx STT"""
        if self.ws and self.running:
            try:
                await self.ws.send(audio_data)
            except Exception as e:
                print(f"Error sending audio: {e}")
                self.running = False

    async def receive_transcription(self, session_id):
        """Receive transcription results from Telnyx"""
        if not self.ws:
            return

        try:
            async for message in self.ws:
                if not self.running:
                    break

                try:
                    result = json.loads(message)
                    # Send transcription to the client via Socket.IO
                    socketio.emit('transcription', result, room=session_id)
                except json.JSONDecodeError:
                    print(f"Failed to decode message: {message}")
        except Exception as e:
            print(f"Error receiving transcription: {e}")
        finally:
            self.running = False

    async def close(self):
        """Close the WebSocket connection"""
        self.running = False
        if self.ws:
            await self.ws.close()

def run_async_task(coro):
    """Helper to run async tasks in a new event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")
    if request.sid in active_connections:
        client = active_connections[request.sid]
        # Close the Telnyx connection
        asyncio.run(client.close())
        del active_connections[request.sid]

@socketio.on('start_transcription')
def handle_start_transcription(data):
    """Start a new transcription session"""
    api_key = data.get('api_key')
    engine = data.get('engine', 'V2')
    language = data.get('language', 'en')

    if not api_key:
        emit('error', {'message': 'API key is required'})
        return

    # Create new STT client
    client = TelnyxSTTClient(api_key, engine, language)

    # Connect to Telnyx in a separate thread
    def connect_and_listen():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        connected = loop.run_until_complete(client.connect())
        if not connected:
            socketio.emit('error', {'message': 'Failed to connect to Telnyx STT'}, room=request.sid)
            return

        # Store the connection
        active_connections[request.sid] = client

        # Notify client of successful connection
        socketio.emit('transcription_started', {'status': 'connected'}, room=request.sid)

        # Start listening for transcriptions
        loop.run_until_complete(client.receive_transcription(request.sid))

    thread = Thread(target=connect_and_listen)
    thread.daemon = True
    thread.start()

@socketio.on('audio_data')
def handle_audio_data(data):
    """Handle incoming audio data from client"""
    if request.sid not in active_connections:
        emit('error', {'message': 'No active transcription session'})
        return

    client = active_connections[request.sid]

    # Decode base64 audio data
    try:
        audio_bytes = base64.b64decode(data['audio'])

        # Send to Telnyx in a separate thread
        def send_audio():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(client.send_audio(audio_bytes))

        thread = Thread(target=send_audio)
        thread.daemon = True
        thread.start()
    except Exception as e:
        print(f"Error processing audio: {e}")
        emit('error', {'message': f'Error processing audio: {str(e)}'})

@socketio.on('stop_transcription')
def handle_stop_transcription():
    """Stop the transcription session"""
    if request.sid in active_connections:
        client = active_connections[request.sid]

        def close_connection():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(client.close())

        thread = Thread(target=close_connection)
        thread.daemon = True
        thread.start()

        del active_connections[request.sid]
        emit('transcription_stopped', {'status': 'stopped'})

if __name__ == '__main__':
    print("Starting Flask STT Application...")
    print("Open http://localhost:5000 in your browser")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
