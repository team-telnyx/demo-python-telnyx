# Python Flask 2FA Demo

Example skeleton project that implements Telnyx 2FA in Python using Flask.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install telnyx.

```bash
pip install telnyx
```

## Setup
Ensure to enter valid values for your **Telnyx API  Key** and **2FA Profile ID** at the top of the main file.

```python
API_KEY = "YOUR_API_KEY"
TWOFA_KEY = "YOUR_TWOFA_KEY"
```

## User Management
This project stores users in memory for the purposes of this example. In a production environment, a traditional database would be appropriate. 

## Usage

Fire up the flask server by running the main file and opening up web browser to ```127.0.0.1:5000/signup```
```bash
python main.py
```