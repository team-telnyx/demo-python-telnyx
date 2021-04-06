import telnyx
import os
from dotenv import load_dotenv

load_dotenv()


def main():
    phone_number = (input("Phone Number to Verify?: ")).strip()
    send_verification_code(phone_number)
    verify_code(phone_number)
    go_again = (input("Would you like to verify a new phone number (y/n)?: ")).lower().strip()
    if go_again == "y":
        main()
    else:
        print("Thanks")


def send_verification_code(phone_number):
    payload = {
        "phone_number": phone_number,
        "verify_profile_id": os.getenv("VERIFY_PROFILE_ID"),
        "type": "sms",
        "timeout": 300
    }
    try:
        result = telnyx.Verification.create(**payload)
        print("Verification code sent")
    except Exception as e:
        print("Error sending verification code")
        raise e


def verify_code(phone_number):
    verification = telnyx.Verification()
    attempts = 0
    while attempts < 5:
        code = (input("Verification code?: ")).strip()
        attempts += 1
        try:
            result = verification.verify_by_phone_number(code=code, phone_number=phone_number)
            if result.data.response_code == "accepted":
                print("Code successfully verified")
                break
            else:
                print("Code verification failed")
                if attempts >= 5:
                    print("Verification max attempts reached")
        except Exception as e:
            print("Error verifying code")


if __name__ == "__main__":
    telnyx.api_key = os.getenv("TELNYX_API_KEY")
    main()
