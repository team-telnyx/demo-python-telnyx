import telnyx
import requests
import os
import json
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, make_response

# Load environment
load_dotenv()

# Run flask app and set telnyx API Key
app = Flask(__name__)
telnyx.api_key = os.getenv("TELNYX_API_KEY")

# Homepage that allows user to enter a number to call
@app.route("/")
def home():
    return render_template("messageform.html")

# Endpoint that can be posted to so users can send a call
@app.route("/outbound", methods=["POST"])
def outbound():
    number = request.form["to_number"]
    try:
        telnyx.Call.create(connection_id=os.getenv("TELNYX_CONNECTION_ID"), to=number, from_=os.getenv("TELNYX_NUMBER"))
        return render_template("messagesuccess.html")
    except:
        print("An error occurred")
        return render_template("messagefailure.html")

# Endpoint that can be posted to so users can send a call
@app.route("/call_control", methods=["POST"])
def inbound():
    body = json.loads(request.data)
    event = body.get("data").get("event_type")

    try:
        if event == "call.initiated":
            call = telnyx.Call(connection_id=os.getenv("TELNYX_CONNECTION_ID"))
            call.call_control_id = body.get("data").get("payload").get("call_control_id")
            call.answer()

        elif event == "call.answered":
            call = telnyx.Call(connection_id=os.getenv("TELNYX_CONNECTION_ID"))
            call.call_control_id = body.get("data").get("payload").get("call_control_id")
            call.speak(
                payload="Hello, Telnyx user! Welcome to this call control demonstration",
                language="en-US",
                voice="female"
            )
        elif event == "call.speak.ended":
            call = telnyx.Call(connection_id=os.getenv("TELNYX_CONNECTION_ID"))
            call.call_control_id = body.get("data").get("payload").get("call_control_id")
            call.hangup()
    except:
        return json.dumps({"success":False}), 500, {"ContentType":"application/json"}
    return json.dumps({"success":True}), 200, {"ContentType":"application/json"}


# Main program execution
def main():
    app.run(port=os.getenv("TELNYX_APP_PORT"), debug=True)

if __name__ == "__main__":
    main()