import telnyx
import json
import base64
import os
import requests
import urllib
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, Response
load_dotenv(find_dotenv())
telnyx.api_key = os.getenv('TELNYX_API_KEY')
my_port = os.getenv('PORT')
my_host = os.getenv('HOST')

app = Flask(__name__)

@app.route('/', methods=['POST'])
def respond():
    #Check record_type of object
    data = request.json['data']
    call_control_id = data.get('payload').get('call_control_id')
    call = telnyx.Call()
    call.call_control_id = call_control_id
    direction = data.get('payload').get('direction')
    transcription_url = f'https://api.telnyx.com/v2/calls/{call.call_control_id}/actions/transcription_start'
    headers2 = {'Content-Type':'application/json','Accept': 'application/json;charset=utf-8','Authorization': f'Bearer {telnyx.api_key}',}
    data2 = '{"language":"en"}'
    if data.get('event_type') == 'call.initiated' and direction == 'incoming':
       print("Incoming call")
       client_state_incoming = str(base64.b64encode(direction.encode('ascii')), "utf-8")
       res = call.answer(client_state=client_state_incoming)
       print(res)
    if data.get('event_type') == 'call.answered':
       call.speak(payload="Please leave a voicemail now.", language="en-US", voice="female")
    if data.get('event_type') == 'call.speak.ended':
       response2 = requests.post(transcription_url, headers=headers2, data=data2)
       start_recording = call.record_start(format="mp3", channels="single")
       print(start_recording)
    if data.get('event_type') == 'transcription':
       transcript = data.get('payload').get('transcription_data').get('transcript')
       with open("transcript.txt", "a") as file_object:
    # Append transcript to the same file
           file_object.write(transcript+"\n")
       print(transcript)
    if data.get('event_type') == 'call.recording.saved':
       recording_url = data.get('payload').get('recording_urls').get('mp3')
       recording_name = data.get('payload').get('recording_id')
       urllib.request.urlretrieve(recording_url, recording_name+".mp3")
    print(data)
    return Response(status=200)
if __name__ == '__main__':
    app.run(host=my_host, port=my_port)
