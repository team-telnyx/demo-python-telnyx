import telnyx
import os
import math
from flask import redirect, url_for, flash
from datetime import datetime


def telnyx_number_acquire(locality, administrative_area):
    city_state_combo = locality + ", " + administrative_area
    number_search = telnyx.AvailablePhoneNumber.list(filter={
        "locality": locality,
        "rate_center": administrative_area,
        "features": "sms",
        "limit": "1",
        "quickship": True,
    })
    # catch no result error
    if number_search.metadata.total_results != 1:
        flash("No results found for specified area, "
              "try again! Watch our for typos!")
        return redirect(url_for('index'))
    else:
        number_to_order = number_search.data[0]["phone_number"]
        number_order_response = telnyx.NumberOrder.create(
            phone_numbers=[
                {"phone_number": number_to_order,
                 },
            ],
            messaging_profile_id=os.getenv("MESSAGING_PROFILE_ID"),
            connection_id=os.getenv("TELNYX_CONNECTION_ID"),
        )
        return number_to_order, city_state_combo


def telnyx_number_delete(number_to_delete):
    retrieve = telnyx.PhoneNumber.retrieve(number_to_delete)
    retrieve.delete()


def telnyx_cnam_lookup(calling_number):
    resource = telnyx.NumberLookup.retrieve(calling_number)
    if resource.caller_name is None:
        cnam_info = "Not Available"
        return cnam_info
    else:
        cnam_info = resource.caller_name
        return cnam_info

# date and time difference function
def difference(start_time, end_time):
    end_time = ''.join(end_time)
    start_time = ''.join(start_time)
    d1 = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    d2 = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    d3 = d1 - d2
    d4 = d3.total_seconds()
    duration = math.ceil(d4)
    date = d2.date()
    return duration, date
