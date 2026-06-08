import json
import os
from html import escape
from typing import Any

from dotenv import load_dotenv
from flask import Flask, Response, request
from flask_sock import Sock


load_dotenv()

app = Flask(__name__)
sock = Sock(app)

TELNYX_FRAME_TYPES = {"setup", "prompt", "dtmf", "interrupt", "error"}
CLIENT_FRAME_TYPES = {"text", "play", "sendDigits", "language", "end"}


def log(label: str, value: Any) -> None:
    print(f"[{label}] {json.dumps(value, indent=2, sort_keys=True)}", flush=True)


def public_base_url() -> str:
    configured_url = os.getenv("TELNYX_PUBLIC_BASE_URL", "").strip()
    if configured_url:
        return configured_url.rstrip("/")
    return request.url_root.rstrip("/")


def conversation_relay_websocket_url() -> str:
    configured_url = os.getenv("CONVERSATION_RELAY_WS_URL", "").strip()
    if configured_url:
        return configured_url

    base_url = public_base_url()
    if base_url.startswith("https://"):
        return "wss://" + base_url.removeprefix("https://") + "/ws/conversation-relay"
    if base_url.startswith("http://"):
        return "ws://" + base_url.removeprefix("http://") + "/ws/conversation-relay"
    return base_url.rstrip("/") + "/ws/conversation-relay"


def conversation_relay_action_url() -> str:
    configured_url = os.getenv("CONVERSATION_RELAY_ACTION_URL", "").strip()
    if configured_url:
        return configured_url
    return public_base_url() + "/callbacks/conversation-relay"


def instruction_fetch_texml() -> str:
    websocket_url = escape(conversation_relay_websocket_url(), quote=True)
    action_url = escape(conversation_relay_action_url(), quote=True)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect action="{action_url}">
        <ConversationRelay
            url="{websocket_url}"
            interruptible="none"
            welcomeGreeting="Welcome to the Conversation Relay test app."
            welcomeGreetingInterruptible="none"
            voice="en-US-Standard-A"
            transcriptionProvider="Deepgram"
            dtmfDetection="true"
        />
    </Connect>
</Response>"""


def text_frame(token: str, last: bool = False) -> str:
    return json.dumps({"type": "text", "token": token, "last": last})


def initial_text_frames() -> tuple[dict[str, Any], ...]:
    return (
        {
            "type": "text",
            "token": "This is the first test message from the WebSocket server.",
            "last": False,
        },
        {
            "type": "text",
            "token": "This is the second test message. I will now stop sending.",
            "last": True,
        },
    )


def parse_message(raw_message: str | bytes) -> dict[str, Any]:
    if isinstance(raw_message, bytes):
        return {"frame_type": "binary", "direction": "unknown", "payload": {"bytes": len(raw_message)}}

    try:
        message = json.loads(raw_message)
    except json.JSONDecodeError:
        return {"frame_type": "text_frame", "direction": "unknown", "payload": {"text": raw_message}}

    if not isinstance(message, dict):
        return {"frame_type": "json_value", "direction": "unknown", "payload": message}

    message_type = str(message.get("type") or message.get("event") or "unknown")
    if message_type in TELNYX_FRAME_TYPES:
        direction = "telnyx-to-client"
    elif message_type in CLIENT_FRAME_TYPES:
        direction = "client-to-telnyx"
    else:
        direction = "unknown"
    return {"frame_type": message_type, "direction": direction, "payload": message}


def handle_message(parsed_message: dict[str, Any]) -> None:
    frame_type = parsed_message["frame_type"]

    handlers = {
        "setup": "relay.setup",
        "prompt": "relay.prompt",
        "dtmf": "relay.dtmf",
        "interrupt": "relay.interrupt",
        "error": "relay.error",
        "binary": "relay.binary",
        "text_frame": "relay.text_frame",
        "json_value": "relay.json_value",
        "unknown": "relay.unknown",
    }

    log(handlers.get(frame_type, f"relay.{frame_type}"), parsed_message)


def send_initial_text_frames(ws) -> None:
    for frame in initial_text_frames():
        ws.send(text_frame(frame["token"], last=frame["last"]))
        log("relay.sent", frame)


def parse_action_callback() -> dict[str, Any]:
    raw_body = request.get_data(as_text=True)
    json_body = request.get_json(silent=True)
    return {
        "method": request.method,
        "path": request.path,
        "query": request.args.to_dict(flat=False),
        "form": request.form.to_dict(flat=False),
        "json": json_body,
        "raw_body": raw_body,
        "headers": {
            key: value
            for key, value in request.headers.items()
            if key.lower().startswith("telnyx") or key.lower() in {"content-type", "user-agent"}
        },
    }


@app.route("/texml/inbound", methods=["GET", "POST"])
def texml_inbound() -> Response:
    log("instruction_fetch", request.values.to_dict(flat=False))
    return Response(instruction_fetch_texml(), status=200, mimetype="application/xml")


@app.route("/callbacks/conversation-relay", methods=["GET", "POST"])
def conversation_relay_action_callback() -> Response:
    log("conversation_relay.action", parse_action_callback())
    return Response(status=204)


@sock.route("/ws/conversation-relay")
def conversation_relay_socket(ws) -> None:
    log("relay.connected", {"path": "/ws/conversation-relay"})
    setup_received = False

    while True:
        raw_message = ws.receive()
        if raw_message is None:
            log("relay.disconnected", {})
            break
        parsed_message = parse_message(raw_message)
        handle_message(parsed_message)

        if parsed_message["frame_type"] == "setup" and not setup_received:
            setup_received = True
            send_initial_text_frames(ws)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("TELNYX_APP_PORT", "8000")),
        debug=os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes", "on"},
    )
