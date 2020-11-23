import telnyx
from flask import Flask, render_template, redirect, request

# Setup
API_KEY = 'KEY017354F4D6F02070FFB17092CA4410C6_x0O6ITAWLkzt4Jptzh32L8'
TWOFA_KEY = '2FA_KEY'

app = Flask(__name__)
telnyx.api_key = API_KEY

# Storage Variables for Users
users = list()
new_user = list()
user = None

# Class to contain user information and describe equality
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
        # response = telnyx.2FA.submit(
        #     phone_number = new_user.phone_number,
        #     code = code_try
        # )
        response = True
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