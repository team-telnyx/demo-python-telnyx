<div align="center">

# Telnyx-Python Simple Call Control Application

![Telnyx](../logo-dark.png)

Sample application demonstrating Telnyx-Node Call Control functionality.

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

Inbound:
* Receives inbound callback
* Answers the call
* Speaks a sentence and waits for speak.ended callback
* Ends the call

Outbound:
* Makes the call to the specified number
* On answer, speaks audio
* Waits for speak.ended callback
* Ends the call

## Usage

The following environmental variables need to be set

| Variable               | Description                                                                                                                                 |
|:-----------------------|:--------------------------------------------------------------------------------------------------------------------------------------------|
| `TELNYX_API_KEY`       | Your [Telnyx API Key](https://portal.telnyx.com/#/app/api-keys?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) |
| `TELNYX_NUMBER`        | Your [Telnyx Phone Number](https://portal.telnyx.com/#/app/numbers/my-numbers)                                                              |
| `TELNYX_CONNECTION_ID` | Your [Telnyx Call Control Application ID](https://portal.telnyx.com/#/app/call-control/applications)                                        |
| `TELNYX_APP_PORT`      | **Defaults to `8000`** The port the app will be served.                                                                                     |

### .env file

This app uses the excellent [python-dotenv](https://github.com/theskumar/python-dotenv) package to manage environment variables.

Make a copy of [`.env.sample`](./.env.sample) and save as `.env` and update the variables to match your creds.

```
TELNYX_API_KEY=""
TELNYX_NUMBER=""
TELNYX_CALL_CONTROL_ID=""
TELNYX_APP_PORT=8000
```

### Install

Run the following commands to get started

```
$ git clone https://github.com/d-telnyx/demo-python-telnyx.git
```

### Run

Start the server `python main.py`

When the application is started, flask serves it to the port specified in the .env file (Default 8000), so you can sipmly take a look at the application at localhost:8000.

**Note: You must enter phone number in E.164 format (i.e. +12345678910) for the call to be sent correctly.**

Once everything is setup, you should now be able to:
* Make calls to a specified outbound number
* Receive an inbound call
