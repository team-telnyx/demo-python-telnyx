import telnyx
import os
import json
from dotenv import load_dotenv
from flask import Flask, render_template, request, Response, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from peewee import *

load_dotenv()

# Keys/IDs/Secrets
telnyx.api_key = os.getenv("TELNYX_API_KEY")

telnyxConnectionId = os.getenv("TELNYX_CONNECTION_ID")
telnyxMessagingId = os.getenv("MESSAGING_PROFILE_ID")
database_user = os.getenv("DATABASE_USER")

mysql_db = MySQLDatabase(os.getenv('DATABASE_NAME'),
                         user=os.getenv('DATABASE_USER'),
                         password=os.getenv('DATABASE_PASSWORD'),
                         host=os.getenv('DATABASE_HOST'),
                         port=3306,
                         )

app = Flask(__name__)
SECRET_KEY = "SecretKey"

# Database setup, WIP
class BaseModel(Model):
    class Meta:
        database = mysql_db


class CallTracker(BaseModel):
    from_cnam_lookup = CharField()
    from_number = CharField()
    date = CharField()
    duration = CharField
    state_of_call = CharField()


class ForwardedPhoneNumbers(BaseModel):
    purchased_number = CharField(unique=True)
    forward_number = CharField()
    tag = TextField()


#Create tables, can be used
#mysql_db.create_tables([CallTracker, ForwardedPhoneNumbers])


# homepage
@app.route('/')
def index():
    all_phone_numbers = ForwardedPhoneNumbers.select()
    phone_data = ForwardedPhoneNumbers.select('id')
    print(phone_data)

    return render_template('index.html', phone_nummbers=all_phone_numbers)


@app.route("/number/acquire", methods=['POST'])
def acquire():
    # body = json.loads(request.data)
    administrative_area = request.form["state"]
    locality = request.form["city"]
    forward_number = request.form["forward_number"]
    tag = request.form["tag"]

    number_search = telnyx.AvailablePhoneNumber.list(filter={
        "locality": locality,
        "rate_center": administrative_area,
        "features": "sms",
        "limit": "1",
        "quickship": True,
    })

    print(number_search)
    number_to_order = number_search.data[0]["phone_number"]
    number_order_response = telnyx.NumberOrder.create(
        phone_numbers=[
            {"phone_number": number_to_order,
             },
        ],
        messaging_profile_id=telnyxMessagingId,
        connection_id=telnyxConnectionId,
    )

    purchased_number = number_to_order

    phone_data = ForwardedPhoneNumbers.create(
        purchasedNumber=purchased_number,
        forwardNumber=forward_number,
        tag=tag
    )
    phone_data.save()

    flash("Phone Number:" + purchased_number + " was purchased successfully!")

    return redirect(url_for('Index'))


@app.route("/number/update", methods=['GET', 'POST'])
def update(id):
    if request.meth == 'POST':
        phone_data = ForwardedPhoneNumbers.query.get(request.form.get('id'))

        phone_data = ForwardedPhoneNumbers.create(
            purchasedNumber=purchased_number,
            forwardNumber=forward_number,
            tag=tag)


@app.route("/number/delete/<id>/", methods=['GET', 'POST'])
def delete(id):
    my_data = ForwardedPhoneNumbers.query.get(id)
    phone_number = ForwardedPhoneNumbers.select().select_from(
        ForwardedPhoneNumbers.purchasedNumber).where(
        ForwardedPhoneNumbers.id == 1)

    flash("Phone Number Successfully Deleted")

    return redirect(url_for('Index'))


if __name__ == "__main__":
    telnyx.api_key = telnyx.api_key
    TELNYX_APP_PORT = "8000"
    app.run(port=TELNYX_APP_PORT)
