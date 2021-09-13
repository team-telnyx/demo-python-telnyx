import os
import base64
import threading
import sys

from flask import Flask, request, Response
from dotenv import load_dotenv, find_dotenv

from colorama import Fore, Style

import telnyx
import symbl

load_dotenv(find_dotenv())

# Fill these in with your required params in the .env file
transfer_number = os.getenv('TRANSFER_NUMBER')    # number of live operator to transfer to
conference_number = os.getenv('CONFERENCE_NUMBER')   # number that's tied to your call control application
conference_name = os.getenv('CONFERENCE_NAME')
symbl_number = os.getenv('SYMBL_NUMBER')   # should be left unchanged, constant number of Symbl for incomming PSTN calls

calls = []
conference = None
customer_call_control_id = ""
customer_call = telnyx.Call()
connection_object = ""
conversation_id = ""

transfer_happened = False

class CallInfo():
    """Store all of our call information"""
    pass

app = Flask(__name__)

@app.route('/webhook', methods=['POST']) # Destination of our API calls, append this to your NGROK URL in the Telnyx Portal under Call Control!
# Our code for handling the call control application goes here!
def respond():
    """This is our main logic board for the call control command"""
    # Activate global arrays
    global calls
    global conference
    global customer_call_control_id
    global customer_call
    first_call = True # Keep track if first call or not
    # Get the data from the request
    data = request.json.get('data')
    #print(data, flush=True) #For testing purposes, you could print out the data object received

    if data.get('record_type') == 'event':
        # Check event type
        event = data.get('event_type')
        # print(event, flush=True) # For testing purposes you can print out the event if you'd like

        # When call is initiated, create the new call object and add it to the calls array
        if event == "call.initiated":
            # Extract call information and store it in a new CallInfo() object
            new_call = CallInfo()
            new_call.call_control_id = data.get('payload').get('call_control_id')
            new_call.call_leg_id = data.get('payload').get('call_leg_id')
            new_call.direction = data.get('payload').get('direction')
            new_call.phone_number = data.get('payload').get('from')
            calls.append(new_call)
            # Seperate and keep track of symb versus other callers
            if new_call.direction == 'incoming' and new_call.phone_number != symbl_number and first_call == True:
                # We will initiate the call from symbl.ai and have it create the conference when a fresh caller comes in
                symbl()
                # We will keep track of our initial 'customer' by setting the client state for the call.
                # Note it needs to be in base64 format, hence the conversion here
                customer_call_control_id = data.get('payload').get('call_leg_id')
                client_state_message = "customer"
                encoded_client_state = base64.b64encode(client_state_message.encode('ascii'))
                client_state_str = str(encoded_client_state, 'utf-8')
                # Answer the call
                print(telnyx.Call.answer(new_call, client_state=client_state_str), flush=True)
                customer_call.call_control_id = customer_call_control_id
                customer_call.client_state_message = client_state_str
                first_call = False # Trigger 
            else:
                print(telnyx.Call.answer(new_call), flush=True)        
        # When the call is answered, find the stored call and either add it
        # to the conference or create a new one if one is not yet created
        # Symbl calling in first will create this conference
        elif event == "call.answered":
            call_id = data.get('payload').get('call_control_id')
            call_created = CallInfo()
            call_created.call_control_id = call_id
            for call in calls:
                if call.call_control_id == call_id:
                    if not conference:
                        conference = telnyx.Conference.create(
                            call_control_id=call_id,
                            name=conference_name)
                    else:
                        conference.join(
                            call_control_id=call_id,
                            end_conference_on_exit=True)

        elif event == "conference.participant.joined":
            client_state = data.get('payload').get('client_state')
            if client_state == "Y3VzdG9tZXI=":
                ivr()
                
        # Webhook recieved when button presses are stopped being inputted after a certain delay
        elif event == 'call.dtmf.received':
            digits_pressed = data.get('payload').get('digits')
            if digits_pressed == "1":
                transfer ()
                print ("Transfering call via button press!")
            elif digits_pressed == "2":
                print ("Digit 2 was pressed, you can do whatever else you want this to do inside here!")

        elif event == "call.hangup":
            call_id = data.get('payload').get('call_leg_id')
            for call in calls:
                calls.remove(call)

        elif event == "conference.ended":
            shutdown_server()

    #print(request.json, flush=True); For testing purposes, you can print out the entire json received
    return Response(status=200)

# our transfer command
def transfer():
    """Transfer command to transfer to our designated transfer target"""
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

def ivr():
    """IVR Speech/Commands + Initiate sentinment analysis!"""
    # we initiate a thread to start the IVR along with starting the sentiment analysis by symbl.ai 
    threading.Thread(target=customer_call.speak(
        payload='This is a very long string of nonsense. Press 1 to transfer. Press 2 to print something to console',
        language= 'en-US',
        voice = 'female',
    ))
    threading.Thread(target=sentiment())

def symbl():
    """Initiates Symbl PSTN call into our conference"""
    import symbl

    global connection_object
    global conversation_id

    # symbl related variables, can optionally add paramaters/email transcript/etc
    phoneNumber = conference_number
    meetingId = ""
    password = ""
    emailId = ""

    # call symble streaming API (telephony)
    connection_object = symbl.Telephony.start_pstn(
              credentials={'app_id': os.getenv('APP_ID'), 'app_secret': os.getenv('APP_SECRET') },
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

    #conversation_id = connection_object.conversation.get_conversation_id()
    print(f'{Fore.YELLOW}Symbl has initiated the call and is joining conference!{Style.RESET_ALL}')
    print(connection_object)
    print(conversation_id)
    print(connection_object.connectionId)

def sentiment():
    """Grabs our realtime sentiment analysis"""
    global transfer_happened
    conversation = connection_object.conversation.get_messages(parameters={'sentiment': True})
    #print(conversation)
    for message in conversation.messages:
        trigger_phrase = message.text
        polarity = message.sentiment.polarity.score
        print (message.text + " Polarity score: " + str(polarity))
        delete_last_line()
        if (polarity <= -0.7):
            print (f'{Fore.RED}Message that triggered negative sentiment: {Style.RESET_ALL}' + trigger_phrase + " Polarity score: " + str(polarity))
            transfer_happened = True
            print (f'{Fore.BLUE}Negative sentiment reached desired value, inititating transfer!{Style.RESET_ALL}')
            transfer()
    if transfer_happened == False:
        threading.Timer(2.0, sentiment).start()

def delete_last_line():
    """Use this function to delete the last line in the STDOUT"""
    #cursor up one line
    sys.stdout.write('\x1b[1A')
    #delete last line
    sys.stdout.write('\x1b[2K')

def shutdown_server():
    """Shuts down flask server after call termination/completion"""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

if __name__ == '__main__':
    telnyx.api_key = os.getenv('TELNYX_API_KEY')
    app.run(port = 5000)
