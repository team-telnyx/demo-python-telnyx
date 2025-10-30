import asyncio
import os
import base64
from tts_ws_client import WebSocketClient


def save_audio(audio_data: str, audio_file: str = "audio.wav"):
    """
    Save base64 encoded audio data to file.

    Args:
        audio_data: Base64 encoded audio string
        audio_file: Path to the audio file to save to (default: "audio.wav")
    """
    try:
        # Decode base64 audio data
        binary_data = base64.b64decode(audio_data)

        # Append to audio file
        with open(audio_file, "ab") as f:
            f.write(binary_data)

        print(f"Saved audio chunk to {audio_file} ({len(binary_data)} bytes)")
    except Exception as e:
        print(f"Error saving audio: {e}")



async def start_tts(
    text: str,
    voice_id: str = "Telnyx.NaturalHD.astra",
    model_id: str = "",
    provider: str = "telnyx",
    audio_file: str = "audio.wav"
):
    """
    Test Telnyx TTS streaming with specified parameters.
    Original: WsTest.start_tts_prod/4

    Args:
        voice_id: Voice identifier
        model_id: TTS model identifier
        text: Text to convert to speech
        provider: Provider name (default: "telnyx")
        audio_file: Path to save audio file (default: "audio.wav")
    """
    client = WebSocketClient(voice_id=voice_id, model_id=model_id, provider=provider)

    print(f"Connecting to URL: {client.url}")

    async def send_messages(client):
        # Initialize with settings
        init_text = {
            "text": " "
        }

        # Send text to be converted
        text_msg = {"text": text}

        # Stop signal
        stop_text = {"text": ""}

        await client.send_text(init_text)
        await asyncio.sleep(1)
        await client.send_text(text_msg)
        await asyncio.sleep(1)
        await client.send_text(stop_text)
        await asyncio.sleep(1)

    # Stream and handle events
    async for event in client.connect_and_send(send_messages):
        if event["type"] == "text":
            data = event["data"]
            print(f"Received message: {data}")
            # Save audio if present
            audio_data = data.get("audio")
            if audio_data:
                chunk_file = f"audio_chunk.wav"

                # Save the audio chunk
                save_audio(audio_data, chunk_file)
        elif event["type"] == "binary":
            print(f"Received binary: {len(event['data'])} bytes")


async def main():

    text = "Hello, this is a test"
    print(await start_tts(text))


if __name__ == "__main__":
    asyncio.run(main())
