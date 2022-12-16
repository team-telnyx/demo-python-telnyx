import json
import base64
import ssl
import telnyx
import time
import os
import http.client
import threading
from flask_socketio import SocketIO, emit 
from flask import Flask, request, Response, render_template 
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, Response
load_dotenv(find_dotenv())
telnyx.api_key = os.getenv('TELNYX_API_KEY')
my_port = os.getenv('TELNYX_APP_PORT')
elevateai_API = os.getenv('ELEVATEAI_API')

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/call-flow', methods=['POST'])

def responds():
    #Check record_type of object
    data = request.json['data']
    print(json.dumps(data, indent=4))
    call_control_id = data.get('payload').get('call_control_id')
    call = telnyx.Call()
    call.call_control_id = call_control_id
    direction = data.get('payload').get('direction')
    conn = http.client.HTTPSConnection("api.elevateai.com")
    headers = {
        'Content-Type': 'application/json',
        'X-API-Token': elevateai_API
    }
   #inbound call
    if data.get('event_type') == 'call.initiated' and direction == 'incoming':
        socketio.emit('message-from-server-to-client2', data.get('event_type'))
        print("Incoming call")
        client_state_incoming = str(base64.b64encode(direction.encode('ascii')), "utf-8")
        res = call.answer(client_state=client_state_incoming)
        print(res)
    if data.get('event_type') == 'call.answered':
       socketio.emit('message-from-server-to-client2', data.get('event_type'))
       print("Answered")
       call.record_start(format="mp3", channels="single")
    if data.get('event_type') == 'call.recording.saved':
       socketio.emit('message-from-server-to-client2', data.get('event_type'))
       recordinguri = data.get('payload').get('recording_urls').get('mp3')
       t = threading.Thread(target=worker, args=(recordinguri, headers, conn))
       t.start()

    return Response(status=200)

def worker(recordinguri, headers, conn):
    #here we're setting the ElevateAI transcription parameters 
       payload = json.dumps({
         "type": "audio",
         "languageTag": "en-us",
         "vertical": "default",
         "audioTranscriptionMode": "highAccuracy",
         "includeAiResults": True,
         "downloadUri":f"{recordinguri}"
         })
       #make the REST API call to ElevateAI to get the Interaction ID
       conn.request("POST", "/v1/interactions", payload, headers)
       res = conn.getresponse()
       dump = res.read().decode('utf-8')
       print(f"Interaction ID is: {dump}")
       interactionID = json.loads(dump)
       transcript_id = interactionID['interactionIdentifier']
       #loop every second until we know the transcription is processed
       status_final = None
       if status_final != "processed":
            while status_final != "processed":
               conn.request("GET", f"/v1/interactions/{transcript_id}/status", payload, headers)
               res2 = conn.getresponse()
               status_string = res2.read().decode('utf-8')
               status = json.loads(status_string)
               status_final = status['status']
               print(status_final)
               socketio.emit('message-from-server-to-client2', status_final)
               time.sleep(1)
       #once the transcription is processed, get the text value and emit it to the webpage        
       if status_final == "processed":
           conn.request("GET", f"/v1/interactions/{transcript_id}/transcripts/punctuated", payload, headers)
           res3 = conn.getresponse()
           transcript_json = res3.read().decode('utf-8')
           transcript_obj = json.loads(transcript_json)
           allphrases_array = transcript_obj['sentenceSegments']
           transcript = ""
           for phraseObj in allphrases_array:
            transcript += phraseObj["phrase"] + " "
           socketio.emit('message-from-server-to-client', transcript)
           print(transcript)
@app.route('/')                                                                 
def index():
    return render_template('elevateai.html')

if __name__ == '__main__':
    socketio.run(app, host="localhost", port=8050)
    