<div align="center">

# Telnyx-Python Secret Santa Generator

![Telnyx](../logo-dark.png)

Sample application that automatically texts all participants in a secret santa their assigned person!

</div>

## Pre-Reqs

You will need to set up:

* [Telnyx Account](https://telnyx.com/sign-up?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
* [Telnyx Phone Number](https://portal.telnyx.com/#/app/numbers/my-numbers?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
* [Telnyx Messaging Profile](https://portal.telnyx.com/#/app/messaging?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
* [Python & PIP](/docs/v2/development/dev-env-setup?lang=python&utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) installed

## What you can do

* Launch site with form to submit multiple participants in Secret Santa
* Have the assignments automatically sent to each participant's phone number

## Usage

The following environmental variables need to be set

| Variable               | Description                                                                                                                                              |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `TELNYX_API_KEY`       | Your [Telnyx API Key](https://portal.telnyx.com/#/app/api-keys?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)              |
| `TELNYX_PHONE NUMBER`  | Your [Telnyx Phone Number](https://portal.telnyx.com/#/app/my-numbers?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)       |
| `APP_PORT`             | **Defaults to `5000`** The port the app will be served                                                                                                   |

### Requirements

This app uses several pip packages to execute. To install run the following:

```
$ pip install [requirement]
```

Requirements:
```
telnyx
os
random
phonenumbers
dotenv
flask
```

### .env file

This app uses the excellent [python-dotenv](https://github.com/theskumar/python-dotenv) package to manage environment variables.

Make a copy of [`.env.sample`](./.env.sample) and save as `.env` and update the variables to match your creds.

```
TELNYX_API_KEY="YOUR_API_KEY"
TELNYX_NUMBER="YOUR_TELNYX_NUMBER"
APP_PORT=5000
```

### Install

Run the following commands to get started

```
$ git clone https://github.com/d-telnyx/demo-python-telnyx.git
```

### Run

Start the server `python main.py`

Once everything is setup, you should now be able to:
* Run the server and access it at localhost:PORT (i.e. localhost:5000)
* Add participants to the secret santa and have their pairs generated
* Have texts sent to all participants informing them who they are buying presents for!

Happy Holidays!
