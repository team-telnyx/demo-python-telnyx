# Flask Live Speech-to-Text Application

A real-time web-based Speech-to-Text application using Telnyx WebSocket API, Flask, and Socket.IO. Record audio from your microphone and get instant transcriptions in your browser!

## Features

- **Live Microphone Transcription**: Real-time audio streaming and transcription
- **Multi-language Support**: 14+ languages including English, Spanish, French, German, and more
- **Two STT Engines**: V1 (Standard) and V2 (Enhanced) for optimal accuracy
- **Transcript Management**: Download transcriptions as text files
- **Live Statistics**: Track word count and recording duration
- **Beautiful UI**: Modern, responsive interface with Telnyx branding
- **Secure Storage**: API keys stored safely in browser localStorage

## Prerequisites

- Python 3.8 or higher
- A Telnyx account with API key ([Get one here](https://portal.telnyx.com))
- Modern web browser with microphone access

## Installation

1. **Navigate to the project directory:**
   ```bash
   cd flask-stt-live
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Open your web browser and go to:**
   ```
   http://localhost:5000
   ```

3. **Configure the application:**
   - Enter your Telnyx API Key
   - Select STT Engine (V2 recommended)
   - Choose your preferred language
   - Click "Save Configuration"

4. **Start transcribing:**
   - Click "Start Recording"
   - Allow microphone access when prompted
   - Speak into your microphone
   - Watch the transcription appear in real-time!
   - Click "Stop Recording" when done

## Usage

### Configuration
- **API Key**: Your Telnyx API key (required)
- **Engine**: Choose between V1 (Standard) or V2 (Enhanced)
- **Language**: Select from 14+ supported languages

### Recording Controls
- **Start Recording**: Begin capturing audio from your microphone
- **Stop Recording**: End the recording session
- **Clear Transcript**: Remove all transcribed text
- **Save Transcript**: Download the transcription as a .txt file

### Supported Languages
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Dutch (nl)
- Polish (pl)
- Russian (ru)
- Japanese (ja)
- Chinese (zh)
- Korean (ko)
- Arabic (ar)
- Hindi (hi)

## How It Works

1. **Frontend (Browser)**:
   - Captures audio from your microphone using MediaRecorder API
   - Sends audio chunks to Flask server via Socket.IO
   - Displays real-time transcription results

2. **Backend (Flask Server)**:
   - Receives audio data from frontend
   - Forwards audio to Telnyx STT WebSocket API
   - Streams transcription results back to frontend

3. **Telnyx STT API**:
   - Processes audio in real-time
   - Returns both interim and final transcriptions
   - Supports multiple languages and engines

## Troubleshooting

### Microphone Not Working
- Ensure your browser has permission to access the microphone
- Check that no other application is using the microphone
- Try refreshing the page and allowing permissions again

### Connection Issues
- Verify your Telnyx API key is correct
- Check your internet connection
- Ensure the Flask server is running

### No Transcription Appearing
- Make sure you've saved the configuration before starting
- Verify the selected language matches what you're speaking
- Try using the V2 engine for better accuracy

## Technical Stack

- **Backend**: Flask, Flask-SocketIO, WebSockets
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Socket.IO Client
- **API**: Telnyx Speech-to-Text WebSocket API

## Security Notes

- API keys are stored in browser localStorage (not sent to any third party)
- All communication with Telnyx uses secure WebSocket (wss://)
- Audio data is streamed in real-time and not stored on the server

## License

This project is provided as a demonstration of Telnyx STT capabilities.

## Support

For issues or questions about:
- **Telnyx API**: Visit [Telnyx Support](https://support.telnyx.com)
- **This Application**: Check the [GitHub repository](https://github.com/team-telnyx/demo-python-telnyx)

## Credits

Built with Telnyx Speech-to-Text API
