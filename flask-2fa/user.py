# Class to contain user information and describe equality
class User:
    def __init__(self, username, password, phone_number=None, verified=False):
        self.username = username
        self.password = password
        self.phone_number = phone_number
        self.verified = verified

    def update_username(self, username):
        self.username = username
    
    def update_password(self, password):
        self.password = password
    
    def update_phone_number(self, phone_number):
        self.phone_number = phone_number

    def update_verified_status(self, verified):
        self.verified = verified

    def __eq__(self, other):
        return self.username == other.username