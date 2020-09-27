# Title

⏱ **30 minutes build time || [Github Repo]()**

## Introduction

Telnyx's messaging API supports both MMS and SMS messsages. Inbound multimedia messaging (MMS) messages include an attachment link in the webhook. The link and corresponding media should be treated as ephemeral and you should save any important media to a media storage (such as AWS S3) of your own.


## What you can do

At the end of this tutorial you'll have an application that:

* Receives an inbound message (SMS or MMS)
* Iterates over any media attachments and downloads the remote attachment locally
* Uploads the same attachment to AWS S3
* Sends the attachments back to the same phone number that originally sent the message


## Pre-reqs & technologies

* Completed or familiar with the [Receiving SMS & MMS Quickstart](docs/v2/messaging/quickstarts/receiving-sms-and-mms)
* A working [Messaging Profile](https://portal.telnyx.com/#/app/messaging) with a phone number enabled for SMS & MMS.
* Ability to receive webhooks (with something like [ngrok](docs/v2/development/ngrok))
* [Familiarity with Flask](https://flask.palletsprojects.com/)
* [Python & PIP](/docs/v2/development/dev-env-setup?lang=python&utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) installed
* AWS Account setup with proper profiles and groups with IAM for S3. See the [Quickstart](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) for more information.
* Previously created S3 bucket with public permissions available.


## Setup

### Telnyx Portal configuration

Be sure to have a [Messaging Profile](https://portal.telnyx.com/#/app/messaging) with a phone number enabled for SMS & MMS and webhook URL pointing to your service (using ngrok or similar)

### Install packages via PIP

```shell
pip install telnyx
pip install boto3
pip install flask
pip install dotenv
pip install requests
```

This will create `Pipfile` file with the packages needed to run the application.

### Setting environment variables

The following environmental variables need to be set

| Variable               | Description                                                                                                                                              |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `TELNYX_API_KEY`       | Your [Telnyx API Key](https://portal.telnyx.com/#/app/api-keys?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)              |
| `TELNYX_PUBLIC_KEY`    | Your [Telnyx Public Key](https://portal.telnyx.com/#/app/account/public-key?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) |
| `TELNYX_APP_PORT`      | **Defaults to `8000`** The port the app will be served                                                                                                   |
| `AWS_PROFILE`          | Your AWS profile as set in `~/.aws`                                                                                                                      |
| `AWS_REGION`           | The region of your S3 bucket                                                                                                                             |
| `TELNYX_MMS_S3_BUCKET` | The name of the bucket to upload the media attachments                                                                                                   |

### .env file

This app uses the excellent [python-dotenv](https://github.com/theskumar/python-dotenv) package to manage environment variables.

Make a copy of the file below, add your credentials, and save as `.env` in the root directory.

```
TELNYX_API_KEY=
TELNYX_PUBLIC_KEY=
TENYX_APP_PORT=8000
AWS_PROFILE=
AWS_REGION=
TELNYX_MMS_S3_BUCKET=
```


## Code-along

We'll use a singe `app.py` file to build the MMS application.

```
touch app.py
```

### Setup Flask Server

```python
import telnyx
import os
from urllib.parse import urlunsplit, urlparse
import json
import requests
import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, Response
from dotenv import load_dotenv

app = Flask(__name__)

## Will add more flask code
## ..
## ..

## Load env vars and start flask server
if __name__ == "__main__":
    load_dotenv()
    TELNYX_MMS_S3_BUCKET = os.getenv("TELNYX_MMS_S3_BUCKET")
    telnyx.api_key = os.getenv("TELNYX_API_KEY")
    TELNYX_APP_PORT = os.getenv("TELNYX_APP_PORT")
    app.run(port=TELNYX_APP_PORT)

```

## Receiving Webhooks

Now that you have setup your auth token, phone number, and connection, you can begin to use the API Library to send/receive SMS & MMS messages. First, you will need to setup an endpoint to receive webhooks for inbound messages & outbound message Delivery Receipts (DLR).

### Basic Routing & Functions

The basic overview of the application is as follows:

1. Verify webhook & create TelnyxEvent
2. Extract information from the webhook
3. Iterate over any media and download/re-upload to S3 for each attachment
4. Send the message back to the phone number from which it came
5. Acknowledge the status update (DLR) of the outbound message

### Media Download & Upload Functions

Before diving into the inbound message handler, first we'll create a few functions to manage our attachments.

* `download_file` saves the content from a URL to disk
* `upload_file` uploads the file passed to AWS S3 (and makes object public)
* `media_downloader_uploader` calls the download function and passes result to upload function

```python
def download_file(url):
    r = requests.get(url, allow_redirects=True)
    file_name = os.path.basename(urlparse(url).path)
    open(file_name, "wb").write(r.content)
    return file_name


def upload_file(file_path):
    global TELNYX_MMS_S3_BUCKET
    s3_client = boto3.client("s3")
    file_name = os.path.basename(file_path)
    try:
        extra_args = {
            "ContentType": "application/octet-stream",
            "ACL": "public-read"
        }
        s3_client.upload_file(
            file_path,
            TELNYX_MMS_S3_BUCKET,
            file_name,
            ExtraArgs=extra_args)
    except ClientError as e:
        print("Error uploading file to S3")
        print(e)
        quit()
    return f"https://{TELNYX_MMS_S3_BUCKET}.s3.amazonaws.com/{file_name}"


def media_downloader_uploader(url):
    file_location = download_file(url)
    file_url = upload_file(file_location)
    return file_url
```

### Inbound Message Handling

Now that we have the functions to manage the media, we can start receiving inbound MMS's

The flow of our function is (at a high level):
1. Extract relevant information from the webhook
2. Build the `webhook_url` to direct the DLR to a new endpoint
3. Iterate over any attachments/media and call our `media_downloader_uploader` function
4. Send the outbound message back to the original sender with the media attachments


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
    medias = body["data"]["payload"]["media"]
    media_urls = list(map(lambda media: media_downloader_uploader(media["url"]), medias))
    try:
        telnyx_response = telnyx.Message.create(
            from_=to_number,
            to=from_number,
            text="👋 Hello World",
            media_urls=media_urls,
            webhook_url=dlr_url,
            use_profile_webhooks=False
        )
        print(f"Sent message with id: {telnyx_response.id}")
    except Exception as e:
        print("Error sending message")
        print(e)
    return Response(status=200)
```

### Outbound Message Handling

As we defined our `webhook_url` path to be `/messaging/outbound` we'll need to create a function that accepts a POST request to that path within messaging.js.

```python
@app.route("/messaging/outbound", methods=["POST"])
def outbound_message():
    body = json.loads(request.data)
    message_id = body["data"]["payload"]["id"]
    print(f"Received message DLR with ID: {message_id}")
    return Response(status=200)
```

### Final app.py

All together the app.py should look something like:

```python
import telnyx
import os
from urllib.parse import urlunsplit, urlparse
import json
import requests
import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, Response
from dotenv import load_dotenv

app = Flask(__name__)


def download_file(url):
    r = requests.get(url, allow_redirects=True)
    file_name = os.path.basename(urlparse(url).path)
    open(file_name, "wb").write(r.content)
    return file_name


def upload_file(file_path):
    global TELNYX_MMS_S3_BUCKET
    s3_client = boto3.client("s3")
    file_name = os.path.basename(file_path)
    try:
        extra_args = {
            "ContentType": "application/octet-stream",
            "ACL": "public-read"
        }
        s3_client.upload_file(
            file_path,
            TELNYX_MMS_S3_BUCKET,
            file_name,
            ExtraArgs=extra_args)
    except ClientError as e:
        print("Error uploading file to S3")
        print(e)
        quit()
    return f"https://{TELNYX_MMS_S3_BUCKET}.s3.amazonaws.com/{file_name}"


def media_downloader_uploader(url):
    file_location = download_file(url)
    file_url = upload_file(file_location)
    return file_url


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
    medias = body["data"]["payload"]["media"]
    media_urls = list(map(lambda media: media_downloader_uploader(media["url"]), medias))
    try:
        telnyx_response = telnyx.Message.create(
            from_=to_number,
            to=from_number,
            text="👋 Hello World",
            media_urls=media_urls,
            webhook_url=dlr_url,
            use_profile_webhooks=False
        )
        print(f"Sent message with id: {telnyx_response.id}")
    except Exception as e:
        print("Error sending message")
        print(e)
    return Response(status=200)


@app.route("/messaging/outbound", methods=["POST"])
def outbound_message():
    body = json.loads(request.data)
    message_id = body["data"]["payload"]["id"]
    print(f"Received message DLR with ID: {message_id}")
    return Response(status=200)


if __name__ == "__main__":
    load_dotenv()
    TELNYX_MMS_S3_BUCKET = os.getenv("TELNYX_MMS_S3_BUCKET")
    telnyx.api_key = os.getenv("TELNYX_API_KEY")
    TELNYX_APP_PORT = os.getenv("TELNYX_APP_PORT")
    app.run(port=TELNYX_APP_PORT)

```

## Usage

Start the server `python app.py`

When you are able to run the server locally, the final step involves making your application accessible from the internet. So far, we've set up a local web server. This is typically not accessible from the public internet, making testing inbound requests to web applications difficult.

The best workaround is a tunneling service. They come with client software that runs on your computer and opens an outgoing permanent connection to a publicly available server in a data center. Then, they assign a public URL (typically on a random or custom subdomain) on that server to your account. The public server acts as a proxy that accepts incoming connections to your URL, forwards (tunnels) them through the already established connection and sends them to the local web server as if they originated from the same machine. The most popular tunneling tool is `ngrok`. Check out the [ngrok setup](/docs/v2/development/ngrok) walkthrough to set it up on your computer and start receiving webhooks from inbound messages to your newly created application.

Once you've set up `ngrok` or another tunneling service you can add the public proxy URL to your Inbound Settings  in the Mission Control Portal. To do this, click  the edit symbol [✎] next to your Messaging Profile. In the "Inbound Settings" > "Webhook URL" field, paste the forwarding address from ngrok into the Webhook URL field. Add `messaging/inbound` to the end of the URL to direct the request to the webhook endpoint in your  server.

For now you'll leave “Failover URL” blank, but if you'd like to have Telnyx resend the webhook in the case where sending to the Webhook URL fails, you can specify an alternate address in this field.

##### Callback URLs For Telnyx Applications

| Callback Type                    | URL                              |
|:---------------------------------|:---------------------------------|
| Inbound Message Callback         | `{ngrok-url}/messaging/inbound`  |
| Outbound Message Status Callback | `{ngrok-url}/messaging/outbound` |


Once everything is setup, you should now be able to:
* Text your phone number and receive a response!
* Send a picture to your phone number and get that same picture right back!

