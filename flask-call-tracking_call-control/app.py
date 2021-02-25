import sys

import telnyx
import os
from urllib.parse import urlunsplit, urlparse
import json
from flask import Flask, request, Response

app = Flask(__name__)


def handle_call_init(call):
    # does some stuff
    return ""


def handle_call_answered(call):
    # does some stuff
    # lookup who do i need to transfer to
    ## hit the db
    ## build the transfer object
    ## call the transfer command
    return ""


@app.route("/call-control/inbound", methods=["POST"])
def inbound_call():
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
            call.answer()
            # handle_call_init(call)
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
