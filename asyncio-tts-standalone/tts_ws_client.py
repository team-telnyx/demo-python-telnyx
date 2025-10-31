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
    Python implementation of the Elixir WebSocketExample module.
    Handles WebSocket connections with audio streaming capabilities.
    Hardcoded to use Telnyx TTS endpoint only.
    """

    # Hardcoded Telnyx configuration
    TELNYX_TOKEN = os.getenv("TELNYX_TOKEN")
    TELNYX_BASE_URL = "wss://api.telnyx.com/v2/text-to-speech"

    if not TELNYX_TOKEN:
        raise ValueError("TELNYX_TOKEN environment variable is not set. Please create a .env file with your token.")

    def __init__(self, voice_id: str):
        """
        Initialize the WebSocket client for Telnyx TTS.

        Args:
            voice_id: Voice identifier for TTS
        """
        
        self.url = f"{self.TELNYX_BASE_URL}/speech?voice={voice_id}"

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

    async def send_text(self, message: Dict[str, Any]):
        """
        Send a text message over the WebSocket.

        Args:
            message: Dictionary to be JSON-encoded and sent
        """
        if not self.ws:
            raise RuntimeError("WebSocket not connected")

        json_msg = json.dumps(message)
        print(f"Sending text frame with payload: {json_msg}")
        await self.ws.send(json_msg)

    async def stream_messages(self):
        """
        Stream messages from the WebSocket as an async generator.
        Yields decoded messages for the caller to handle.

        Yields:
            Dict[str, Any]: Decoded message data with type information
        """
        if not self.ws:
            raise RuntimeError("WebSocket not connected")

        try:
            async for message in self.ws:
                yield self._parse_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
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
                data = json.loads(message)
                return {
                    "type": "text",
                    "data": data
                }
            elif isinstance(message, bytes):
                # Handle binary messages
                return {
                    "type": "binary",
                    "data": message
                }
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
            return {"type": "error", "error": str(e)}
        except Exception as e:
            print(f"Error parsing message: {e}")
            return {"type": "error", "error": str(e)}

    async def connect_and_send(self, send_handler):
        """
        Connect to WebSocket and run send handler.
        Returns an async generator for streaming messages.

        Args:
            send_handler: Async function that takes the client and sends messages

        Usage:
            async for event in client.connect_and_send(send_messages):
                # Handle event
                pass
        """
        await self.connect()

        try:
            # Start message streaming
            stream = self.stream_messages()

            # Run send handler in background
            send_task = asyncio.create_task(send_handler(self))

            # Yield messages as they arrive
            async for event in stream:
                yield event

            # Wait for send task to complete
            await send_task

        finally:
            await self.disconnect()
