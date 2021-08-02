import telnyx
import requests
import os
import json
from texml import answer_texml, join_conference_texml
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, make_response

# Run flask app and set telnyx API Key
app = Flask(__name__)


# Endpoint that can be posted to so users can send a call
@app.route("/texml/inbound", methods=["POST"])
def inbound():
    body = request.form
    texml = answer_texml("/texml/gather")
    return texml, 200


# Endpoint that can be posted to so users can send a call
@app.route("/texml/gather", methods=["POST"])
def gather():
    body = request.form
    digits = body['Digits']
    texml = join_conference_texml(digits)
    return texml, 200, {"ContentType": "application/xml"}


if __name__ == "__main__":
    # Load environment
    load_dotenv()
    telnyx.api_key = os.getenv("TELNYX_API_KEY")
    app.run(port=os.getenv("PORT"), debug=True)
