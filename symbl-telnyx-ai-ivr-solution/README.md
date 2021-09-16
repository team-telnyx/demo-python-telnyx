<div align="center">

# Telnyx & Symbl.ai : CI Enabled Transfers On Calls

![Telnyx](../logo-dark.png)

This sample application not only implements automation features on a telephony based call using Telnyx Call Control, but it also recognizes and acts on conversation sentiment to transfer and route calls directly to specific numbers by parsing data collected from Symbl.ai.


</div>

# Objective
## To create a functional Telnyx Voice API Intelligent Transfers to a Live Operator with Symbl.ai in a IVR/AVR Python Flask App   

## Documentation

The full documentation and step by step process can be found in the Workshop folder linked [here](./workshop/README.md)

For a quick setup guide, follow below...

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
TELNYX_API_KEY="" # Telnyx API KEY (V2) found in the API Keys section in the portal
TELNYX_PUBLIC_KEY="" # Telnyx Public Key found in API Keys in the Portal
CONNECTION_ID="" # Call Control Application ID
TRANSFER_NUMBER="" # Number you want your application transfered to
CONFERENCE_NUMBER="" # Telnyx purchased number 
CONFERENCE_NAME="" # Your desired conference name

SYMBL_NUMBER="+12015947998"" # Symbl's Number that will be calling us (sh
APP_ID="" # Symbl AI's APP ID found in Portal
APP_SECRET="" # Symbl AI's App Secret found in Portal
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

At this point you can point your Call Control application (located [here](https://portal.telnyx.com/#/app/call-control/applications)) to the generated ngrok URL + path  (Example: `http://{your-url}.ngrok.io/Webhook`).

## Next Steps?

Perhaps with this knowlede you'd be able to build out a more complex IVR solution.

Check out these resources for more documentation and examples of other code bases as well as fully completed demo-apps to spark your interest!

Use what you learned here with our other projects to bring out the best of your creativity!

* https://developers.telnyx.com/docs/v2/call-control/tutorials
* https://developers.telnyx.com/docs/v2/verify/quickstart
* https://github.com/team-telnyx/demo-python-telnyx
* https://github.com/team-telnyx/demo-node-telnyx
* https://github.com/team-telnyx/demo-php-telnyx
* https://github.com/team-telnyx/demo-ruby-telnyx
* https://github.com/team-telnyx/demo-dotnet-telnyx
* https://github.com/team-telnyx/demo-java-telnyx
