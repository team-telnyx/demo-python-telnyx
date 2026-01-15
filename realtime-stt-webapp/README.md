# Real-Time STT Web Application

A modern web application for real-time speech-to-text transcription using Telnyx API. Features a beautiful UI with Telnyx branding, live microphone input, and multi-language support.

## Features

- **Real-Time Microphone Transcription**: Capture audio directly from your microphone and see live transcriptions
- **Multiple STT Engines**: Support for Telnyx STT, AWS, Azure, and Google
- **Multi-Language Support**: Transcribe in English (US/UK), Spanish, French, and German
- **Save Transcripts**: Export your transcriptions to text files with timestamps
- **Modern UI**: Beautiful, responsive interface with Telnyx design system
- **Live Status Indicators**: Visual feedback with recording pulse animation
- **Confidence Scores**: See confidence levels for each transcription

## Prerequisites

- Python 3.8+
- A Telnyx API Key (get one at [telnyx.com](https://telnyx.com))
- Modern web browser with microphone support

## Installation

1. **Navigate to the project directory:**
   ```bash
   cd realtime-stt-webapp
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** (optional - you can also enter the API key in the UI):
   ```env
   TELNYX_TOKEN=your_telnyx_api_token
   ```

## Usage

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Enter your Telnyx API key** in the configuration section

4. **Select your preferred:**
   - STT Engine (Telnyx STT, AWS, Azure, or Google)
   - Language (English US, English UK, Spanish, French, or German)

5. **Click "Start Recording"** to begin transcription

6. **Speak into your microphone** and watch the live transcription appear

7. **Click "Stop Recording"** when finished

8. **Click "Save Transcript"** to export your transcription to a file

## Project Structure

```
realtime-stt-webapp/
├── app.py                    # Flask backend with WebSocket support
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # Main HTML interface
├── static/
│   ├── css/
│   │   └── style.css        # Telnyx design system styles
│   └── js/
│       └── app.js           # Frontend JavaScript logic
└── transcripts/             # Saved transcripts (auto-created)
```

## How It Works

1. **Frontend**: The browser captures audio from your microphone using the Web Audio API
2. **Audio Processing**: Audio is converted to 16-bit PCM format at 16kHz sample rate
3. **WebSocket Communication**: Audio chunks are sent to the Flask backend via Socket.IO
4. **Telnyx STT API**: The backend streams audio to Telnyx's WebSocket STT service
5. **Live Results**: Transcriptions are sent back to the frontend and displayed in real-time

## Design System

The application follows the Telnyx design system:

- **Primary Color**: Telnyx Green (#00C569)
- **Background**: Light Gray (#F8F9FA)
- **Typography**: Inter font family
- **Components**: Rounded corners (16px), subtle shadows, smooth transitions
- **Interactions**: Hover effects, focus states, recording pulse animation

## Configuration Options

### STT Engines
- **Telnyx STT**: Telnyx's native speech-to-text engine
- **AWS**: Amazon Web Services speech recognition
- **Azure**: Microsoft Azure speech services
- **Google**: Google Cloud speech-to-text

### Supported Languages
- English (US) - `en-US`
- English (UK) - `en-GB`
- Spanish - `es-ES`
- French - `fr-FR`
- German - `de-DE`

## Saved Transcripts

Transcripts are automatically saved to the `transcripts/` directory with:
- Timestamp for each transcription segment
- Confidence scores
- Selected language and STT engine
- Formatted for easy reading

Example filename: `patient_note_2026-01-15T10-30-45-123Z.txt`

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

Requires HTTPS or localhost for microphone access.

## Troubleshooting

### "Microphone access denied"
- Grant microphone permissions in your browser
- Ensure you're using HTTPS or localhost

### "Failed to connect to Telnyx STT"
- Verify your API key is correct
- Check your internet connection
- Ensure the selected engine supports your chosen language

### "No audio detected"
- Check your microphone is working and selected as the default input
- Ensure no other application is using the microphone
- Try refreshing the page

## Development

To run in development mode with auto-reload:

```bash
python app.py
```

The server will start on `http://0.0.0.0:5000` with debug mode enabled.

## Security Notes

- API keys are stored in browser localStorage for convenience
- Use environment variables for production deployments
- Consider implementing server-side API key management for production
- Always use HTTPS in production

## License

This project is part of the demo-python-telnyx repository.

## Support

For issues or questions:
- Telnyx API Documentation: [developers.telnyx.com](https://developers.telnyx.com)
- Telnyx Support: [support.telnyx.com](https://support.telnyx.com)

---

**Built with Telnyx Speech-to-Text API**
