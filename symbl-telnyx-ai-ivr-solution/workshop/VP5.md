| [Overview](./VP1.md)  | [Telnyx Prerequisites](./VP2.md) | [Symbl Prerequisites](./VP3.md) | [Telnyx Call Control Conferencing Application](./VP4.md) | [Symbl <-> Telnyx Sentiment IVR](./VP5.md) | [What's Next?](./VP6.md)
| :---: | :---: | :---: | :---: | :---: | :---: |

# AI IVR Workshop
## Symbl <-> Telnyx Sentiment IVR

## Synopsis
Your customer calls a telephony API programmed by Telnyx to route calls for an Integrated Virtual Assistant (IVR)/ Automated Virtual Assistant (AVA). After the customer’s call is received by Telnyx’s Voice API, Symbl.ai’s Conversation Intelligence API platform triggers automated speech recognition on the customer. Symbl.ai analyzes the customer’s messages to determine whether or not the customer responses display a rise or fall in disposition. If the disposition falls below a preset threshold, the logic of the application automatically transfers the customer away from a IVR/AVA to a live operator, creating a persistent, omnichannel, multi-member, artificially intelligent conversation.  

In this demo application, we will add on to the conference application that we built in the previous step to extend the capabilities of a standard IVR to accomplish something beyond standard speech recognition: complete sentiment analysis on messages.
 

## Setup
Before we get started with adding on more code, we will need to get some API credentials from symbl.ai's page. More information can be located at the [Symble Prerequisites](./VP3.md)

Take note of both App ID and App Secret

As before, we will now want to install Symbl:

```bash
$ pip install symbl
```

A full complete list of Symbl.ai's full SDK capabilities can be located [here](https://docs.symbl.ai/docs/python-sdk/overview).

We will also be utilizing a fabulous package called `python-dotenv`. This simplifies our variable process by not having to expose our secret keys and the like to the outward facing world, and have a one stop place to fill these in.

Create a file called `.env`, and input all of your previously acquired variables from previous steps in here:
```
TELNYX_API_KEY="" # Telnyx API KEY (V2) found in the API Keys section in the portal
TELNYX_PUBLIC_KEY="" # Telnyx Public Key found in API Keys in the Portal
CONNECTION_ID="" # Call Control Application ID
TRANSFER_NUMBER="" # Number you want your application transfered to
CONFERENCE_NUMBER="" # Telnyx purchased number 
CONFERENCE_NAME="" # Your desired conference name
SYMBL_NUMBER="+12015947998"" # Symbl's Number that will be calling us (should be static, do not change)
APP_ID="" # Symbl AI's APP ID found in Portal
APP_SECRET="" # Symbl AI's App Secret found in Portal
```
<br>

## Constructing the Code

From here, we will be adding on to the conference section with some logic involving IVR fundamentals and the Symbl.ai integration. To make the most sense, we will post the entire code block and work from there to visualize why we are constructing things the way we do: 

<details>
  <summary markdown="span";>Main Code Block</summary>

```python
import os
import base64
import threading
import sys

from flask import Flask, request, Response # mini web framework
from dotenv import load_dotenv, find_dotenv # variable import from .env

from colorama import Fore, Style # Nice way to color our console

import telnyx # our VOIP service application
import symbl # our sentiment analysis application

load_dotenv(find_dotenv())

# Fill these in with your required params in the .env file
transfer_number = os.getenv('TRANSFER_NUMBER')    # number of live operator to transfer to
conference_number = os.getenv('CONFERENCE_NUMBER')  # number that's tied to your CC application
conference_name = os.getenv('CONFERENCE_NAME')
symbl_number = os.getenv('SYMBL_NUMBER')   # unchanging number of Symbl for incomming PSTN calls

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
# Destination of our API calls, append this to your NGROK URL in the Telnyx Portal under Call Control!
@app.route('/webhook', methods=['POST']) 
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
        if polarity <= -0.7:
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
```
</details>

<br>

Lets start with the beginning:

```python
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
```

This will be our variables section. We will first have to grab some information from the portal to fill in here, such as the number we want to transfer to, the number that the conference is attached to, the name of the conference that we would like, and symbl's static number.

We then create some variables:

* `Calls` from before, to keep track of our calls since this is a conference
* `conference` to keep track if we have made and established a conference room from our first call
* `customer_call_control_id` to identify the initial caller, so we can send commands that will only pertain to him and not the entire conference
* `customer_call` is an object to initialize with Telnyx so we can manipulate the initial call of our person calling in
* `first_call` to keep track of the initial caller
* `connection_object` symbl's identity of it's PSTN call service
* `conversation_id` symbl's way to keep track of conversation analytics


The next thing we should do is make the logic to transfer and for our ivr:

```python
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
```

The `transfer()` function will make an outbound call from our conference to our number we would want our "live" operator to live at. We will have seperate logic in place to handle the call and have it join our conference which will be located later on, in the `respond()` function. 

>Our transfer will not work as a standard IVR. Rather than transfering the initial caller to the representative, we will be having our representative **JOIN** the conference that the customer is already in for a smoother experience. 

> Also do notice we are adding a *client_state* parameter. This is simply to keep track of who is who in the call, as adding this will perpetuate this header in our json response objects in the webhook as we go alone. For more information on the paramaters the ```telny.Call.Create()``` object can take, visit [here](https://developers.telnyx.com/docs/api/v2/call-control/Call-Commands#callDial).

The `ivr` function starts a text to speach command that listens for DTMF signals for the customer. The logic of the button presses will be established in the `respond()` function later on. We are also threading this with the `sentiment()` function. Once the IVR is started, we want to then start our analysis of our "customer's" sentiment to know when to transfer. 
> This is a good place to start running this, but you can start it earlier or later on if you so desire by simply moving this function to another part of the call flow. For example, you can start sentiment analysis after the IVR completes its statement by listening to the specific webhooks that come. For more information and more paramaters that you can issue in for these commands, you can find the information located here: https://developers.telnyx.com/docs/api/v2/call-control/Call-Commands 


Next we will look to the Symbl related functions

```python
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

```

The `symbl` function simply initiates a PSTN call inbound to our conference number that we have set up. We are printing some information to record just in case at the end, as well as to track if it has joined. We can also find that information in the webhook responses that are being sent to the ngrok url.

The `sentiment` function is there to loop and find conversation objects that we are scanning for sentiment analysis. Inside the `connection_object` we get a variety of information from Symbl. To see what kind of things you can grab, visit their [Straming API Page](https://docs.symbl.ai/docs/python-sdk/streaming-api). Once those are scanned and we detect a "negative" sentiment with a specified polarity score (in this case being -0.7), we take the call and then forwarded to our designated number that we established in the `.env` file.

Now we will take a look into our main function, `respond()`. This is where the entirety of our logic comes into play. Telnyx works by observing webhook responses and sending information back to your address that you listed in your webhook_url in setup creation. Here we will be forming the brains of the operation by having our application do certain things once we get certain webhooks that hit our flask server that we are running.

```python
@app.route('/webhook', methods=['POST'])
# Our code for handling the call control application goes here! 
def respond():

    # Activate global arrays
    global calls
    global conference
    global customer_call_control_id
    global my_IVR_info
    global customer_call
    global first_call
    # Get the data from the request
    data = request.json.get('data')
    #print(data, flush=True) #For testing purposes, you could print out the data object received

    # Check record_type
    # Find out how to return 200 after symbl() initiates call

    if data.get('record_type') == 'event':
        # Check event type
        event = data.get('event_type')
        # print(event, flush=True) #For testing purposes you can print out the event if you'd like

        
                # When call is initiated, create the new call object and add it to the calls array
if __name__ == '__main__':
    load_dotenv()
    telnyx.api_key = os.getenv('TELNYX_API_KEY')
    app.run(port = 5000)
```

First we will be defining our flask operation to route to `'/webhook'` This means that we will be listening to our [POST] requests at our ngrokurl/webhook. ex. `123.456.789/webhook`. This application will then also proceed to run on `port 5000`.
> Reference [Telnyx Conferencing Tutorial](./VP4.md) for more information about this set up.

We then activate our global arrays and variables. We proceed to shorthand our json response data that will come into our server and listen to those invents.


```python
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
```

Here we have our first event. We recieve a `call.initiated` webhook once we get an incoming/outgoing call that starts ringing on the Telnyx server and Telnyx sends that over to our ngrok URL which hits our application. We proceed to record a bunch of data for troubleshooting purposes if need be, then make an `if` statement discerning between Symbl.ai joining the call vs our intended customer.

If it is a new customer, and not `symbl` calling us, we initiate the function `symbl()` that we made before to start an incoming call for symbl.ai to do it's analytics.

We then track this later on by encoding the string `customer` in base64 and adding it to the call via `client_state`. This will then carry through the rest of the call so we can keep track. Otherwise, we just answer the call like normal for other callers.


```Python
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
        
        elif event == "call.hangup":
            call_id = data.get('payload').get('call_leg_id')
            for call in calls:
                calls.remove(call)
```

The `call.answered` and `call.hangup` events are processed exactly like we had it in the [Conferencing](./VP4.md) tutorial. If there's no conference, we create one. Otherwise we join the existing conference. If we recieve a `call.hangup`, we remove the call from our array.

> The way we have setup our call flow in this app is that a recieving an initiation of a call triggers Symbl to call us, and Symbl will trigger the conference create. This way we always have Symbl being able to record the voice data and it doesn't miss a word as it's the first one in the conference.

``` Python
        elif event == "conference.participant.joined":
            client_state = data.get('payload').get('client_state')
            if client_state == "Y3VzdG9tZXI=":
                ivr()
```

Here we state that if we get a `confere.participant.joined` webhook and the client state matches the b64 encode (of customer), we will trigger the ivr() function.

```python
        elif event == "conference.ended":
            shutdown_server()
```
If it ends, we execute our `shutdown_server()` function.


And that's it! It looks a lot scarier than it really is. This is essentially just a bunch of conditional statements to control a live call that is happening based on the different states that the call can be in. As always, more information on the different call states and call commands that you can invoke can be found [here](https://developers.telnyx.com/docs/api/v2/call-control/Call-Commands).

You should now be successfully able to put all of this together to start your flask server, call-in to your application and trigger Symbl to start and create a conference. In here, you will hear your designated IVR message and a printout of the call transcription should be in the console. Afterwards, if Symbl.ai responds with a negative sentiment we initiate a transfer to our designated number! 

Congratulations, you have successfully made an IVR that is powered by AI. Let's see what else you can do!

You are now ready to [proceed to the next step](./VP6.md).