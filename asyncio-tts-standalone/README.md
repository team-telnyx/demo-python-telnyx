# WebSocket TTS Client

Python WebSocket client for testing Telnyx Text-to-Speech (TTS) streaming service.

## Overview

This project provides a Python implementation for connecting to Telnyx TTS WebSocket endpoints. It includes:

- **tts_ws_client.py**: Async WebSocket client with audio streaming capabilities for Telnyx TTS
- **tts_ws_test.py**: Simple test script demonstrating TTS streaming

## Features

- Async WebSocket client using `asyncio` and `websockets`
- Automatic base64 audio decoding and file saving

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your Telnyx token:
```
TELNYX_TOKEN=your_telnyx_bearer_token
```

## Usage

### Basic Usage

Run the test script:
```bash
python tts_ws_test.py
```

This will connect to Telnyx TTS, stream the text "Hello, this is a test", and save the audio to `audio_chunk.wav`.

### Using the Test Function

```python
import asyncio
from tts_ws_test import start_tts

asyncio.run(start_tts(
    text="Hello, this is a test",
    voice_id="Telnyx.NaturalHD.astra",
    model_id="",
    provider="telnyx",
    audio_file="audio.wav"
))
```

### Using the WebSocket Client Directly

```python
import asyncio
from tts_ws_client import WebSocketClient
from tts_ws_test import save_audio

async def example():
    # Create client
    client = WebSocketClient(voice_id="Telnyx.NaturalHD.astra")

    # Define message handler
    async def send_messages(client):
        # Initialize with empty text
        await client.send_text({"text": " "})
        await asyncio.sleep(1)

        # Send actual text to convert
        await client.send_text({"text": "Hello from Telnyx!"})
        await asyncio.sleep(1)

        # Send stop signal
        await client.send_text({"text": ""})
        await asyncio.sleep(1)

    # Stream events and handle audio
    async for event in client.connect_and_send(send_messages):
        if event["type"] == "text":
            audio_data = event["data"].get("audio")
            if audio_data:
                save_audio(audio_data, "output_audio.wav")
        elif event["type"] == "binary":
            print(f"Received binary data: {len(event['data'])} bytes")

asyncio.run(example())
```

## Configuration

The client requires a Telnyx API token, which can be provided via:
- `.env` file with `TELNYX_TOKEN=your_token`
- Environment variable `TELNYX_TOKEN`

## API Endpoints

The client is hardcoded to use the Telnyx TTS endpoint:

- Speech endpoint: `wss://api.telnyx.com/v2/text-to-speech/speech?voice={voice}`

The base URL is configured in `tts_ws_client.py:23`.

## Message Flow

1. **Initialize**: Send initial message with space character `{"text": " "}`
2. **Send Text**: Send actual text to be converted to speech `{"text": "your text"}`
3. **Stop**: Send empty text to signal completion `{"text": ""}`
4. **Stream Events**: Events are yielded via async generator as they arrive

## Event-Driven Architecture

The client uses an async generator pattern:

```python
async for event in client.connect_and_send(send_handler):
    if event["type"] == "text":
        # Handle JSON messages (may contain audio data)
        audio_data = event["data"].get("audio")
    elif event["type"] == "binary":
        # Handle binary messages
        binary_data = event["data"]
    elif event["type"] == "error":
        # Handle parsing errors
        error_msg = event["error"]
```

## Requirements

- Python 3.7+
- websockets >= 12.0
- python-dotenv (for loading `.env` files)

## Troubleshooting

### Connection Issues

If you encounter connection issues:
1. Verify your `TELNYX_TOKEN` environment variable is set correctly
2. Check network connectivity
3. Ensure the Telnyx endpoint URLs are accessible
4. Check console output for connection errors

### No Audio Output

If no audio file is created:
1. Check that the Telnyx API is returning audio data
2. Verify the `audio` field is present in responses
3. Check console output for decode errors
4. Ensure write permissions in the current directory
