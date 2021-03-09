<div align="center">

# Telnyx-Python Fax and Email Webinar Demo

![Telnyx](../logo-dark.png)

Sample application demonstrating Telnyx-Python Faxing to and From Email

</div>

## Documentation & Tutorial

The full documentation and tutorial is available on [developers.telnyx.com](https://developers.telnyx.com/docs/v2/development/dev-env-setup?lang=dotnet&utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)

## Pre-Reqs

You will need to set up:

* [Telnyx Account](https://telnyx.com/sign-up?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
* [Telnyx Phone Number](https://portal.telnyx.com/#/app/numbers/my-numbers?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) enabled with:
  * [Telnyx Fax Application](https://portal.telnyx.com/#/app/fax/applications)
  * [Telnyx Outbound Voice Profile](https://portal.telnyx.com/#/app/outbound-profiles?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
* Ability to receive webhooks (with something like [ngrok](https://developers.telnyx.com/docs/v2/development/ngrok?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link))
* [Python & PIP](https://developers.telnyx.com/docs/v2/development/dev-env-setup?lang=python&utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) installed
* AWS Account setup with proper profiles and groups with IAM for S3. See the [Quickstart](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) for more information.
  * Only needed for email *to* fax
* [Mailgun Account](mailgun.com)
  * Mailgun Account with the ability to setup [inbound routes](https://app.mailgun.com/app/receiving/routes) (for email *to* fax; not needed for fax *to* email)
* Previously created S3 bucket with public permissions available.

## What you can do

* Send an SMS or MMS and receive a copy of the attachments back to your phone number
* Upload a file to AWS S3
* Send those file as an MMS via Telnyx

## Usage

The following environmental variables need to be set

| Variable                   | Description                                                                                                                                              |
|:---------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `TELNYX_API_KEY`           | Your [Telnyx API Key](https://portal.telnyx.com/#/app/api-keys?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)              |
| `TELNYX_PUBLIC_KEY`        | Your [Telnyx Public Key](https://portal.telnyx.com/#/app/account/public-key?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) |
| `TELNYX_S3_BUCKET`         | The name of the bucket to upload the media attachments                                                                                                   |
| `TELNYX_FAX_CONNECTION_ID` | The [connection id](https://portal.telnyx.com/#/app/fax/applications) for your fax application                                                           |
| `MAILGUN_API_KEY`          | Your [Mailgun](https://www.mailgun.com/) API key                                                                                                         |
| `MAILGUN_DOMAIN`           | Your [Mailgun Domain](https://app.mailgun.com/app/sending/domains). Like `sandbox367c5ec1512d458e95f5e5c60f5fe97a.mailgun.org`                           |
| `PORT`                     | **Defaults to `8000`** The port the app will be served                                                                                                   |

### .env file

This app uses the excellent [python-dotenv](https://github.com/theskumar/python-dotenv) package to manage environment variables.

Make a copy of [`.env.sample`](./.env.sample) and save as `.env` and update the variables to match your creds.

```
TELNYX_PUBLIC_KEY="+kWXUag92mcUMFQopVlff7ctD/m2S/IoXv+AlI1/5a0="
TELNYX_API_KEY="KEYI"
TELNYX_S3_BUCKET=telnyx-mms-demo
TELNYX_FAX_CONNECTION_ID=36092346987
MAILGUN_API_KEY="123-432-123"
MAILGUN_DOMAIN="sandbox367c5ec1512d458e95f5e5c60f5fe97a.mailgun.org"
PORT=8000
```

### Callback URLs For Telnyx Applications

| Callback Type   | URL                         |
|:----------------|:----------------------------|
| Fax Callbacks   | `{ngrok-url}/faxes`         |
| Email Callbacks | `{ngrok-url}/email/inbound` |

### Install

Run the following commands to get started

```
$ git clone https://github.com/team-telnyx/demo-python-telnyx.git
```

### Ngrok

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

At this point you can point your application to generated ngrok URL + path  (Example: `http://{your-url}.ngrok.io/faxes`).

## Run

### Highlevel Code Overview

#### Receiving Fax, Sending Email

1. Receive the webhook from Telnyx indicating fax is incoming
2. We only only care about the `fax.received` webhook for `inbound` faxes
3. Extract the `to`/`from` and other information about the fax
4. Download the attachment and save locally
5. Lookup the association between phone_number and email
6. Create and send an email via Mailgun with downloaded media as an attachment

#### Sending Fax

1. Receive webhook from mailgun for incoming email
2. Extract the prefix of the email (`19198675309@MAILGUN_DOMAIN.com`, we want `19198675309`) and prepend the `+`
3. Lookup the association between email and phone_number to determine the `from` phone number
4. Save the first attachment locally
5. Upload the attachment to S3
6. Create and send a fax to the phone number extracted above

### Update "DB"

The app as provided uses a dumb-hard-coded database to minimize dependencies for the sake of examples. There is an in memory database defined at the top that associates an email to a Telnyx number.

```python
DB = [
    {
        "email": "@telnyx.com",
        "phone_number": "+"
    }
]
```

* `phone_number` is a **Telnyx** phone number
* `email` is the email to associate with that phone number

#### Receiving faxes

```
{+19198675309} ==(faxes)==> {telnyx_phone_number} ==(emails)==> {email_as_defined}
```

#### Sending Faxes

```
{email_as_defined} ==(emails)==> {destination_phone_number@MAILGUN_DOMAIN} ==(faxes)==> {destination_phone_number}
```

### Launch the app and update callbacks

Start the server `python app.py`

When you are able to run the server locally, the final step involves making your application accessible from the Internet. So far, we've set up a local web server. This is typically not accessible from the public internet, making testing inbound requests to web applications difficult.

The best workaround is a tunneling service. They come with client software that runs on your computer and opens an outgoing permanent connection to a publicly available server in a data center. Then, they assign a public URL (typically on a random or custom subdomain) on that server to your account. The public server acts as a proxy that accepts incoming connections to your URL, forwards (tunnels) them through the already established connection and sends them to the local web server as if they originated from the same machine. The most popular tunneling tool is `ngrok`. Check out the [ngrok setup](/docs/v2/development/ngrok) walkthrough to set it up on your computer and start receiving webhooks from inbound faxes to your newly created application.

Once you've set up `ngrok` or another tunneling service you can add the public proxy URL to your Inbound Settings  in the Mission Control Portal. To do this, click  the edit symbol [✎] next to your Fax Profile. In the "Inbound Settings" > "Webhook URL" field, paste the forwarding address from ngrok into the Webhook URL field. Add `faxes` to the end of the URL to direct the request to the webhook endpoint in your  server.

For now you'll leave “Failover URL” blank, but if you'd like to have Telnyx resend the webhook in the case where sending to the Webhook URL fails, you can specify an alternate address in this field.

Once everything is setup, you should now be able to:
* Fax your phone number and receive an email
* Email `{19198675309}@domain.com` an attachment to send a fax to {19198675309}
