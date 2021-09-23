<div align="center">

# Telnyx-Python Fax and Email Webinar Demo

![Telnyx](../logo-dark.png)

Sample application demonstrating a Telnyx-Python Voicemail to Email

</div>

## Documentation & Tutorial

The full documentation and tutorial is currently being constructed. Please reference the High-Level Overview section at this time on what needs to be accomplished if you would like to construct this yourself.
## Pre-Reqs

You will need to set up:

* [Telnyx Account](https://telnyx.com/sign-up?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
* [Telnyx Phone Number](https://portal.telnyx.com/#/app/numbers/my-numbers?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) enabled with:
  * [Telnyx Call Control Application](https://portal.telnyx.com/#/app/call-control/applications)
  * [Telnyx Outbound Voice Profile](https://portal.telnyx.com/#/app/outbound-profiles?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
* Ability to receive webhooks (with something like [ngrok](https://developers.telnyx.com/docs/v2/development/ngrok?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link))
* [Python & PIP](https://developers.telnyx.com/docs/v2/development/dev-env-setup?lang=python&utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) installed
* [SMTP Access](mailgun.com)
  * We will be using google's SMTP server for this process ([SMTP](https://support.google.com/a/answer/176600?hl=en))

## What you can do

* Construct a pseudo Voice Mail service with the use of the recording API along with Transcription
* Attach the recording file along with transcription to an email of your choice
* Send email to your desired email address

## Usage

The following environmental variables need to be set

| Variable                   | Description                                                                                                                                              |
|:---------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `TELNYX_API_KEY`           | Your [Telnyx API Key](https://portal.telnyx.com/#/app/api-keys?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)              |
| `TELNYX_PUBLIC_KEY`        | Your [Telnyx Public Key](https://portal.telnyx.com/#/app/account/public-key?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) |
| `TELNYX_CALL_CONTROL_ID`   | The [connection id](https://portal.telnyx.com/#/app//call-control/applications) for your call control application                                        |
| `SMTP_GMAIL_DOMAIN`         | Your new [GMAIL] domain                                                                                                                                  |
| `SMTP_GMAIL_PASSWORD`       | Your new GMAIL domain's password                                                                                                                         |
| `PORT`                     | **Defaults to `8000`** The port the app will be served                                                                                                   |

### .env file

This app uses the excellent [python-dotenv](https://github.com/theskumar/python-dotenv) package to manage environment variables.

Make a copy of [`.env.sample`](./.env.sample) and save as `.env` and update the variables to match your creds.

```
TELNYX_PUBLIC_KEY="+kWXUag92mcUMFQopVlff7ctD/m2S/IoXv+AlI1/5a0="
TELNYX_API_KEY="KEYI"
TELNYX_CALL_CONTROL_ID=36092346987
SMTP_GMAIL_DOMAIN="example@gmail.com"
SMTP_GMAIL_PASSWORD ="examplestrongpassword"
PORT=8000
```

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

## Highlevel Code Overview

We will be constructing a Voicemail to Email service using Flask and Python.

Currently, we have an example application that acts as a pseudo-voicemail service by utilizing the record API. After a beep, the recording starts and an inbound caller is able to leave a message at a specific phone number. After call completion, we get the transcript of the call as well as the recording saved to our system. An example of this project is found [here](https://github.com/team-telnyx/demo-python-telnyx/tree/master/flask-transcription-voicemail_call-coontrol)

After we get both the voice file and the transcript to our system, we will want to send this outwards to our destination. The easiest way to accomplish this would be to use a SMTP server. SMTP stands for Simple Mail Transfer Protocol, which gives direct access to the ability to communicate from one service to another. Python has an inbuilt module called `smtplib` which will be perfect for our use case here. 

What esentially will be constructed is an addition to the above demo. We will add a function at the end of the code response to invoke the consctruction of an email using Python's inbuild mail service properties, then send that email to our desired destination. A quick reference guide can be found [here](https://levelup.gitconnected.com/send-email-using-python-30fc1f203505) on this process that this demo will utilize. 

A rough code sample of the constructed function addition to go at end of the above project: 

```import smtplib
import mimetypes
from email.message import EmailMessage

message = EmailMessage()

// Our sender/sendee params.
sender = "your-name@gmail.com"
recipient = "example@example.com"
message['From'] = sender
message['To'] = recipient

// Subject of email, we will be getting PhoneNumber from previous steps
message['Subject'] = 'Here is your recent voicemail coming from' + SenderPhoneNumber

// Body construction, we will be stringifying transcript from previous application and inserting into body here.
body = """Hello
Transcription of the voicemail that was sent:""" + str.TranscriptionFromTelnyx
message.set_content(body)

// To send attachments, we will need to extract mime values to utilize the SMTP service effectively
mime_type, _ = mimetypes.guess_type('Transcription.mp3')
mime_type, mime_subtype = mime_type.split('/')

// This is us attaching our transcript to our email
with open('something.mp3', 'rb') as file:
 message.add_attachment(file.read(),
 maintype=mime_type,
 subtype=mime_subtype,
 filename='something.pdf')
print(message)

// invoking server and sending our message to our desired email
mail_server = smtplib.SMTP_SSL('smtp.gmail.com')
mail_server.set_debuglevel(1)
mail_server.login("your-name@gmail.com", 'Your password')
mail_server.send_message(message)
mail_server.quit()
```
All of the above should be a seperate function and invoked once we get a call.ended webhook response from our server. This should result in a successful voicemail to email service! 