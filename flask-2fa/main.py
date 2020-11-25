import telnyx
import requests
import json
from flask import Flask, render_template, redirect, request

# Setup
API_KEY = "YOUR_API_KEY"
TWOFA_KEY = "YOUR_TWOFA_KEY"

# Run flask app and set telnyx API Key
app = Flask(__name__)
telnyx.api_key = API_KEY

# TEMP: Storage Variables for Users (Production would implement a standard database of users)
users = list()
new_user = None
user = None

# Wrapper function for initiating a new 2FA with Telnyx API
def Create2FA(phone_number):
    url = "https://apidev.telnyx.com/v2/verifications"
    auth = "Bearer " + API_KEY
    headers  = {
        "Authorization": auth,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "phone_number": phone_number,
        "twofa_profile_id": TWOFA_KEY,
        "type": "sms",
        "timeout": 300
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    return r

# TEMP: Class to contain user information and describe equality (Production would interact with database of users)
class User:
    def __init__(self, username, password, phone_number=None):
        self.username = username
        self.password = password
        self.phone_number = phone_number

    def update_username(self, username):
        self.username = username
    
    def update_password(self, password):
        self.password = password
    
    def update_phone_number(self, phone_number):
        self.phone_number = phone_number

    def __eq__(self, other):
        return self.username == other.username

# Homepage redirects to user welcome if someone logged in, otherwise prompts user to login
@app.route('/')
def home():
    if user:
        return redirect('/success')
    else:
        return redirect('/login') 

# Success page simply welcomes user
@app.route('/success')
def welcome():
    return render_template('welcome.html', phone_number=user.phone_number, user=user.username)

# Login page for users that checks against user database
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User(request.form['username'], request.form['password'])
        if user not in users:
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect('/success')
    return render_template('login.html', error=error)

# Signup page for users that initiates a 2FA for given phone number and redirects to verify page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        global new_user
        new_user = User(request.form['username'], request.form['password'], request.form['phone_number'])
        # TODO: Implement Telnyx 2FA create using given phone number
        # telnyx.2FA.create(
        #     phone_number = request.form['phone_number'],
        #     twofa_profile_id = '2FA PROFILE ID',
        #     type_ = "sms",
        #     timeout_secs = 300
        # )
        return redirect('/verify')
    else:
        return render_template('signup.html')

# Verify page attempts to verify based on input code and redirects to success
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    error = None
    if request.method == 'POST':
        code_try = request.form['code']
        # TODO: Implement Telnyx 2FA validate using the given code and phone number
        # response = telnyx.2FA.submit(
        #     phone_number = new_user.phone_number,
        #     code = code_try
        # )

        # TODO: Check if response is successful validation of the phone number and code
        if response:
            global user
            user = new_user
            users.append(new_user)
            return redirect('/success')
        else:
            error = 'Incorrect Code. Please try again.'
    return render_template('verify.html', user=new_user.username, error=error)

# Main program execution
def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()