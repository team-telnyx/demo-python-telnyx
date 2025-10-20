from fastapi import FastAPI, WebSocket
import websockets
import os
from dotenv import load_dotenv
import json
from fastapi.responses import Response
import asyncio
from fastapi import FastAPI, Request
from typing import Optional
import requests
from pydantic import BaseModel
# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TELNYX_API_KEY = os.getenv('TELNYX_API_KEY')

if not OPENAI_API_KEY:
    exit(1)

# Initialize FastAPI
app = FastAPI()

# Constants
PROMPT = 'You are a AI assistant. You love to answer any user questions and is prepared to offer some facts about them. Speak in English'
VOICE = 'alloy'
PORT = int(os.getenv('PORT', 6000))  # Allow dynamic port assignment

# List of Event Types to log to the console
LOG_EVENT_TYPES = [
    'response.content.done',
    'rate_limits.updated',
    'response.done',
    'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped',
    'input_audio_buffer.speech_started',
    'session.created'
]

class WebhookData(BaseModel):
    data: dict
    meta: dict = None 

# Root Route
@app.get("/")
async def root():
    return {"message": "Media Stream Server is running!"}

@app.api_route('/webhooks/', methods=["GET", "POST"])
def webhooks_received(webhook_data: WebhookData,
                      request: Request):
    print(f"Webhook received: {webhook_data.data['event_type']}")

    if(webhook_data.data['event_type'] == 'call.initiated'):
         answer(webhook_data.data['payload']['call_control_id'], request.headers.get('host'))
    return {"success": True}

def answer(call_control_id, host):
    print(f"Answering call with call control ID: {call_control_id}")
   
    params = {
         "stream_url":f"wss://{host}/media-stream",
         "stream_bidirectional_mode": "rtp"
    }
    
    print(send_request(f'calls/{call_control_id}/actions/answer', 'POST', params))

@app.websocket("/media-stream")
async def media_stream_endpoint(websocket: WebSocket):
    await websocket.accept()
    print('Client connected')

    async with websockets.connect(
        'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
        extra_headers={
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'OpenAI-Beta': 'realtime=v1'
        }
    ) as openai_ws:
        stream_sid = None

        async def send_session_update():
            session_update = {
                'type': 'session.update',
                'session': {
                    'turn_detection': {'type': 'server_vad'},
                    'input_audio_format': 'g711_ulaw',
                    'output_audio_format': 'g711_ulaw',
                    'voice': VOICE,
                    'instructions': PROMPT,
                    'modalities': ["text", "audio"],
                    'temperature': 0.8,
                }
            }
            print('Sending session update:', json.dumps(session_update))
            await openai_ws.send(json.dumps(session_update))

        # Send initial session update
        print('Connected to the OpenAI Realtime API')
        await send_session_update()

        async def handle_openai_messages():
            try:
                while True:
                    openai_message = await openai_ws.recv()
                    try:
                        response = json.loads(openai_message)

                        if response['type'] in LOG_EVENT_TYPES:
                            print(f"Received event: {response['type']}", response)

                        if response['type'] == 'session.updated':
                            print('Session updated successfully:', response)

                        if response['type'] == 'response.audio.delta' and response.get('delta'):
                            audio_delta = {
                                'event': 'media',
                                'media': {'payload': response['delta']}
                            }
                            await websocket.send_text(json.dumps(audio_delta))
                    except json.JSONDecodeError as e:
                        print('Error processing OpenAI message:', e)
            except websockets.exceptions.ConnectionClosed:
                print('OpenAI WebSocket connection closed')

        async def handle_ws_messages():
            nonlocal stream_sid
            try:
                while True:
                    message = await websocket.receive_text()
                    try:
                        data = json.loads(message)

                        if data['event'] == 'media':
                            audio_append = {
                                'type': 'input_audio_buffer.append',
                                'audio': data['media']['payload']
                            }
                            await openai_ws.send(json.dumps(audio_append))
                        elif data['event'] == 'start':
                            stream_sid = data['stream_id']
                            print('Incoming stream has started', stream_sid)
                        else:
                            print('Received non-media event:', data['event'])
                    except json.JSONDecodeError as e:
                        print('Error processing WS message:', e)
            except websockets.exceptions.ConnectionClosed:
                print('WebSocket connection closed')

        # Run both handlers concurrently
        try:
            await asyncio.gather(
                handle_openai_messages(),
                handle_ws_messages()
            )
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            print('Client disconnected.')
 
def send_request(method, operation = "GET",  parameters = None):
    endpoint = 'https://api.telnyx.com/v2/{0}'.format(method)

    headers = {'Authorization': 'Bearer {0}'.format(TELNYX_API_KEY), 
               'Content-Type': 'application/json'}

    if(operation == 'GET'):
        return requests.get(endpoint, headers = headers, params = parameters)
    elif(operation == 'POST'):
        print(endpoint)
        return requests.post(endpoint, headers = headers, json = parameters)
    elif(operation == 'DELETE'):
        return requests.delete(endpoint, headers = headers)
    elif(operation == 'PATCH'):
        return requests.patch(endpoint, headers = headers, json = parameters) 
    else:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=PORT)