| [Overview](./VP1.md)  | [Telnyx Prerequisites](./VP2.md) | [Symbl Prerequisites](./VP3.md) | [Telnyx Call Control Conferencing Application](./VP4.md) | [Symbl <-> Telnyx Sentiment IVR](./VP5.md) | [What's Next?](./VP6.md)
| :---: | :---: | :---: | :---: | :---: | :---: |

# AI IVR Workshop

## Overview

Imagine this: You have a customer that calls inbound to an IVR. They, as many of us, are getting increasingly more and more frustrated with the state of robo-calls and long menu's pressing digits to navigate to the department that they need. They voice this frustration over the phone. What if there was an AI that could be processing this and route the call to a live agent right before the customer hangs up, potentially leading to complaint or loss of a sale?

Here we have constructed something that does just that; using a combination of Telnyx's raw Call Control prowess to seamlessly manage and create calls combined with Symbl.ai's intelligent processing of speech recognition, we can create an application that can track a caller's sentiment during a live call and programmatically act upon it. 

This workshop will guide you step by step on how to construct your own AI IVR solution using Telnyx's Call Control capabilities intertwined with Symbl.ai's Voice Processing. We will guide you step-by-step with all that you need to accomplish this.

### [Telnyx Prerequisites](./VP2.md)

1. Sign up for a <strong>Telnyx account</strong>.
2. Create an <strong>application</strong> to configure how you connect your calls.
3. Buy or port a <strong>phone number</strong> to receive inbound calls, and assign this number to your new application.
4. Create an <strong>outbound voice profile</strong> to make outbound calls, and assign your application to this new profile.
5. Find your:
    * [API Key](https://portal.telnyx.com/#/app/api-keys)
    * [Public Key](https://portal.telnyx.com/#/app/api-keys/public-key)
    * [Call Control ID](https://portal.telnyx.com/#/app/call-control/applications) of the application you will create
***

### [Symbl Prerequisites](./VP3.md)

1. Sign up and create an account on the [Symbl Platform](https://platform.symbl.ai/#/login)
2. Find your:
    * App ID
    * App Secret

### [Telnyx Call Control Conferencing Application](./VP4.md)

* Learn how to get started with Telnyx Call Control
* Create a Flask server
* Utilize ngrok to communicate with Telnyx
* Create a conferencing application using the Python SDK

### [Symbl <-> Telnyx Sentiment IVR](./VP5.md)

* Create a more robust conferencing application with conditional arguments
* Incorporate Symbl.ai's voice processing
* Make an intelligent IVR that transfers a call based on sentiment analysis

### [What's Next?](./VP6.md)