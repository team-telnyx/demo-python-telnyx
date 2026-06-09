#!/usr/bin/env python3
"""
Flask application for live Speech-to-Text using Telnyx WebSocket API.
Provides a web interface for real-time microphone transcription.
"""

import os
import json
import asyncio
import base64
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import websockets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active WebSocket connections
active_connections = {}


class TelnyxSTTClient:
    """WebSocket client for Telnyx Speech-to-Text API"""

    def __init__(self, api_key, engine="V2", language="en"):
        self.api_key = api_key
        self.engine = engine
        self.language = language
        self.ws = None
        self.is_connected = False

    async def connect(self):
        """Connect to Telnyx STT WebSocket"""
        uri = "wss://rtc.telnyx.com/v2/ai/transcription"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            self.ws = await websockets.connect(uri, extra_headers=headers)
            self.is_connected = True

            # Send initial configuration
            config = {
                "type": "config",
                "model": self.engine,
                "language": self.language,
                "interim_results": True
            }
            await self.ws.send(json.dumps(config))
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    async def send_audio(self, audio_data):
        """Send audio data to STT service"""
        if self.ws and self.is_connected:
            try:
                message = {
                    "type": "input_audio",
                    "audio": audio_data
                }
                await self.ws.send(json.dumps(message))
            except Exception as e:
                print(f"Send audio error: {e}")
                self.is_connected = False

    async def receive_transcription(self, callback):
        """Receive transcription results"""
        if not self.ws:
            return

        try:
            async for message in self.ws:
                data = json.loads(message)
                await callback(data)
        except websockets.exceptions.ConnectionClosed:
            self.is_connected = False
        except Exception as e:
            print(f"Receive error: {e}")
            self.is_connected = False

    async def close(self):
        """Close WebSocket connection"""
        if self.ws:
            try:
                # Send end of stream
                await self.ws.send(json.dumps({"type": "stop"}))
                await self.ws.close()
            except:
                pass
            self.is_connected = False


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('status', {'message': 'Connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

    # Clean up any active connections
    if request.sid in active_connections:
        client = active_connections[request.sid]
        asyncio.create_task(client.close())
        del active_connections[request.sid]


@socketio.on('start_transcription')
def handle_start_transcription(data):
    """Start transcription session"""
    api_key = data.get('api_key')
    engine = data.get('engine', 'V2')
    language = data.get('language', 'en')

    if not api_key:
        emit('error', {'message': 'API key is required'})
        return

    # Create STT client
    client = TelnyxSTTClient(api_key, engine, language)
    active_connections[request.sid] = client

    # Start connection in background
    async def start_connection():
        connected = await client.connect()
        if connected:
            socketio.emit('status', {'message': 'Connected to Telnyx STT'}, room=request.sid)

            # Start receiving transcriptions
            async def on_transcription(data):
                socketio.emit('transcription', data, room=request.sid)

            await client.receive_transcription(on_transcription)
        else:
            socketio.emit('error', {'message': 'Failed to connect to Telnyx STT'}, room=request.sid)

    # Run async task
    asyncio.create_task(start_connection())


@socketio.on('audio_data')
def handle_audio_data(data):
    """Handle incoming audio data from client"""
    if request.sid not in active_connections:
        emit('error', {'message': 'Not connected to STT service'})
        return

    client = active_connections[request.sid]
    audio_base64 = data.get('audio')

    if audio_base64:
        # Send audio to Telnyx
        async def send_audio():
            await client.send_audio(audio_base64)

        asyncio.create_task(send_audio())


@socketio.on('stop_transcription')
def handle_stop_transcription():
    """Stop transcription session"""
    if request.sid in active_connections:
        client = active_connections[request.sid]

        async def stop_connection():
            await client.close()

        asyncio.create_task(stop_connection())
        del active_connections[request.sid]

        emit('status', {'message': 'Transcription stopped'})


if __name__ == '__main__':
    print("=" * 60)
    print("🎤 Telnyx Live STT Application")
    print("=" * 60)
    print("\n✅ Server starting on http://localhost:5000")
    print("\n📋 Instructions:")
    print("   1. Open your browser to http://localhost:5000")
    print("   2. Enter your Telnyx API key")
    print("   3. Configure language and engine settings")
    print("   4. Click 'Start Recording' to begin transcription")
    print("\n" + "=" * 60 + "\n")

    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
