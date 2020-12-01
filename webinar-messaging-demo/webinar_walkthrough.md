## Environment setup

* Launch ngrok
* Create messaging profile and callback to ngrok
* Order phone number and associate with messaging profile
* Send message to number and see callback fail
* Create a `.env` file based on `.env.sample`

## Install Packages

```bash
pip install telnyx
pip install python-dotenv
pip install flask
```

## Base Python File

```python
import telnyx
from flask import Flask, request, Response
from dotenv import load_dotenv
import os
import json
from urllib.parse import urlunsplit

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello_world():
  return "Hello World"


if __name__ == "__main__":
    load_dotenv()
    telnyx.api_key = os.getenv("TELNYX_API_KEY")
    telnyx.public_key = os.getenv("TELNYX_PUBLIC_KEY")
    TELNYX_APP_PORT = os.getenv("PORT")
    app.run(port=TELNYX_APP_PORT)
```

## Add inbound handler

```python
@app.route("/messaging/inbound", methods=["POST"])
def inbound_message():
    body = json.loads(request.data)
    message_id = body["data"]["payload"]["id"]
    print(f"Received inbound message with ID: {message_id}")
    return Response(status=200)
```

## Add outbound handler

```python
@app.route("/messaging/outbound", methods=["POST"])
def outbound_message():
    body = json.loads(request.data)
    message_id = body["data"]["payload"]["id"]
    print(f"Received message DLR with ID: {message_id}")
    return Response(status=200)
```

## Expand inbound handler

```python
@app.route("/messaging/inbound", methods=["POST"])
def inbound_message():
    body = json.loads(request.data)
    message_id = body["data"]["payload"]["id"]
    print(f"Received inbound message with ID: {message_id}")
    webhook_url = urlunsplit((
        request.scheme,
        request.host,
        "/messaging/outbound",
        "", ""))
    to_number = body["data"]["payload"]["to"][0]["phone_number"]
    from_number = body["data"]["payload"]["from"]["phone_number"]
    telnyx_request = {
        "from_": to_number,
        "to": from_number,
        "webhook_url": webhook_url,
        "use_profile_webhooks": False,
        "text": "Hello from Telnyx!"
    }
    try:
        telnyx_response = telnyx.Message.create(**telnyx_request)
        telnyx_response.media_urls = ["hey"]
        print(f"Sent message with id: {telnyx_response.id}")
    except Exception as e:
        print("Error sending message")
        print(e)
    return Response(status=200)
```

## Add MMS detection

```python
@app.route("/messaging/inbound", methods=["POST"])
def inbound_message():
    body = json.loads(request.data)
    message_id = body["data"]["payload"]["id"]
    print(f"Received inbound message with ID: {message_id}")
    dlr_url = urlunsplit((
        request.scheme,
        request.host,
        "/messaging/outbound",
        "", ""))
    to_number = body["data"]["payload"]["to"][0]["phone_number"]
    from_number = body["data"]["payload"]["from"]["phone_number"]
    telnyx_request = {
        "from_": to_number,
        "to": from_number,
        "webhook_url": dlr_url,
        "use_profile_webhooks": False,
        "text": "Hello from Telnyx!"
    }
    text = body["data"]["payload"]["text"].strip().lower()
    if text == "dog":
        telnyx_request["media_urls"] = ["https://telnyx-mms-demo.s3.us-east-2.amazonaws.com/small_dog.JPG"]
        telnyx_request["text"] = "Here is a doggo!"
    try:
        telnyx_response = telnyx.Message.create(**telnyx_request)
        telnyx_response.media_urls = ["hey"]
        print(f"Sent message with id: {telnyx_response.id}")
    except Exception as e:
        print("Error sending message")
        print(e)
    return Response(status=200)
```

## Add callback signature validation

```python
def validate_webhook(req):
    body = req.data.decode("utf-8")
    signature = req.headers.get("Telnyx-Signature-ed25519", None)
    timestamp = req.headers.get("Telnyx-Timestamp", None)

    try:
        event = telnyx.Webhook.construct_event(body,
                                               signature,
                                               timestamp,
                                               100000000)
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

    print("Received event: id={id}, type={type}".format(
            id=event.data.id,
            type=event.data.payload.type))
    return True
```

## Update Inbound Message Handler

```python
@app.route("/messaging/inbound", methods=["POST"])
def inbound_message():
    valid_webhook = validate_webhook(request)
    if not valid_webhook:
        return "Webhook not verified", 400
    body = json.loads(request.data)
    message_id = body["data"]["payload"]["id"]
    print(f"Received inbound message with ID: {message_id}")
    dlr_url = urlunsplit((
        request.scheme,
        request.host,
        "/messaging/outbound",
        "", ""))
    text = body["data"]["payload"]["text"].strip().lower()
    to_number = body["data"]["payload"]["to"][0]["phone_number"]
    from_number = body["data"]["payload"]["from"]["phone_number"]
    telnyx_request = {
        "from_": to_number,
        "to": from_number,
        "webhook_url": dlr_url,
        "use_profile_webhooks": False,
        "text": "Hello from Telnyx!"
    }
    if text == "dog":
        telnyx_request["media_urls"] = [MEDIA_URL]
        telnyx_request["text"] = "Here is a doggo!"
    try:
        telnyx_response = telnyx.Message.create(**telnyx_request)
        telnyx_response.media_urls = ["hey"]
        print(f"Sent message with id: {telnyx_response.id}")
    except Exception as e:
        print("Error sending message")
        print(e)
    return Response(status=200)
```