<div align="center">

# Symbl <-> Telnyx AI IVR Solution

![Telnyx](../logo-dark.png)

Sample application demonstrating a sample example of an IVR Solution using Telnyx Call Control and AI processing provided by Symbl.ai


</div>

## Documentation

The full documentation will be available on [developers.telnyx.com]


## Pre-Reqs
What you will need to set up on the Telnyx Side:

* [Telnyx Account](https://telnyx.com/sign-up?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
* [Telnyx Call Control Application](https://portal.telnyx.com/#/app/call-control/applications)
* [Python and PIP](https://developers.telnyx.com/docs/v2/development/dev-env-setup?lang=python) installed
* Ability to receive webhooks (with something like [ngrok](https://developers.telnyx.com/docs/v2/development/ngrok?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link))


What you will need to set up on the Symbl Side:
* [Symbl Account](https://telnyx.com/sign-up?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)


## What you can do

* Set up a phone number to call into to set up a mock "IVR' center utilizing Telnyx Conference Call Control
* Based on sentiment analysis provided by Symbl, choose to transfer the call from the IVR to a live operator

## Usage

### .env file

This app uses the excellent [python-dotenv](https://github.com/theskumar/python-dotenv) package to manage environment variables.

Make a copy of [`.env.sample`](./.env.sample) and save as `.env` and update the variables to match your creds.

```
# remove .sample from file name
TELNYX_API_KEY=""
TELNYX_PUBLIC_KEY=""
CONNECTION_ID=""
PORT_NUMBER=8000
```

### symbl.conf
From symbl.ai sign up page, insert your app_id and app_secret. Once you sign up for an account mentioned in the Pre-Reqs above, the front page will give you the required details.

```
# remove .sample from file name
[credentials]
app_id= #Your Symbl.ai appId 
app_secret= #Your Symbl.ai appSecret 
```

### Callback URLs For Telnyx Applications

| Callback Type                    | URL                              |
|:---------------------------------|:---------------------------------|
| Inbound Call-Control Callback  | `{ngrok-url}/webhook`  |

This URL is needed to be 

## Installation

### Environment Setup


#### Dependencies

This package relies on some very nice external dependencies and modules. The specific ones can be found in the Pipfile. 
To make this easier we are using `pipenv` to manage all of our packaging needs. To utilize this amazing tool, make sure you have `pip` installed, then run `pip install pipenv` 

Afterwards, simply run `pipenv install` to automatically install all the required packages that are needed.

#### Ngrok

This application is served on the port defined in the runtime environment (or in the `.env` file). Be sure to launch [ngrok](https://developers.telnyx.com/docs/v2/development/ngrok?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) for that port
```
./ngrok http 8000
```

> Terminal should look _something_ like

```
ngrok by @inconshreveable                                                                                                                               (Ctrl+C to quit)

Session Status                online
Account                       Little Bobby Tables (Plan: Free)
Version                       2.3.35
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    http://your-url.ngrok.io -> http://localhost:8000
Forwarding                    https://your-url.ngrok.io -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

At this point you can point your Call Control application (located [here](https://portal.telnyx.com/#/app/call-control/applications)) to the generated ngrok URL + path  (Example: `http://{your-url}.ngrok.io/call-control/inbound`).

### Telnyx Portal Setup

In the [Portal](https://portal.telnyx.com/)
* Create call control application and callback to ngrok
* Attach call control application to phone number


### Symbl Portal Setup
In the [Portal](https://platform.symbl.ai/)
* Jot down your App ID Credentials and App Secret

### Run
Before you're able to run the application, you will need to set up some variables. Reference Installation from above.

You will also need to fill out these variables in the conference.py file:
* transfer_number = ``` This is  the number you want the initial caller ("customer") to be transfered to after his sentiment value gets too low```
* conference_number = ```This is the number that you have assigned to your Call Control ID for the initial caller ("customer")```
* conference_name = ```Any name that you wish to call your Conference to establish where everything should join towards ```

#### Start the server

Start the server `conference.py`

When the application is started, flask serves it to the port specified in the .env file (Default 8000)

When you place a call towards the number you specified in conference.py (the number that you set your IVR application to point to), the program will do the rest to route the call. 

Once you reach the IVR, exemplified by the text-to-speech talking on the line, you can start saying phrases for Symbl.ai to parse through. Once the AI finds a phrase that the caller/customer has spoken that it determines to be "negative" (Link here for more information), the call with send a forward and initiate a call request to an "operator".

If an operator joins the call, it will automatically join his conference to provide service to him. Hanging up will terminate the session.