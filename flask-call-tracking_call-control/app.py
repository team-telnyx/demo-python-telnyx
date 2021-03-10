import telnyx
import os
import json
from dotenv import load_dotenv
from flask import Flask, \
    render_template, request, Response, redirect, url_for, flash
from flask_modus import Modus
from urllib.parse import urlunsplit
from Model.database_queries import db_fetch_data, \
    db_number_insert, db_number_update, db_number_row_identifier, \
    db_number_delete, db_call_delete, db_number_forward_fetch, \
    db_call_insert
from telnyx_commands import telnyx_number_acquire, \
    telnyx_number_delete, telnyx_cnam_lookup, difference


load_dotenv()

app = Flask(__name__)
modus = Modus(app)
app.secret_key = "SecretKey"


# homepage
@app.route('/')
def index():
    all_phone_numbers, all_call_data = db_fetch_data()

    return render_template('index.html',
                           all_phone_numbers=all_phone_numbers,
                           all_call_data=all_call_data, )


# search and order first number we get based on City/State
@app.route("/number/", methods=['POST'])
def acquire():

    # pull data to store in db later to display on frontend
    locality = request.form["city"]
    administrative_area = request.form["state"]
    forward_number = request.form["forward_number"]
    tag = request.form["tag"]
    city_state_combo = locality + ", " + administrative_area

    number_to_order, city_state_combo = telnyx_number_acquire(locality, administrative_area)

    db_number_insert(number_to_order, city_state_combo, forward_number, tag)

    flash("Phone Number:" + number_to_order +
          " Was Purchased Successfully!")

    return redirect(url_for('index'))


# using modus module to incorporate PATCH and DELETE requests
@app.route("/number/<id>/", methods=['PATCH', 'DELETE'])
def update(id):
    try:
        if request.method == b'PATCH':
            # grabbing id from index
            id = request.form.get('id')
            # updating new variables in update screen
            updated_forward_number = request.form["forward_number"]
            updated_tag = request.form["tag"]

            phone_number = db_number_update(id, updated_forward_number, updated_tag)
            flash("Phone Number" + phone_number + " Was Updated Successfully")

        elif request.method == b'DELETE':
            number_to_delete = db_number_row_identifier(id)
            # delete from telnyx portal
            telnyx_number_delete(number_to_delete)
            # delete from database and save
            db_number_delete(id)
            flash("Phone Number" + number_to_delete + " Successfully Deleted")

    except Exception as e:
        print("Error updating database")
        print(e)
    return redirect(url_for('index'))


@app.route("/call/<id>/", methods=['DELETE'])
def delete_call(id):

    if request.method == b'DELETE':
        db_call_delete(id)
        flash("Call Record Successfully Deleted!")

    return redirect(url_for('index'))


def handle_call_answered(call, called_number):
    number_to_forward_to = db_number_forward_fetch(called_number)

    webhook_url = urlunsplit((
        request.scheme,
        request.host,
        "/call-control/outbound",
        "", ""))
    transfer_params = {
        "to": number_to_forward_to,
        "webhook_url": webhook_url
    }
    call.transfer(**transfer_params)


@app.route("/call-control/inbound", methods=["POST"])
def inbound_call():
    # store some id values JUST IN CASE for troubleshooting purposes
    body = json.loads(request.data)
    calling_number = body["data"]["payload"]["from"]
    called_number = body["data"]["payload"]["to"]
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

    # construct call object, which is needed for initial call control commands
    call = telnyx.Call()
    call.call_control_id = call_control_id

    # main logic response based on inbound webhook events
    try:
        if event_type == "call.initiated":
            call = telnyx.Call(connection_id=os.getenv("TELNYX_CONNECTION_ID"))
            call.call_control_id = body.get("data").get("payload").get("call_control_id")
            call.answer()
            print(calling_number)
            print(called_number)
        elif event_type == "call.answered":
            handle_call_answered(call, called_number)
        elif event_type == "call.hangup":
            print(body)
            cnam_info = telnyx_cnam_lookup(calling_number)
            # time difference
            end_time = ''.join(body.get("data").get("payload").get("end_time"))
            start_time = ''.join(body.get("data").get("payload").get("start_time"))
            duration, date = difference(start_time, end_time)
            forward_number = db_number_forward_fetch(called_number)
            db_call_insert(cnam_info, calling_number, called_number, forward_number, date, duration)

    except Exception as e:
        print("Error processing webhook")
        print(e)
    return Response(status=200)


@app.route("/call-control/outbound", methods=["POST"])
def outbound_call():
    body = json.loads(request.data)
    call_leg_id = body[
        "data"][
        "payload"][
        "call_leg_id"]
    print(f"Received call_control event with call_leg_id: {call_leg_id}")
    return Response(status=200)


if __name__ == "__main__":
    telnyx.api_key = telnyx.os.getenv("TELNYX_API_KEY")
    TELNYX_APP_PORT = "8000"
    app.run(port=TELNYX_APP_PORT)
