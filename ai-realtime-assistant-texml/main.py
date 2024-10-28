import os
import asyncio
import json

import websockets
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    print('Missing OpenAI API key. Please set it in the .env file.')
    exit(1)

# Constants
SYSTEM_MESSAGE = 'You are a helpful and bubbly AI assistant who loves to chat about anything the user is interested about and is prepared to offer them facts.'
VOICE = 'alloy'
PORT = int(os.getenv('PORT', 8000))  # Allow dynamic port assignment

# List of Event Types to log to the console. See OpenAI Realtime API Documentation.
LOG_EVENT_TYPES = [
    'response.content.done',
    'rate_limits.updated',
    'response.done',
    'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped',
    'input_audio_buffer.speech_started',
    'session.created'
]

app = FastAPI()

# Add middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/")
async def root():
    return {"message": "Telnyx Media Stream Server is running!"}

# Route for telnyx to handle incoming and outgoing calls

@app.post("/inbound")
async def incoming_call(request: Request):
    print("Incoming call received")
    headers = request.headers
    
    # Construct the correct relative path to the texml.xml file
    texml_path = os.path.join(os.path.dirname(__file__), 'texml.xml')
    
    try:
        with open(texml_path, 'r') as file:
            texml_response = file.read()
        texml_response = texml_response.replace("{host}", headers.get("host"))
        print(f"TeXML Response: {texml_response}")  # Log the TeXML response
    except FileNotFoundError:
        print(f"File not found at: {texml_path}")
        return PlainTextResponse("TeXML file not found", status_code=500)
    
    return PlainTextResponse(texml_response, media_type="text/xml")

# WebSocket route for media-stream
@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    
    try:
        async with websockets.connect(
                'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
                extra_headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "OpenAI-Beta": "realtime=v1"
                }
        ) as openai_ws:

            async def send_session_update():
                session_update = {
                    "type": "session.update",
                    "session": {
                        "turn_detection": {"type": "server_vad"},
                        "input_audio_format": "g711_ulaw",
                        "output_audio_format": "g711_ulaw",
                        "voice": VOICE,
                        "instructions": SYSTEM_MESSAGE,
                        "modalities": ["text", "audio"],
                        "temperature": 0.8,
                    }
                }
                print("Sending session update:", json.dumps(session_update))
                await openai_ws.send(json.dumps(session_update))

            # Wait to send session update after WebSocket connection is stable
            await asyncio.sleep(0.25)
            await send_session_update()

            async def receive_openai_messages():
                async for message in openai_ws:
                    try:
                        response = json.loads(message)
                        if response.get("type") in LOG_EVENT_TYPES:
                            print(f"Received event: {response['type']}", response)
                        if response.get("type") == "session.updated":
                            print("Session updated successfully:", response)
                        if response.get("type") == "response.audio.delta" and response.get("delta"):
                            audio_delta = {
                                "event": "media",
                                "media": {
                                    "payload": response["delta"]
                                }
                            }
                            await websocket.send_json(audio_delta)
                    except Exception as e:
                        print("Error processing OpenAI message:", e, "Raw message:", message)

            async def receive_telnyx_messages():
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    event_type = message.get("event")
                    if event_type == "media":
                        if openai_ws.open:
                            await openai_ws.send(json.dumps(message))
                    elif event_type == "start":
                        stream_sid = message["stream_id"]
                        print(f"Incoming stream has started: {stream_sid}")
                    else:
                        print(f"Received non-media event: {event_type}")

            # Run OpenAI and Telnyx message receivers concurrently
            await asyncio.gather(receive_openai_messages(), receive_telnyx_messages())

    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print("WebSocket error:", e)

# Start the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
