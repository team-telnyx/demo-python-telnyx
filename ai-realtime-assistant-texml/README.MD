# Speech Assistant with Telnyx Voice and the OpenAI Realtime API (Python)

This application demonstrates how to use Python, [Telnyx Voice](https://developers.telnyx.com/docs/voice/programmable-voice/get-started) and [TeXML](https://developers.telnyx.com/docs/voice/programmable-voice/texml-setup), and [OpenAI's Realtime API](https://platform.openai.com/docs/) to make a phone call to speak with an AI Assistant.

The application opens websockets with the OpenAI Realtime API and Telnyx, and sends voice audio from one to the other to enable a two-way conversation.

This application uses the following Telnyx products in conjuction with OpenAI's Realtime API:

- Voice (TeXML, WebRTC)
- Phone Numbers

## Prerequisites

To use the app, you will  need:

- **A Telnyx account.** You can [sign up for free](https://telnyx.com/sign-up).
- **Python 3+** You can download from [here](https://www.python.org/downloads/).
- **A Telnyx number with _Voice_ capabilities.** You can find [a walkthrough to purchase a phone number here](https://support.telnyx.com/en/articles/4380325-search-and-buy-numbers).
- **An OpenAI account and an OpenAI API Key.** You can [sign up here](https://platform.openai.com/).
- **OpenAI Realtime API access.**

## Local setup overview

This project can be summarized by the following:

1. Forward incoming traffic on the desired port to the internal address of your application, also known as a port forward. This can be done in a variety of ways:
   - Manually port forward by configuring your router settings (not recommended as it might expose your network)
   - Use a tunneling provider
      - [Ngrok](https://ngrok.com/).
      - [Expose](https://expose.dev/).
      - [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/run-tunnel/)

      This guide will be demonstrating setting up this project using ngrok, but most tunneling providers would suffice by providing a safe, encrypted connection between your local machine and the internet. This is how your application will be able to talk to the Telnyx and OpenAI ecosystem.
2. Setup your Telnyx account with a successfully procured [phone number that has Voice capabilities](https://support.telnyx.com/en/articles/4380325-search-and-buy-numbers)
3. Update and fill out the ```.env``` file, making sure to remove the ```.sample``` suffix
4. Install the dependencies and packages
5. Run the project!

### Open an ngrok tunnel

Port forwarding is a networking technique that allows devices on a private network (LAN) to be accessed by devices on an external network (WAN) by directing incoming traffic from a specified port on the WAN to a specific device or service within the LAN. A drawback of this is that you're opening a hole into your network and with a slight misconfiguration, this could lead to your LAN being compromised.

Easy way to circumvent some of these drawbacks is to tunnel with a tool like ngrok. We won't have to mess with network configurations on the router level (especially useful if you are stuck behind [a double NAT scenario](https://kb.netgear.com/30186/What-is-double-NAT-and-why-is-it-bad)), provides [encryption at rest](https://ngrok.com/security#:~:text=All%20data%20is%20encrypted%20at,keys%20that%20only%20we%20control.) and can be raised and killed with a few basic commands.

#### Open a Terminal and run

```
ngrok http 8000
```

You should see something akin to:

```
$ ./ngrok http 8000

ngrok by @inconshreveable

Session Status                online
Account                       Little Bobby Tables (Plan: Free)
Version                       2.x.x
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    http://ead8b6b4.ngrok.io -> localhost:8000
Forwarding                    https://ead8b6b4.ngrok.io -> localhost:8000

Connections                   ttl     opn     rt1.   rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

Once the tunnel has been opened and brought online, copy the `Forwarding` URL. It will look something like: `https://[your-ngrok-subdomain].ngrok.app`.

Once you've set up `ngrok` or another tunneling service, we will need to tell Telnyx to route it correctly.

#### Adding the public proxy URL to your Inbound Settings  in the Mission Control Portal

To do this, click  the edit symbol [✎] next to your [[TeXML Application](https://portal.telnyx.com/#/app/call-control/applications)](https://portal.telnyx.com/#/call-control/texml)

In the **"App Info"** > **"Send a webhook to the URL: (Required)"** field, paste the forwarding address from ngrok into the Webhook URL field. Add `/inbound` to the end of the URL to direct the request to the webhook endpoint in your server.

> Make sure that the Voice method is **POST**

In this example, the URL will be `http://ead8b6b4.ngrok.io/inbound`.

Note that the `ngrok` command above forwards to a development server running on port `8000`, which is the default port configured in this application. If
you override the `PORT` defined in your root application file, you will need to update the `ngrok` command accordingly.

Keep in mind that each time you run the `ngrok http` command, a new URL will be created, and you'll need to update it everywhere it is referenced below.

## Run the App

Once ngrok is running and Telnyx is configured properly, fill out the `.env.sample` file with your secret.
> **Note:** Make sure to remove the ```.sample``` portion in the suffix and save it as just a ```.env``` file.

We can install the dependencies of the repo with:

```
pip install -r requirements.txt
```

and run the dev server with the following command:

```
python3 main.py
```

## Test the app

Now you should be able to call the phone number and get a friendly AI assistant to answer and help with your requests!
