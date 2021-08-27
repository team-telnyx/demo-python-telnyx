import os

import base64
import time
from flask import Flask, request, Response
from dotenv import load_dotenv

import telnyx
import symbl

app = Flask(__name__)

# Fill these in with your required params
transfer_number = ""    # number of live operator to transfer to
conference_number = ""   # number that's tied to your call control application
conference_name = "Conference Test 121"
symbl_number = "+12015947998"   # should be left unchanged, constant number of Symbl for incomming PSTN calls

calls = []
conference = None
customer = ""
class call_info():
    pass

@app.route('/webhook', methods=['POST'])
def respond():

    # Activate global arrays
    global calls
    global conference
    global customer 
    
    # Get the data from the request
    data = request.json.get('data')
    #print(data, flush=True) #For testing purposes, you could print out the data object received

    # Check record_type

    customer_call_control_id = ""
    if data.get('record_type') == 'event':
        # Check event type
        event = data.get('event_type')
        # print(event, flush=True) #For testing purposes you can print out the event if you'd like

        # When call is initiated, create the new call object and add it to the calls array
        if event == "call.initiated":
            # Extract call information and store it in a new call_info() object
            new_call = call_info()
            new_call.call_control_id = data.get('payload').get('call_control_id')
            new_call.call_leg_id = data.get('payload').get('call_leg_id')
            calls.append(new_call)
            direction = data.get('payload').get('direction')
            phone_number = data.get('payload').get('from')
            if (direction == 'incoming' and phone_number != symbl_number):
                customer = data.get('payload').get('call_leg_id')
                customer_call_control_id = data.get('payload').get('call_leg_id')
                encoded_client_state = base64.b64encode(direction.encode('ascii'))
                client_state_str = str(encoded_client_state, 'utf-8')
                # Answer the call
                print(telnyx.Call.answer(new_call, client_state=client_state_str), flush=True)
            else:
                print(telnyx.Call.answer(new_call), flush=True)
        # When the call is answered, find the stored call and either add it 
        # to the conference or create a new one if one is not yet created
        elif event == "call.answered":
            call_id = data.get('payload').get('call_control_id')
            from_number = data.get('payload').get('from')
            call_created = call_info()
            call_created.call_control_id = call_id
            for call in calls:
                if call.call_control_id == call_id:
                    if not conference:
                        conference = telnyx.Conference.create(
                            call_control_id=call_id, 
                            name=conference_name)
                    else:
                        conference.join(call_control_id=call_id, end_conference_on_exit=True)
        # once conference is created, we have symbl ai call inwards
        elif event == "conference.created":
            symbl()

        elif event == "conference.participant.joined":
            client_state = data.get('payload').get('client_state')
            # if client state = "incoming", base 64 encoded.
            if(client_state=="aW5jb21pbmc="):
                res = conference.speak(
                    payload='This is a very long string of nonsense, customers hate hearing this robot over and over.',
                    language= 'en-US',
                    voice = 'female',
                    call_control_ids = customer_call_control_id
                )
                
        elif event == "call.hangup":
            call_id = data.get('payload').get('call_leg_id')
            for call in calls:
                if call.call_leg_id == call_id:
                    calls.remove(call)
                    print(customer)

    #print(request.json, flush=True); For testing purposes, you can print out the entire json received
    return Response(status=200)

# our transfer command
def transfer():
    connection_id = os.getenv('CONNECTION_ID')
    client_state = "outbound agent transfer"
    encoded_client_state = base64.b64encode(client_state.encode('ascii'))
    client_state_str = str(encoded_client_state, 'utf-8')
    telnyx.Call.create(
        connection_id=connection_id,
        to = transfer_number,
        from_ = conference_number,
        client_state = client_state_str
    )

def symbl():
    import symbl
    # symbl related variables, can optionally add paramaters/email transcript/etc
    phoneNumber = conference_number 
    meetingId = "" 
    password = "" 
    emailId = ""

    # call symble streaming API (telephony)
    connection_object = symbl.Telephony.start_pstn(
        phone_number=phoneNumber,
        dtmf = ",,{}#,,{}#".format(meetingId, password),
        actions = [
            {
            "invokeOn": "stop",
            "name": "sendSummaryEmail",
            "parameters": {
                "emails": [
                emailId
                ],
            },
            },
        ]
    )
    conversation_id = connection_object.conversation.get_conversation_id()
    print(connection_object)
    print(conversation_id)
    
    # function to get sentiment responses every so often, then trigger transfer if sentiment is negative
    def sentiment():
        sentiment = connection_object.conversation.get_messages(parameters={'sentiment': True})     
        for message in sentiment.messages:
            if (message.sentiment.suggested == "negative" and has_transfer_happened == False):
                trigger_phrase = message.text   # Phrase that triggered a negative response
                print("Message that triggered transfer:" + trigger_phrase)
                has_transfer_happened == True;
                return ("Negative")
    i = 0
    has_transfer_happened = False   # To make sure we send only 1 transfer command

    while i < 30:
        sentiment()
        if sentiment() == "Negative":
            transfer()
            print("Initiated Transfer")
            break
        else: 
            time.sleep(1)
            i = i + 1

if __name__ == '__main__':
    load_dotenv()
    telnyx.api_key = os.getenv('TELNYX_API_KEY')
    app.run(port = os.getenv('PORT_NUMBER'))