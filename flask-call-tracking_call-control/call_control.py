import sys

import telnyx
import os
from urllib.parse import urlunsplit, urlparse
import json
from flask import Flask, request, Response

app = Flask(__name__)


def validate_webhook(req):
    body = req.data.decode("utf-8")
    signature = req.headers.get("Telnyx-Signature-ed25519", None)
    timestamp = req.headers.get("Telnyx-Timestamp", None)

    try:
        event = telnyx.Webhook.construct_event(body, signature, timestamp, 100000000)
    except ValueError:
        print("Error while decoding event!")
        return False
    except telnyx.error.SignatureVerificationError:
        print("Invalid signature!")
        return False
    except Exception as e:
        print("Unknown Error")
        print(e)
        return False

    print("Received event: id={id}, type={type}".format(id=event.data.id, type=event.data.payload.type))
    return True

def handle_call_answered(call):
    # does some stuff
    # lookup who do i need to transfer to
    ## hit the db
    ## build the transfer object
    ## call the transfer command
    return ""


@app.route("/call-control/inbound", methods=["POST"])
def inbound_call():
    valid_webhook = validate_webhook(request)
    if not valid_webhook:
        return "Webhook not verified", 400
    body = json.loads(request.data)
    payload = call_control_id = body["data"]["payload"]
    call_control_id = body["data"]["payload"]["call_control_id"]
    call_session_id = body["data"]["payload"]["call_session_id"]
    call_leg_id = body["data"]["payload"]["call_leg_id"]
    event_type = body["data"]["event_type"]
    webhook_url = urlunsplit((
        request.scheme,
        request.host,
        "/call-control/outbound",
        "", ""))

    call = telnyx.Call()
    call.call_control_id = call_control_id

    try:
        if event_type == "call.initiated":
            call = telnyx.Call(connection_id=os.getenv("TELNYX_CONNECTION_ID"))
            call.call_control_id = body.get("data").get("payload").get("call_control_id")
            call.answer()
        elif event_type == "call.answered":
            transfer_params = {
                "to": "+19198675309",
                "webhook_url": webhook_url
            }
            call.transfer(**transfer_params)
        elif event_type == "call.hangup":
            print(body)
    except Exception as e:
        print("Error processing webhook")
        print(e)
    return Response(status=200)


@app.route("/call-control/outbound", methods=["POST"])
def outbound_call():
    body = json.loads(request.data)
    call_leg_id = body["data"]["payload"]["call_leg_id"]
    print(f"Received call_control event with call_leg_id: {call_leg_id}")
    return Response(status=200)


if __name__ == "__main__":
    telnyx.api_key = ""
    TELNYX_APP_PORT = "8000"
    app.run(port=TELNYX_APP_PORT)
