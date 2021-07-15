<div align="center">

# Telnyx-Python Call Control Setup Example

![Telnyx](../logo-dark.png)

Sample application demonstrating Telnyx-Python And Call-Control Setup

</div>

## Documentation & Tutorial

The full documentation and tutorial is available on [developers.telnyx.com](https://developers.telnyx.com/docs/v2/development/dev-env-setup?lang=dotnet&utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)

## Pre-Reqs

You will need to set up:

* [Telnyx Account](https://telnyx.com/sign-up?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link)

## What you can do

* Console Application to configure an account with a:
    * [Outbound Voice Profile (OVP)](https://portal.telnyx.com/#/app/outbound-profiles)
    * [Call Control Application (with the OVP)](https://portal.telnyx.com/#/app/call-control/applications)
    * [Phone Number (association the call control application)](https://portal.telnyx.com/#/app/numbers/my-numbers)


## Usage

The following variables need to be set in the application

| Variable         | Description                                                                                                                                 |
|:-----------------|:--------------------------------------------------------------------------------------------------------------------------------------------|
| `TELNYX_API_KEY` | Your [Telnyx API Key](https://portal.telnyx.com/#/app/api-keys?utm_source=referral&utm_medium=github_referral&utm_campaign=cross-site-link) |
| `WEBHOOK_URL`    | Your Server's URL for call-control events                                                                                                   |


### Install

Run the following commands to get started

```
$ git clone https://github.com/team-telnyx/demo-python-telnyx.git
$ cd demo-python-telnyx/console-call_control_setup
```

Install the dependencies:

```
pip install telnyx
```

### Run

Run the script `python app.py`

