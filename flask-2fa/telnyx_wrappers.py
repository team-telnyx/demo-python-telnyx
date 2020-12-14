# Wrapper function for initiating a new verification with Telnyx API
import requests
import config
import os

def CreateVerification(phone_number):
    url = "https://api.telnyx.com/v2/verifications"
    auth = "Bearer " + os.getenv("API_KEY")
    headers  = {
        "Authorization": auth,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "phone_number": phone_number,
        "verify_profile_id": os.getenv("VERIFY_KEY"),
        "type": "sms",
        "timeout": 300
    }
    r = requests.post(url, headers=headers, json=payload)
    return r

# Wrapper function for submitting a new verification code with Telnyx API
def SubmitVerificationCode(code, phone_number):
    url = "https://api.telnyx.com/v2/verifications/by_phone_number/" + phone_number + "/actions/verify"
    auth = "Bearer " + os.getenv("API_KEY")
    headers  = {
        "Authorization": auth,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "code": code
    }
    r = requests.post(url, headers=headers, json=payload)
    return r