import os
import json
import base64
from dotenv import load_dotenv
import telnyx

load_dotenv()
telnyx.api_key = os.getenv('TELNYX_API_KEY')
TELNYX_CONNECTION_ID = os.getenv('TELNYX_APP_CONNECTION_ID')
TELNYX_PHONE_NUMBER = os.getenv('TELNYX_PHONE_NUMBER')
YOUR_PHONE_NUMBER = os.getenv('YOUR_PHONE_NUMBER')

from flask import Flask, request, Response

def encode_client_state(client_obj):
    return base64.urlsafe_b64encode(json.dumps(client_obj).encode()).decode()

def decode_client_state(client_data):
    return json.loads(base64.urlsafe_b64decode(client_data.encode()).decode())


# ACTION STATES
INTRO = 'intro'
ATTEMPTING_CHALLENGE = 'attempting challenge'
RECORDING_VICTORY_SPEECH = 'recording victory speech'
HANGING_UP = 'hanging up'

app = Flask(__name__)

@app.route('/dial', methods=['GET'])
def dial_player():
    client_state = {'action':INTRO,'remaining_attempts':3,'answer':'00'}
    encoded_client_state = encode_client_state(client_state)
  
    telnyx.Call.create(connection_id=TELNYX_CONNECTION_ID, to=YOUR_PHONE_NUMBER, from_=TELNYX_PHONE_NUMBER, client_state=encoded_client_state)
    return Response(status=200)


@app.route('/webhooks', methods=['POST'])
def respond():
    body = json.loads(request.data)
    print(body)
    event_type = body.get('data').get('event_type')
    payload = body.get('data').get('payload')
    client_state = decode_client_state(payload.get('client_state'))
    print(client_state)

    call = telnyx.Call(connection_id=TELNYX_CONNECTION_ID)
    call.call_control_id = payload.get('call_control_id')

    if client_state['action'] == INTRO:
        if event_type == "call.answered":
            client_state['action'] = ATTEMPTING_CHALLENGE
            encoded_client_state = encode_client_state(client_state)
            call.speak(
                payload='Hello, Telnyx user! Welcome to this call control demonstration.',
                language='en-US',
                voice='female',
                client_state=encoded_client_state
            )
    elif client_state['action'] == ATTEMPTING_CHALLENGE:
        if event_type == 'call.speak.ended':
            call.gather_using_speak(
                payload='Attempt to guess the two digit code now',
                language='en-US',
                voice='female',
                minimum_digits=2,
                maximum_digits=2,
                client_state=payload.get('client_state')
            )
        elif event_type == 'call.gather.ended':
            digits = payload.get('digits')
            remaining_attempts = client_state['remaining_attempts'] = client_state['remaining_attempts'] - 1
            entry = f'You have entered {" ".join(list(digits))}'
            
            if digits == client_state['answer']:
                response = f'{entry} and that is the correct two digit code. Congratulations, you have won the game. Please record your victory message after the beep and press any key once finished.'
                client_state['action'] = RECORDING_VICTORY_SPEECH
            elif client_state['remaining_attempts'] <= 0:
                response = f'{entry} and that is not the correct two digit code. You have no more remaining attempts. Thanks for playing and goodbye.'
                client_state['action'] = HANGING_UP
            else:
                response = f'{entry} and that is not the correct two digit code, you have {remaining_attempts} attempts remaining.'
                client_state['action'] = ATTEMPTING_CHALLENGE

            encoded_client_state = encode_client_state(client_state)
            call.speak(
                payload=response,
                language='en-US',
                voice='female',
                client_state=encoded_client_state
            )
    elif client_state['action'] == RECORDING_VICTORY_SPEECH:
        if event_type == 'call.speak.ended':
            encoded_client_state = encode_client_state(client_state)
            call.record_start(format='mp3', channels='single', client_state=encoded_client_state, play_beep=True)
        elif event_type == 'call.dtmf.received':
            client_state['action'] = HANGING_UP
            encoded_client_state = encode_client_state(client_state)
            call.record_stop(client_state=encoded_client_state)
    elif client_state['action'] == HANGING_UP:
        if event_type == 'call.recording.saved' or event_type == 'call.speak.ended':
            call.hangup()

    return Response(status=200)

if __name__ == '__main__':
    app.run(port=5000)
