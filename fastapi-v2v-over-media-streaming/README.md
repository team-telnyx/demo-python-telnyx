# FastAPI Voice-to-Voice over Media Streaming

This FastAPI application demonstrates real-time voice-to-voice conversation using Telnyx's media streaming capabilities and OpenAI's Realtime API. The application creates an AI assistant that can answer phone calls and engage in natural conversations with callers.

## Features

- Real-time bidirectional audio streaming using WebSockets
- Integration with OpenAI's GPT-4 Realtime API for voice responses
- Telnyx Call Control for managing inbound calls
- Voice activity detection (VAD) for natural conversation flow
- G.711 μ-law audio format for telephony compatibility

## Architecture

The application consists of three main components:

1. **Webhook Endpoint** (`/webhooks/`): Receives call events from Telnyx and initiates the call flow
2. **Media Stream Endpoint** (`/media-stream`): Handles WebSocket connections for bidirectional audio streaming
3. **OpenAI Integration**: Connects to OpenAI's Realtime API for AI-powered voice responses

## Prerequisites

- Python 3.8+
- Telnyx account with:
  - An active phone number
  - Call Control application configured
  - API key
- OpenAI account with:
  - Access to OpenAI Realtime API
  - API key

## Installation

1. Clone the repository:
```bash
cd fastapi-v2v-over-media-streaming
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.sample .env
```

4. Edit `.env` and add your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
TELNYX_API_KEY=your_telnyx_api_key_here
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `TELNYX_API_KEY`: Your Telnyx API key (required)
- `PORT`: Server port (default: 6000)

### Customizing the AI Assistant

You can customize the assistant's behavior by modifying these constants in `server.py`:

- `VOICE` (line 27): OpenAI voice model (options: alloy, echo, fable, onyx, nova, shimmer)

## Running the Application

### Local Development

1. Start the server:
```bash
python server.py
```

The server will start on `http://127.0.0.1:6000`

2. Expose your local server using a tunneling service (e.g., ngrok):
```bash
ngrok http 6000
```

### Telnyx Configuration

1. Log in to your [Telnyx Portal](https://portal.telnyx.com)
2. Navigate to your Call Control Application
3. Set the webhook URL to: `https://your-ngrok-address.com/webhooks/`
4. Ensure your phone number is associated with the Call Control Application

## API Endpoints

### `GET /`
Health check endpoint that returns server status.

**Response:**
```json
{
  "message": "Media Stream Server is running!"
}
```

### `POST /webhooks/`
Receives webhook events from Telnyx. Handles call events and initiates media streaming.

### `WebSocket /media-stream`
WebSocket endpoint for bidirectional audio streaming between Telnyx and OpenAI.

## How It Works

1. **Call Initiation**: When a call is received, Telnyx sends a `call.initiated` webhook to the `/webhooks/` endpoint
2. **Call Answer**: The application answers the call and establishes a media stream connection using `stream_bidirectional_mode: rtp`
3. **WebSocket Connection**: Two WebSocket connections are established:
   - One between Telnyx and the FastAPI server
   - One between the FastAPI server and OpenAI's Realtime API
4. **Audio Streaming**: Audio is streamed bidirectionally:
   - Incoming audio from caller → Telnyx → FastAPI → OpenAI
   - AI responses from OpenAI → FastAPI → Telnyx → Caller
5. **Voice Detection**: OpenAI's server-side VAD detects when the caller starts and stops speaking for natural turn-taking


## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **websockets**: WebSocket client library for OpenAI connection
- **python-dotenv**: Environment variable management
- **requests**: HTTP library for Telnyx API calls
- **pydantic**: Data validation using Python type annotations
- **uvicorn**: ASGI server for running FastAPI

## Troubleshooting

### Connection Issues
- Ensure your server is publicly accessible via HTTPS (WebSocket Secure required)
- Verify webhook URL is correctly configured in Telnyx Portal
- Check that both API keys are valid and properly set in `.env`

### Audio Quality Issues
- Verify the audio format is G.711 μ-law on both Telnyx and OpenAI sides
- Check network latency between your server and both APIs
- Monitor console logs for dropped packets or connection errors

## Resources

- [Telnyx Call Control Documentation](https://developers.telnyx.com/docs/api/v2/call-control)
- [Telnyx Media Streaming Guide](https://developers.telnyx.com/docs/v2/call-control/media-streaming)
- [OpenAI Realtime API Documentation](https://platform.openai.com/docs/guides/realtime)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

