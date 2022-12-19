<div align="center">

# Telnyx-Python Voicemail Transciption & Recording Call Control Application via Elevate AI

![Telnyx](logo-dark.png)

Sample application demonstrating Telnyx-Python transcription and recording functionality using Elevate AI 

</div>

## Pre-Reqs

You will need to set up:

* [Telnyx Account](https://telnyx.com/sign-up?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
* [Telnyx Phone Number](https://portal.telnyx.com/#/app/numbers/my-numbers) enabled with:
    * [Telnyx Call Control Application](https://portal.telnyx.com/#/app/call-control/applications)
    * [Telnyx Outbound Voice Profile](https://portal.telnyx.com/#/app/outbound-profiles)
* [Python and PIP](https://developers.telnyx.com/docs/v2/development/dev-env-setup?lang=python) installed


## What you can do

This app, when running has the following behavior for inbound and outbound calls:

Webpage:
* Enables webpage to recieve websocket messages

Inbound:
* Receives inbound callback
* Answers the call
* Starts recording
* Saves the recording when the call.hangup event is triggered
* Waits for transcription to be processed by the Elevate API
* Prints transcription

## Usage

The following environmental variables need to be set

| Variable               | Description                                                                                                                                 |
|:-----------------------|:--------------------------------------------------------------------------------------------------------------------------------------------|
| `TELNYX_API_KEY`       | Your [Telnyx API Key](https://portal.telnyx.com/#/app/api-keys?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
| `ELEVATEAI_API` | Your [ElevateAI API Key](https://app.elevateai.com/ManageTokens)                                        |
| `PORT`      | **Defaults to `8050`** The port the app will be served.                                                                                     |

### .env file

This app uses the excellent [python-dotenv](https://github.com/theskumar/python-dotenv) package to manage environment variables.

Make a copy of [`sample.env`](sample.env) and save as `.env` and update the variables to match your creds.

```
TELNYX_API_KEY="KEY..."
TELNYX_APP_PORT=8050
ELEVATEAI_API="SOMEKEY"
```

### Install

Run the following commands to get started

```
$ git clone https://github.com/d-telnyx/demo-python-telnyx.git
```

### Run

Start the server `python3 main.py`

When the application is started, flask serves it to the port specified in the .env file (Default 8050), so you can simply take a look at the application at localhost:8050. The webpage where the transcription/call statuses and transcription results prints is http://localhost:PORT/elevateai.html make sure you copy over the entire templates folder.
