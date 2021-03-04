import os
from dotenv import load_dotenv
from peewee import *
from peewee import CharField


load_dotenv()

mysql_db = MySQLDatabase(os.getenv('DATABASE_NAME'),
                         user=os.getenv('DATABASE_USER'),
                         password=os.getenv('DATABASE_PASSWORD'),
                         host=os.getenv('DATABASE_HOST'),
                         port=3306,
                         )

# Database setup

# inheritance for Meta (peewee), assigns DB to subsequent DB classes
class BaseModel(Model):
    class Meta:
        database = mysql_db

# peewee constructs id primary keys automatically (they are required to make queries)
class CallTracker(BaseModel):
    from_cnam_lookup = CharField()
    from_number = CharField()
    purchased_number = CharField()
    forward_number = CharField()
    date = CharField()
    duration_of_call = CharField()


class ForwardedPhoneNumbers(BaseModel):
    purchased_number = CharField()
    city_state = CharField()
    forward_number = CharField()
    tag = TextField()


class MessageStorage(BaseModel):
    message_body = CharField()
    from_number = CharField()


# Create tables function
mysql_db.connect()
mysql_db.create_tables([CallTracker, ForwardedPhoneNumbers])
