import random
import string
import datetime
import telnyx
import time


api_keys = ["your-api-keys"]
webhook_url = "http://google.com"


def main():
    script_id = generate_script_id()
    print(f"Script Id: {script_id}")
    for api_key in api_keys:
        telnyx.api_key = api_key
        ovp = create_ovp(script_id)
        print(f"OVP Id: {ovp.id}")
        cc_app = create_cc_app(script_id, ovp.id, webhook_url)
        print(f"CC App ID: {cc_app.id}")
        number = search_order_associate_phone_number(script_id, cc_app.id)
        print(f"Ordered {number}")


def create_ovp(script_id):
    payload = {
        "name": script_id,
        "whitelisted_destinations": ["BR", "US"]
    }
    try:
        result = telnyx.OutboundVoiceProfile.create(**payload)
        return result
    except Exception as e:
        print("Error creating OVP ")
        raise e


def create_cc_app(script_id, ovp_id, webhook_event_url):
    payload = {
        "application_name": script_id,
        "webhook_event_url": webhook_event_url,
        "webhook_api_version": "2",
        "outbound": {
            "outbound_voice_profile_id": ovp_id
        }
    }
    try:
        result = telnyx.CallControlApplication.create(**payload)
        return result
    except Exception as e:
        print("Error creating CC App ")
        raise e


def search_order_associate_phone_number(script_id, cc_app_id):
    search_payload = {
        "country_code": "BR",
        "national_destination_code": "21",
        "features": "voice",
        "limit": 2
    }
    try:
        numbers = search_phone_numbers(search_payload)
        number_to_order = numbers[0]["phone_number"]
        order_status = order_phone_numbers(script_id, cc_app_id, number_to_order)
        wait_for_order_to_complete(order_status)
        add_tag_to_phone_number(script_id, number_to_order)
        return number_to_order
    except Exception as e:
        print("Error searching and ordering number")
        raise e


def search_phone_numbers(search_payload):
    try:
        numbers = telnyx.AvailablePhoneNumber.list(filter=search_payload)
        return numbers.data
    except Exception as e:
        print("Error searching Numbers")
        raise e


def order_phone_numbers(script_id, cc_app_id, phone_number):
    order_payload = {
        "phone_numbers": [{"phone_number": phone_number}],
        "connection_id": cc_app_id,
        "customer_reference": script_id
    }
    try:
        number_order = telnyx.NumberOrder.create(**order_payload)
        return number_order
    except Exception as e:
        print("Error ordering numbers")
        raise e


def wait_for_order_to_complete(number_order):
    telnyx_response = telnyx.NumberOrder.retrieve(number_order.id)
    while telnyx_response.status == 'pending':
        telnyx_response = telnyx.NumberOrder.retrieve(number_order.id)
        time.sleep(.25)
    return telnyx_response


def add_tag_to_phone_number(script_id, number):
    try:
        telnyx_number = telnyx.PhoneNumber.retrieve(number)
        telnyx_number.tags = [script_id]
        telnyx_number.save()
    except Exception as e:
        print(f"Error adding tag to {number}")
        raise e


def generate_script_id():
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    unique_string = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"{today_date}_{unique_string}"


if __name__ == "__main__":
    main()
