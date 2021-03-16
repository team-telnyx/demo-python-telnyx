<div align="center">

# Telnyx Flask Call Control Tracker

![Telnyx](../logo-dark.png)

Sample application demonstrating Telnyx-Python Call Control and API


</div>

## Documentation

The full documentation is available on [developers.telnyx.com]https://developers.telnyx.com/docs/v2/development/dev-env-setup?lang=python)


## Pre-Reqs
You will need to set up:

* [Telnyx Account](https://telnyx.com/sign-up?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
* [Telnyx Call Control Application](https://portal.telnyx.com/#/app/call-control/applications)
* [Telnyx Messaging Profile](https://portal.telnyx.com/#/app/messaging)
* [Python and PIP](https://developers.telnyx.com/docs/v2/development/dev-env-setup?lang=python) installed
* Ability to receive webhooks (with something like [ngrok](https://developers.telnyx.com/docs/v2/development/ngrok?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link))
* A MySQL Server to store user data. A simple local database can be set up using [XAMPP](https://www.apachefriends.org/index.html)


## What you can do

* Present users a search for a number to acquire and input a number to forward to
* Once a user has filled out the form, searches and acquires the first result
* Sets up the number in Telnyx with required params
* Forwards any call coming into the purchased numbers towards the number setup
* Tracks the inbound calls that were made and gives duration
* Supports multiple numbers

## Usage

### .env file

This app uses the excellent [python-dotenv](https://github.com/theskumar/python-dotenv) package to manage environment variables.

Make a copy of [`.env.sample`](./.env.sample) and save as `.env` and update the variables to match your creds.

```
TELNYX_API_KEY="YOUR_API_KEY"
TELNYX_CONNECTION_ID="YOUR_CONNECTION_ID"
MESSAGING_PROFILE_ID="YOUR_MESSAGING_PROFILE_ID"

DATABASE_HOST="localhost"
DATABASE_USER="root"
DATABASE_PASSWORD=""
DATABASE_NAME="cctracker"
```

### Callback URLs For Telnyx Applications

| Callback Type                    | URL                              |
|:---------------------------------|:---------------------------------|
| Inbound Call-Control Callback  | `{ngrok-url}/call-control/inbound`  |
| Outbound Call-Control Callback | `{ngrok-url}/call-control/outbound` |


## Installation

### Environment Setup

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

At this point you can point your application to generated ngrok URL + path  (Example: `http://{your-url}.ngrok.io/call-control/inbound`).

### Telnyx Portal Setup

In the [Portal](https://portal.telnyx.com/)
* Create call control application and callback to ngrok
* Create messaging profile

### Run

#### Create Database and Tables

First, make sure you have created your database in MySQL

```sql
CREATE DATABASE cctracker
```

Then, run `database.py` to create our tables in the database we specified in `database.py` (in this case being `calltracker` and `forwardedphonenumbers`)

#### Start the server

Start the server `python app.py`

When the application is started, flask serves it to the port specified in the .env file (Default 8000), so you can simply take a look at the application at localhost:8000.

Once everything is set up, you should now be able to:
* Search and purchase specified phone numbers
* Have those numbers be setup for forwarding towards your designated number
