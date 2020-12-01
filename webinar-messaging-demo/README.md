<div align="center">

# Telnyx-Python MMS and SMS Getting Started

![Telnyx](../logo-dark.png)

Sample application demonstrating Telnyx-Python SMS and MMS attachments

</div>

## Documentation & Tutorial

The full documentation and tutorial is available on [developers.telnyx.com](https://developers.telnyx.com/)

## Pre-Reqs

You will need to set up:

* [Telnyx Account](https://telnyx.com/sign-up?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
* [Telnyx Phone Number](https://portal.telnyx.com/#/app/numbers/my-numbers?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) enabled with:
  * [Telnyx Messaging Profile](https://portal.telnyx.com/#/app/messaging)
* Ability to receive webhooks (with something like [ngrok](https://developers.telnyx.com/docs/v2/development/ngrok?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link))
* [Python & PIP](/docs/v2/development/dev-env-setup?lang=python&utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) installed

## What you can do

* Send an SMS or MMS and receive an auto response based on the "text" you send
* Send those file as an MMS via Telnyx

## Usage

The following environmental variables need to be set

| Variable               | Description                                                                                                                                              |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `TELNYX_API_KEY`       | Your [Telnyx API Key](https://portal.telnyx.com/#/app/api-keys?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)              |
| `TELNYX_PUBLIC_KEY`    | Your [Telnyx Public Key](https://portal.telnyx.com/#/app/account/public-key?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) |
| `PORT`      | **Defaults to `8000`** The port the app will be served                                                                                                   |

### .env file

This app uses the excellent [python-dotenv](https://github.com/theskumar/python-dotenv) package to manage environment variables.

Make a copy of [`.env.sample`](./.env.sample) and save as `.env` and update the variables to match your creds.

```
TELNYX_PUBLIC_KEY="+kWXUag92mcUMFQopVlff7ctD/m2S/IoXv+AlI1/5a0="
TELNYX_API_KEY="KEY0RTHKsApNgH"
PORT=8000
```

### Callback URLs For Telnyx Applications

| Callback Type                    | URL                              |
|:---------------------------------|:---------------------------------|
| Inbound Message Callback         | `{ngrok-url}/messaging/inbound`  |
| Outbound Message Status Callback | `{ngrok-url}/messaging/outbound` |

## Install

### Environment setup

#### Ngrok

This application is served on the port defined in the runtime environment (or in the `.env` file). Be sure to launch [ngrok](https://developers.telnyx.com/docs/v2/development/ngrok?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) for that port

```
./ngrok http 8000
```

> Terminal should look _something_ like

```
ngrok by @inconshreveable                                                                                                                               (Ctrl+C to quit)

Session Status                online
Account                       Little Bobby Tables (Plan: Free)
Version                       2.3.35
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    http://your-url.ngrok.io -> http://localhost:8000
Forwarding                    https://your-url.ngrok.io -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

At this point you can point your application to generated ngrok URL + path  (Example: `http://{your-url}.ngrok.io/messaging/inbound`).

### Telnyx Portal Setup

In the [Portal](https://portal.telnyx.com/)

* Create messaging profile and callback to ngrok
* Order phone number and associate with messaging profile

### Install Packages

```bash
pip install telnyx
pip install python-dotenv
pip install flask
```

## Code-along

Create an `app.py` file to host your application

### Base Python File

Copy/paste the below into your app.py file to load the basic application

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

### Add inbound handler

Add the following route to receive and acknowledge webhooks from Telnyx

```python
@app.route("/messaging/inbound", methods=["POST"])
def inbound_message():
    body = json.loads(request.data)
    message_id = body["data"]["payload"]["id"]
    print(f"Received inbound message with ID: {message_id}")
    return Response(status=200)
```

### Add outbound handler

Add the following route to receive and acknowledge webhooks about Outbound messages from Telnyx

```python
@app.route("/messaging/outbound", methods=["POST"])
def outbound_message():
    body = json.loads(request.data)
    message_id = body["data"]["payload"]["id"]
    print(f"Received message DLR with ID: {message_id}")
    return Response(status=200)
```

### Expand inbound handler

Update the inbound function to auto respond to the inbound text message

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
        print(f"Sent message with id: {telnyx_response.id}")
    except Exception as e:
        print("Error sending message")
        print(e)
    return Response(status=200)
```

### Add MMS detection

Update the inbound function to check the `text` contents of the sms and send an MMS if the text is "dog"

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
        print(f"Sent message with id: {telnyx_response.id}")
    except Exception as e:
        print("Error sending message")
        print(e)
    return Response(status=200)
```

## Add callback signature validation

Create a new function to validate webhooks are indeed from Telnyx

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

### Update Inbound Message Handler

Then update the inbound function to call the validate function with the request and return `400` if webhook is not validated

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

### Run

Start the server `python app.py`

When you are able to run the server locally, the final step involves making your application accessible from the internet. So far, we've set up a local web server. This is typically not accessible from the public internet, making testing inbound requests to web applications difficult.

The best workaround is a tunneling service. They come with client software that runs on your computer and opens an outgoing permanent connection to a publicly available server in a data center. Then, they assign a public URL (typically on a random or custom subdomain) on that server to your account. The public server acts as a proxy that accepts incoming connections to your URL, forwards (tunnels) them through the already established connection and sends them to the local web server as if they originated from the same machine. The most popular tunneling tool is `ngrok`. Check out the [ngrok setup](/docs/v2/development/ngrok) walkthrough to set it up on your computer and start receiving webhooks from inbound messages to your newly created application.

Once you've set up `ngrok` or another tunneling service you can add the public proxy URL to your Inbound Settings  in the Mission Control Portal. To do this, click  the edit symbol [✎] next to your Messaging Profile. In the "Inbound Settings" > "Webhook URL" field, paste the forwarding address from ngrok into the Webhook URL field. Add `messaging/inbound` to the end of the URL to direct the request to the webhook endpoint in your  server.

For now you'll leave “Failover URL” blank, but if you'd like to have Telnyx resend the webhook in the case where sending to the Webhook URL fails, you can specify an alternate address in this field.

Once everything is setup, you should now be able to:
* Text your phone number and receive a response!
* Send 'dog' to the phone number and get a doggo back!
