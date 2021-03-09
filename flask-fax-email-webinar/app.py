import re
import telnyx
import os
from urllib.parse import urlparse
import json
import requests
import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, Response
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

app = Flask(__name__)

DB = [
    {
        "email": "@telnyx.com",
        "phone_number": "+"
    }
]


def extract_email(email_string):
    emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", email_string)
    return emails.pop().lower()


def get_phone_number_from_email(email):
    global DB
    for record in DB:
        if record["email"] == email:
            return record["phone_number"]
    return False


def get_email_from_phone_number(phone_number):
    global DB
    for record in DB:
        if record["phone_number"] == phone_number:
            return record["email"]
    return False


def allowed_file(filename):
    allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def download_file(url):
    r = requests.get(url, allow_redirects=True)
    file_name = os.path.basename(urlparse(url).path)
    open(file_name, "wb").write(r.content)
    return file_name


def upload_file(file_path):
    global TELNYX_S3_BUCKET
    s3_client = boto3.client("s3")
    file_name = os.path.basename(file_path)
    try:
        extra_args = {
            "ContentType": "application/octet-stream",
            "ACL": "public-read"
        }
        s3_client.upload_file(
            file_path,
            TELNYX_S3_BUCKET,
            file_name,
            ExtraArgs=extra_args)
    except ClientError as e:
        print("Error uploading file to S3")
        print(e)
        quit()
    return f"https://{TELNYX_S3_BUCKET}.s3.amazonaws.com/{file_name}"


def save_and_upload_attachment_to_s3(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(filename)
        file_url = upload_file(filename)
        return file_url


def send_email(file_name, from_phone_number, to_phone_number, email):
    global MAILGUN_API_KEY
    global MAILGUN_DOMAIN
    auth = ("api", MAILGUN_API_KEY)
    files = [("attachment", (file_name, open(file_name, "rb").read()))]
    email_uri = "https://api.mailgun.net/v3/" + MAILGUN_DOMAIN + "/messages"
    email_result = requests.post(
        email_uri,
        auth=auth,
        files=files,
        data={"from": f"{from_phone_number} <{from_phone_number}@{MAILGUN_DOMAIN}>",
              "to": email,
              "subject": f"Inbound fax to: {to_phone_number}, from: {from_phone_number}",
              "text": f"Inbound fax to: {to_phone_number}, from: {from_phone_number}.\nFiles attached",
              })
    return email_result


@app.route("/faxes", methods=["POST"])
def inbound_message():
    body = json.loads(request.data)
    fax_id = body["data"]["payload"]["fax_id"]
    event_type = body["data"]["event_type"]
    direction = body["data"]["payload"]["direction"]
    if event_type != "fax.received" or direction != "inbound":
        print(f"Received fax event_type: {event_type} to {direction} fax_id: {fax_id}")
        return Response(status=200)
    to_number = body["data"]["payload"]["to"]
    from_number = body["data"]["payload"]["from"]
    media_url = body["data"]["payload"]["media_url"]
    attachment = download_file(media_url)
    email = get_email_from_phone_number(to_number)
    if not email:
        print(f"No association for phone number: {to_number}")
        return Response(status=200)
    try:
        email_response = send_email(attachment, from_number, to_number, email)
        print(f"Sent email with id: {json.loads(email_response.text).get('id')}")
    except Exception as e:
        print("Error sending email")
        print(e)
    return Response(status=200)


@app.route("/email/inbound", methods=["POST"])
def inbound_email():
    global TELNYX_FAX_CONNECTION_ID
    data = dict(request.form)
    to_phone_number = "+" + extract_email(data["To"]).split("@")[0]
    from_email = extract_email(data["From"])
    from_phone_number = get_phone_number_from_email(from_email)
    attachment_count = data["attachment-count"]
    if int(attachment_count) == 0 or not from_phone_number:
        return Response(status=200)
    file = request.files["attachment-1"]
    try:
        file_url = save_and_upload_attachment_to_s3(file)
        fax_response = telnyx.Fax.create(
            connection_id=TELNYX_FAX_CONNECTION_ID,
            to=to_phone_number,
            from_=from_phone_number,
            media_url=file_url
        )
        print(f"Sent fax with fax_id: {fax_response.id}")
    except Exception as e:
        print("Error sending fax")
        print(e)
    return Response(status=200)


@app.route("/", methods=["POST"])
def respond_to_tests():
    return Response(status=200)


if __name__ == "__main__":
    load_dotenv()
    MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
    MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
    TELNYX_S3_BUCKET = os.getenv("TELNYX_S3_BUCKET")
    telnyx.api_key = os.getenv("TELNYX_API_KEY")
    telnyx.public_key = os.getenv("TELNYX_PUBLIC_KEY")
    TELNYX_APP_PORT = os.getenv("TELNYX_APP_PORT")
    TELNYX_FAX_CONNECTION_ID = os.getenv("TELNYX_FAX_CONNECTION_ID")
    app.run(port=TELNYX_APP_PORT)
