# Telnyx Live Speech-to-Text Application

A real-time web-based speech-to-text application powered by Telnyx STT API with live microphone transcription.

## Features

- **Live Microphone Transcription**: Real-time speech-to-text using your browser's microphone
- **Multi-Language Support**: Support for 14+ languages including English, Spanish, French, German, and more
- **Multiple STT Engines**: Choose between V1 (Standard) and V2 (Enhanced) engines
- **Transcript Management**: Save transcripts as text files and clear when needed
- **Live Statistics**: Track word count and recording duration in real-time
- **Beautiful UI**: Modern, responsive interface with Telnyx branding
- **Secure Configuration**: API key storage in browser's local storage

## Prerequisites

- Python 3.7+
- A Telnyx account with API key
- Modern web browser with microphone access

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Configure the application:
   - Enter your Telnyx API Key
   - Select your preferred STT Engine (V2 recommended)
   - Choose your language
   - Click "Save Configuration"

4. Start transcribing:
   - Click "Start Recording"
   - Allow microphone access when prompted
   - Start speaking
   - Watch the transcription appear in real-time
   - Click "Stop Recording" when done

## Supported Languages

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

## Features

### Configuration
- **API Key**: Your Telnyx API key (stored securely in browser)
- **STT Engine**: Choose between V1 (Standard) or V2 (Enhanced)
- **Language**: Select from 14+ supported languages

### Real-Time Transcription
- Live transcription as you speak
- Interim results shown in real-time
- Final results highlighted with timestamps

### Transcript Management
- Clear transcript with one click
- Save transcript as .txt file
- Word count tracking
- Duration tracking

## Technical Details

### Backend (Flask)
- Flask server with Socket.IO for real-time communication
- WebSocket client for Telnyx STT API
- Audio streaming from browser to Telnyx

### Frontend
- HTML5 with modern CSS
- JavaScript with Socket.IO client
- Web Audio API for microphone access
- Real-time audio processing and streaming

## Troubleshooting

### Microphone Access Denied
Make sure your browser has permission to access the microphone. Check browser settings.

### Connection Failed
- Verify your API key is correct
- Check your internet connection
- Ensure Telnyx API is accessible

### No Transcription
- Speak clearly into your microphone
- Check microphone volume levels
- Try selecting a different language if speaking non-English

## API Documentation

For more information about Telnyx STT API:
- [Telnyx Documentation](https://developers.telnyx.com/)
- [Portal](https://portal.telnyx.com/)

## License

This is a demo application. Check Telnyx terms of service for API usage.
