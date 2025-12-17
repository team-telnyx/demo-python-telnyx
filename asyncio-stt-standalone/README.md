# Asyncio STT Standalone

A Python standalone project for performing Speech-to-Text (STT) using Telnyx API over WebSockets with `asyncio`.

## Prerequisites

- Python 3.8+
- A Telnyx API Key

## Installation

1.  **Clone the repository** (if you haven't already).
2.  **Navigate to the project directory:**
    ```bash
    cd asyncio-stt-standalone
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Create a `.env` file in the root of the project directory.
2.  Add your Telnyx API Token:

    ```env
    TELNYX_TOKEN=your_telnyx_api_token
    ```

## Usage

You can run the test script `stt_ws_test.py` to transcribe an audio file.

```bash
python stt_ws_test.py <path_to_audio_file>
```

**Example:**

```bash
python stt_ws_test.py my_audio.mp3
```

### Customization

You can modify `stt_ws_test.py` to change the STT engine or input format:

```python
client = WebSocketClient(engine="Azure", input_format="mp3")
# Supported engines: "Deepgram", "Azure", "Telnyx", "Google"
# Supported formats: "wav", "mp3", etc.
```

## Features

- **Asynchronous Streaming:** streams audio chunks to the Telnyx STT service.
- **Real-time Feedback:** Prints connection status and transcription events as they arrive.
- **Robustness:** Handles connection closures and waits for final messages after sending audio.
