import telnyx
import os
from flask import Flask, request, Response
from dotenv import load_dotenv

app = Flask(__name__)

calls = []
conference = None

class call_info():
    pass

@app.route('/webhook', methods=['POST'])
def respond():

    # Activate global calls array
    global calls
    global conference
    global connection_object

    # Get the data from the request
    data = request.json.get('data')

    #print(data, flush=True) #For testing purposes, you could print out the data object received

    # Check record_type
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
            # Answer the call
            print(telnyx.Call.answer(new_call), flush=True)
            print(data.get('payload'))

        # When the call is answered, find the stored call and either add it 
        # to the conference or create a new one if one is not yet created
        elif event == "call.answered":
            call_id = data.get('payload').get('call_control_id')
            call_created = call_info()
            call_created.call_control_id = call_id

            for call in calls:
                if call.call_control_id == call_id:
                    if not conference:
                        conference = telnyx.Conference.create(beep_enabled="always",call_control_id=call_id, name="demo-conference")
                    else:
                        conference.join(call_control_id=call_id)
        
        elif event == "call.hangup":
            call_id = data.get('payload').get('call_leg_id')
            for call in calls:
                if call.call_leg_id == call_id:
                    calls.remove(call)

    #print(request.json, flush=True); For testing purposes, you can print out the entire json received
    
    return Response(status=200)

if __name__ == '__main__':
    load_dotenv()
    telnyx.api_key = os.getenv('TELNYX_API_KEY')
    app.run(port=52)