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
