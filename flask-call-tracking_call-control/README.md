<div align="center">

# Telnyx Flask Call Control Tracker

![Telnyx](../logo-dark.png)

Sample application demonstrating Telnyx-Python Call Control and API


</div>

## Documentation

The full documentation is available on [developers.telnyx.com](https://developers.telnyx.com/docs/v2/development/dev-env-setup?lang=python)


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

At this point you can point your application to generated ngrok URL + path  (Example: `http://{your-url}.ngrok.io/call-control/inbound`).

### Telnyx Portal Setup

In the [Portal](https://portal.telnyx.com/)
* Create call control application and callback to ngrok
* Create messaging profile

### Run

#### Create Database and Tables

We will need store data somewhere and have it be recalled in order for this app to work, so we will be using a database. You can use whichever database that you prefer, but in this example here I'll be using MySQL. The process should be relatively the same across most relational databases. 

First we connect to our database. I personally use MySQL Workbench to accomplish this. Take note of the credentials you used, and inset them into the .env sample file.
Specifically, we will need: 

```credentials
DATABASE_HOST=""
DATABASE_USER=""
DATABASE_PASSWORD=""
DATABASE_NAME=""
DATABASE_PORT=""
```

With regard to MySQL, we will need to create a schema which will be acting in lieu of our database.

```sql
CREATE DATABASE cctracker
```

The name will go into the `DATABASE_NAME` portion above, in this case being `cctracker`

After successfully inserting the details, run `database.py` to create our tables in the database we specified in `database.py` (in this case being `calltracker` and `forwardedphonenumbers`)

#### Start the server

Start the server `python app.py`

When the application is started, flask serves it to the port specified in the .env file (Default 8000), so you can simply take a look at the application at localhost:8000.

Once everything is set up, you should now be able to:
* Search and purchase specified phone numbers
* Have those numbers be setup for forwarding towards your designated number
