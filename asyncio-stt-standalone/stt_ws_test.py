import asyncio
import os
import sys
from stt_ws_client import WebSocketClient

# Chunk size for reading audio (simulating real-time stream)
CHUNK_SIZE = 2048

async def file_audio_generator(file_path: str):
    """
    Yields audio chunks from a file.
    
    Args:
        file_path: Path to the audio file.
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    print(f"Reading audio from {file_path}...")
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk

async def start_stt(audio_file: str):
    """
    Starts the STT process using the websocket client.
    
    Args:
        audio_file: Path to the audio file to transcribe.
    """
    client = WebSocketClient(engine="Azure",input_format="mp3")
    
    print(f"Connecting to {client.url}")
    
    audio_gen = file_audio_generator(audio_file)
    
    try:
        async for event in client.connect_and_stream(audio_gen):
            # Check for transcript in the event directly
            if "transcript" in event:
                transcript = event['transcript']
                is_final = event.get('is_final')
                confidence = event.get('confidence')
                print(f"Transcription (Final: {is_final}, Conf: {confidence}): {transcript}")
            elif "error" in event:
                 print(f"Error: {event['error']}")
            else:
                 # Fallback/System messages
                print(f"Received: {event}")
    except KeyboardInterrupt:
        print("Stopping...")
    except Exception as e:
        print(f"An error occurred: {e}")

async def main():
    if len(sys.argv) < 2:
        print("Usage: python stt_ws_test.py <audio_file_path>")
        sys.exit(1)
        
    audio_file = sys.argv[1]
    await start_stt(audio_file)

if __name__ == "__main__":
    asyncio.run(main())
