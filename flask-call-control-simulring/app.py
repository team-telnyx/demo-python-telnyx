
import telnyx
import json
import base64
import os
import mysql.connector
from flask import Flask, request, Response
from dotenv import load_dotenv

telnyx.api_key = os.getenv("TELNYX_API_KEY")
app = Flask(__name__)
@app.route('/', methods=['POST'])
def respond():
    # Check record_type of object
    # mydb = mysql.connector.connect(host='localhost', database='Voice_Response', user='root', password='Walcott34', autocommit = True)
    # mycursor = mydb.cursor()
    data = request.json['data']
    call_control_id = data.get('payload').get('call_control_id')
    call = telnyx.Call()
    call.call_control_id = call_control_id
    direction = data.get('payload').get('direction')
    client_state = data.get('payload').get('client_state')
    client_state_incoming = ""
    client_state_outgoing = ""
    # inbound call
    if data.get('event_type') == 'call.initiated' and direction == 'incoming':
       print("Incoming call")
       client_state_incoming = str(base64.b64encode(direction.encode('ascii')), "utf-8")
       res = call.answer(client_state=client_state_incoming)
       print(res)
    if data.get('event_type') == 'call.answered' and base64.b64decode(client_state).decode('ascii') == 'incoming':
        client_state_outgoing = str(base64.b64encode(call_control_id.encode('ascii')), "utf-8")
        # call1 = telnyx.Call.create(connection_id="1446442091122001881", to="+12393492102", from_="+12892787139", client_state=client_state_outgoing)
        callstat = "call.initiated"
        # sql_agent_create1 = f"INSERT INTO StoreCall (client_state, call_control_id, status) VALUES ('{client_state_outgoing}', '{call1.call_control_id}', '{callstat}')"
        # mycursor.execute(sql_agent_create1)
        # call2 = telnyx.Call.create(connection_id="1446442091122001881", to="+14168305230", from_="+12892787139", client_state=client_state_outgoing)
        callstat2 = "call.initiated"
        # sql_agent_create2 = f"INSERT INTO StoreCall (client_state, call_control_id, status) VALUES ('{client_state_outgoing}', '{call2.call_control_id}', '{callstat2}')"
        # mycursor.execute(sql_agent_create2)
    if data.get('event_type') == 'call.answered' and base64.b64decode(client_state).decode('ascii') != 'incoming':
        callstat3 = data.get('payload').get('state')
        # sql_update_agent = f"UPDATE StoreCall SET status = '{callstat3}'"
        # mycursor.execute(sql_update_agent)
        call.gather_using_speak(payload="Press 1 to be connected to the client, press two to hang up", language='en-US', voice='male')
    if data.get('event_type') == 'call.gather.ended':
        digits = data.get('payload').get('digits')
        if digits == "1":
           print(call.speak(payload="Standby. Bridging your call", language='en-US', voice='male'))
          #  sql_select_agent = f"SELECT call_control_id FROM StoreCall WHERE client_state = '{client_state}' AND call_control_id != '{call_control_id}'"
          #  mycursor.execute(sql_select_agent)
          #  myresult = mycursor.fetchone()
          #  call1 = telnyx.Call()
          #  call1.call_control_id = myresult[0]
          #  call1.hangup()
    if data.get('event_type') == 'call.speak.ended':
       original_inbound_call_control_id = base64.b64decode(client_state).decode('ascii')
       original_inbound_call = telnyx.Call()
       original_inbound_call.call_control_id = original_inbound_call_control_id
       print(original_inbound_call.bridge(call_control_id=call_control_id))
    print(data)
    return Response(status=200)
if __name__ == '__main__':
    app.run(port=8080, debug=True)