# Wrapper function for initiating a new verification with Telnyx API
import telnyx
import os

def CreateVerification(phone_number):
    try:
        payload = {
            "phone_number": phone_number,
            "verify_profile_id": os.getenv("VERIFY_PROFILE_ID"),
            "type": "sms",
            "timeout": 300
        }
        result = telnyx.Verification.create(**payload)
        return result
    except Exception as e:
        print("Error Creating Verification")
        return

# Wrapper function for submitting a new verification code with Telnyx API
def SubmitVerificationCode(code, phone_number):
    try:
        verification = telnyx.Verification()
        result = verification.verify_by_phone_number(code=code, phone_number=phone_number)
        return result
    except Exception as e:
        print("Error Validating")
        return
