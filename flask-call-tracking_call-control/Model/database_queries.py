from Model.database import mysql_db, CallTracker, ForwardedPhoneNumbers


def db_fetch_data():
    all_phone_numbers = mysql_db.execute_sql(
        'select * from forwardedphonenumbers').fetchall()
    all_call_data = mysql_db.execute_sql(
        'select * from calltracker').fetchall()
    return all_phone_numbers, all_call_data


# store in our db, save
def db_number_insert(number_to_order, city_state_combo, forward_number, tag):
    phone_data = ForwardedPhoneNumbers.create(
        purchased_number=number_to_order,
        city_state=city_state_combo,
        forward_number=forward_number,
        tag=tag
    )
    phone_data.save()


def db_number_update(id, updated_forward_number, updated_tag):
    my_data = (ForwardedPhoneNumbers
               .update(forward_number=updated_forward_number,
                       tag=updated_tag)
               .where(ForwardedPhoneNumbers.id == id)
               .execute())
    # front end flash for what number was updated
    phone_number = ForwardedPhoneNumbers.get(
        ForwardedPhoneNumbers.id == id).purchased_number
    return phone_number


def db_number_row_identifier(id):
    my_data = ForwardedPhoneNumbers.get(ForwardedPhoneNumbers.id == id)
    number_to_delete = my_data.purchased_number
    return number_to_delete


# deletes numbers from db by id
def db_number_delete(id):
    my_data = ForwardedPhoneNumbers.get(ForwardedPhoneNumbers.id == id)
    my_data.delete_instance()
    my_data.save()


def db_call_delete(id):
    my_data = CallTracker.get(CallTracker.id == id)
    my_data.delete_instance()
    my_data.save()


def db_number_forward_fetch(purchased_number):
    number_to_forward_to = (ForwardedPhoneNumbers
                            .get(ForwardedPhoneNumbers.
                                 purchased_number == purchased_number)
                            .forward_number)
    return number_to_forward_to


def db_call_insert(cnam_info, calling_number, called_number, forward_number, date, duration):
    phone_data = CallTracker.create(
        from_cnam_lookup=cnam_info,
        from_number=calling_number,
        purchased_number=called_number,
        forward_number=forward_number,
        date=date,
        duration_of_call=duration)
    phone_data.save()
