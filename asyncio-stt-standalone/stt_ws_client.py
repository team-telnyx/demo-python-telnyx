import asyncio
import json
import base64
import os
from typing import Optional, Dict, Any
import websockets
from websockets.client import WebSocketClientProtocol
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class WebSocketClient:
    """
    Python implementation dealing with Telnyx STT.
    Handles WebSocket connections with audio streaming capabilities.
    """

    # Hardcoded Telnyx configuration
    TELNYX_TOKEN = os.getenv("TELNYX_TOKEN")
    
    if not TELNYX_TOKEN:
         raise ValueError("TELNYX_TOKEN environment variable is not set. Please create a .env file with your token.")

    def __init__(self, engine: str = "Deepgram", input_format: str = "wav"):
        """
        Initialize the WebSocket client for Telnyx STT.

        Args:
            engine: STT engine (default: "Deepgram")
            input_format: Audio format (default: "wav")
        """
        
        self.url = f"wss://api.telnyx.com/v2/speech-to-text/transcription?transcription_engine={engine}&input_format={input_format}"

        # Hardcoded Telnyx authorization header
        self.headers = {
            "Authorization": f"Bearer {self.TELNYX_TOKEN}"
        }
        self.ws: Optional[WebSocketClientProtocol] = None

    async def connect(self):
        """Establish WebSocket connection."""
        try:
            self.ws = await websockets.connect(
                self.url,
                extra_headers=self.headers
            )
            print(f"Connected to {self.url}")
        except Exception as e:
            print(f"Connection failed: {e}")
            raise

    async def disconnect(self):
        """Close WebSocket connection."""
        if self.ws:
            await self.ws.close()
            print("Disconnected!")

    async def send_audio(self, audio_data: bytes):
        """
        Send audio data over the WebSocket.

        Args:
            audio_data: Binary audio data
        """
        if not self.ws:
            raise RuntimeError("WebSocket not connected")

        print(f"Sending binary frame of size: {len(audio_data)}")
        await self.ws.send(audio_data)

    async def receive_messages(self):
        """
        Receive messages from the WebSocket as an async generator.
        Yields decoded messages for the caller to handle.

        Yields:
            Dict[str, Any]: Decoded message data with type information
        """
        if not self.ws:
            raise RuntimeError("WebSocket not connected")

        try:
            async for message in self.ws:
                print(f"Message received: {message}")
                yield self._parse_message(message)
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed. Code: {e.code}, Reason: {e.reason}")
        except Exception as e:
            print(f"Error receiving messages: {e}")

    def _parse_message(self, message) -> Dict[str, Any]:
        """
        Parse incoming WebSocket messages.

        Args:
            message: Raw message from WebSocket

        Returns:
            Dict with 'type' and message data
        """
        try:
            if isinstance(message, str):
                # Handle text messages
                return json.loads(message)
                
            # We don't expect binary messages from the server for STT results
            return {"type": "unknown", "data": message}
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}") 
            return {"type": "error", "error": str(e)}
        except Exception as e:
            print(f"Error parsing message: {e}")
            return {"type": "error", "error": str(e)}

    async def connect_and_stream(self, audio_generator):
        """
        Connect to WebSocket and stream audio.
        Returns an async generator for receiving messages.

        Args:
            audio_generator: Async function or iterator that yields audio chunks

        Usage:
            async for event in client.connect_and_stream(audio_chunks):
                # Handle event
                pass
        """
        await self.connect()

        try:
            # Start message receiving task
            stream = self.receive_messages()
            
            # Create a task to send audio
            async def send_loop():
                async for chunk in audio_generator:
                    await self.send_audio(chunk)
                    await asyncio.sleep(0.1) # Small sleep to mimic real-time
                
                print("Finished sending audio, waiting 20s for remaining messages...")
                await asyncio.sleep(20)
                print("20s wait over, closing connection.")
                await self.disconnect()

            send_task = asyncio.create_task(send_loop())

            # Yield messages as they arrive
            async for event in stream:
                yield event
                
            await send_task

        finally:
            await self.disconnect()
