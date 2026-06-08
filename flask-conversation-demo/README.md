# Flask Conversation Relay Test App

Minimal Telnyx Conversation Relay test app.

## What it does

- Responds to TeXML instruction fetch requests at `/texml/inbound`
- Returns `<Connect><ConversationRelay ... /></Connect>`
- Accepts Conversation Relay WebSocket connections at `/ws/conversation-relay`
- Logs Conversation Relay action callbacks at `/callbacks/conversation-relay`
- Logs every incoming WebSocket frame to stdout
- Sends two AsyncAPI `text` frames after the Telnyx `setup` frame is received
- Parses Telnyx-to-customer frames: `setup`, `prompt`, `dtmf`, `interrupt`, `error`
- Parses customer-to-Telnyx frames: `text`, `play`, `sendDigits`, `language`, `end`
- Still logs unknown JSON, non-JSON text frames, JSON scalar values, and binary frames

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
```

## Configure

```text
TELNYX_APP_PORT=8000
TELNYX_PUBLIC_BASE_URL=https://your-public-url
CONVERSATION_RELAY_WS_URL=wss://your-public-url/ws/conversation-relay
CONVERSATION_RELAY_ACTION_URL=https://your-public-url/callbacks/conversation-relay
```

If `CONVERSATION_RELAY_WS_URL` is not set, the app derives it from `TELNYX_PUBLIC_BASE_URL`.
If `CONVERSATION_RELAY_ACTION_URL` is not set, the app derives it from `TELNYX_PUBLIC_BASE_URL`.

Point the Telnyx TeXML application's voice URL to:

```text
https://your-public-url/texml/inbound
```

The generated `<Connect>` includes:

```xml
action="https://your-public-url/callbacks/conversation-relay"
```

Action callback requests are logged to stdout, including method, query params, form data, JSON body, raw body, and Telnyx-related headers.

## Run

```bash
python app.py
```

## Test

```bash
python -m unittest -q
```

Local instruction fetch test:

```bash
curl -X POST http://127.0.0.1:8000/texml/inbound \
  -d 'CallSid=v2:example' \
  -d 'From=+15555550100' \
  -d 'To=+15555550200'
```

After Telnyx sends the `setup` frame, this app sends two Conversation Relay AsyncAPI `TextFrame` messages:

```json
{"type":"text","token":"This is the first test message from the WebSocket server.","last":false}
{"type":"text","token":"This is the second test message. I will now stop sending.","last":true}
```
