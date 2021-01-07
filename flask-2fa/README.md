<div align="center">

# Telnyx-Python Verify Example

![Telnyx](../logo-dark.png)

Sample application demonstrating Telnyx-Python Verify

</div>

## Documentation & Tutorial

The full documentation and tutorial is available on [developers.telnyx.com](https://developers.telnyx.com/docs/v2/development/dev-env-setup?lang=dotnet&utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)

## Pre-Reqs

You will need to set up:

* [Telnyx Account](https://telnyx.com/sign-up?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
* [Telnyx Verify Profile](https://portal.telnyx.com/#/app/verify/profiles)
* [Python and PIP](https://developers.telnyx.com/docs/v2/development/dev-env-setup?lang=python) installed
* A MySQL Server to store user data. A simple local database can be set up using [XAMPP](https://www.apachefriends.org/index.html).

## What you can do

* Present users a signup/login form
* Once a user has signed up, send them a verification code
* Submit the verification code to verify the profile
* Add the user to the MySQL database

## Usage

The following environmental variables need to be set

| Variable               | Description                                                                                                                                              |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `TELNYX_API_KEY`       | Your [Telnyx API Key](https://portal.telnyx.com/#/app/api-keys?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)              |
| `TELNYX_VERIFY_KEY`    | Your [Telnyx Public Key](https://portal.telnyx.com/#/app/account/public-key?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) |
| `TELNYX_APP_PORT`      | **Defaults to `8000`** The port the app will be served.                                                                                                  |
| `DB_SERVER_NAME`       | The URL or server where the MySQL database is located.                                                                                                   |
| `DB_USERNAME`          | The database username.                                                                                                                                   |
| `DB_PASSWORD`          | The database password.                                                                                                                                   |
| `DB_NAME`              | The database name which holds the table we want to access.                                                                                               |
### .env file

This app uses the excellent [python-dotenv](https://github.com/theskumar/python-dotenv) package to manage environment variables.

Make a copy of [`.env.sample`](./.env.sample) and save as `.env` and update the variables to match your creds.

```
TELNYX_API_KEY="YOUR_API_KEY"
TELNYX_VERIFY_KEY="YOUR_VERIFY_KEY"
TELNYX_APP_PORT=8000

DB_SERVER_NAME="localhost"
DB_USERNAME="root"
DB_PASSWORD=""
DB_NAME="users"
```

### Install

Run the following commands to get started

```
$ git clone https://github.com/team-telnyx/demo-python-telnyx.git
```

### Run

Start the server `python main.py`

When the application is started, flask serves it to the port specified in the .env file (Default 8000), so you can sipmly take a look at the application at localhost:8000.

**Note: You must enter phone number in E.164 format (i.e. +12345678910) for the code to be sent correctly.**

Once everything is setup, you should now be able to:
* Sign up/Login users.
* Verify their phone numbers by submitting a pin code sent to the device.
