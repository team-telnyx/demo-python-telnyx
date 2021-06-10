<div align="center">

# Telnyx-Python Guess Number Call Control

![Telnyx](../logo-dark.png)

Sample application demonstrating Telnyx-Python Call Control

</div>


## Documentation & Tutorial

The full documentation and tutorial is available on [developers.telnyx.com](https://developers.telnyx.com/docs/v2/development/dev-env-setup?lang=dotnet&utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)

## Setup Telnyx

- Complete the steps outlined on the [Call Control > Quickstarts > Portal Setup](https://developers.telnyx.com/docs/v2/call-control/quickstart) developer page
- You will:
    - Sign up for a Telnyx account
    - Create an application to configure how you connect your calls
    - Buy or port a phone number to receive inbound calls, and assign this number to your new application
    - Create an outbound voice profile to make outbound calls, and assign your application to this new profile.

## Setup Localhost App

- Clone this repository and change directory to this project folder
- Run `pip install -r requirements.txt`
- Run `cp .env.sample .env` and enter the following values into the `.env` file:
    - [Telynx API Key](https://portal.telnyx.com/#/app/api-keys)
    - [Public Key](https://portal.telnyx.com/#/app/api-keys/public-key)
    - Call control application's 'Connection ID'
    - Purchased Telnyx phone number
    - Phone number to receive call
- Start the server `python app.py`

## Setup Reverse Proxy to Localhost

For your localhost app to receive webhooks from Telnyx, we recommend the use of [ngrok](https://ngrok.com/):
- Sign up for a free account and follow the ngrok 'Setup & Installation' guide. When running the `ngrok` tool, be sure to change the port value from `80` to `5000` (the port our app is listening on).
- Once the `ngrok` process is running on your localhost, copy the forwarding https address (e.g., https://4f7e5039ecb9.ngrok.io)
- On your [Telnyx Call Control Application](https://portal.telnyx.com/#/app/call-control/applications), update the webhook url with the copied forwarding url and append the defined webhooks path (e.g., https://4f7e5039ecb9.ngrok.io/webhooks)
- Save the changes made to call control application
- You should now be able to trigger a phone call by loading the [http://localhost:5000/dial](http://localhost:5000/dial) page

