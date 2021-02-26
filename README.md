<div align="center">

# Telnyx Python Getting Started

![Telnyx](logo-dark.png)

</div>

## Documentation & Tutorial

The full documentation and tutorial is available on [developers.telnyx.com](https://developers.telnyx.com/docs/v2/development/dev-env-setup?lang=dotnet&utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)

## Pre-Reqs

Generall you will need to set up:

* [Telnyx Account](https://telnyx.com/sign-up?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
* [Telnyx Phone Number](https://portal.telnyx.com/#/app/numbers/my-numbers?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) enabled with:
  * [Telnyx Call Control Application](https://portal.telnyx.com/#/app/call-control/applications?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
  * [Telnyx Outbound Voice Profile](https://portal.telnyx.com/#/app/outbound-profiles?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)
  * [Telnyx Messaging Profile](https://portal.telnyx.com/#/app/messaging)
* Ability to receive webhooks (with something like [ngrok](https://developers.telnyx.com/docs/v2/development/ngrok?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link))
* [Python & PIP](https://developers.telnyx.com/docs/v2/development/dev-env-setup?lang=python&utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) installed

## What you can do

| Example                                          | Description                                                                                                         |
|:-------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------|
| [Flask Messaging](flask-messaging)               | Example working with inbound MMS & SMS messages, downloading media from inbound MMS, and uploading media to AWS S3. |
| [TeXML Call Center](call-center-texml)           | Call center solution using aiohttp and Telnyx TeXML.                                                                |
| [Webinar Messaging Demo](webinar-messaging-demo) | Example auto-responder with MMS and webhook validation.                                                             |
| [Secret Santa Generator](flask-secret-santa)     | Example project that generates secret santa assignments and texts all participants using Telnyx Messaging.          |
| [Flask Call Control](flask-call-control)         | Simple call control project that handles inbound calls by speaking text and can create an outbound call to a number specified by the user. |

### Install

Run the following commands to get started

```
$ git clone https://github.com/team-telnyx/demo-python-telnyx.git
```
