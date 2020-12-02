import telnyx
import requests
from flask import Flask, render_template, redirect, request

# External .py files for the project
import config
import sql_utils
from user import User

# Remove this once Python SDK is working correctly
import telnyx_wrappers

# Run flask app and set telnyx API Key
app = Flask(__name__)
telnyx.api_key = config.API_KEY

# Local storage variable for current user
current_user = None

# Homepage redirects to user welcome if someone logged in, otherwise prompts user to login
@app.route('/')
def home():
    if current_user:
        return redirect('/success')
    else:
        return redirect('/signup') 

# Success page simply welcomes user
@app.route('/success')
def welcome():
    return render_template('welcome.html', phone_number=current_user.phone_number, user=current_user.username)

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
    error = None
    if request.method == 'POST':
        global current_user
        current_user = User(request.form['username'], request.form['password'], request.form['phone_number'])
        r = telnyx_wrappers.CreateVerification(current_user.phone_number)
        user_created = sql_utils.InsertUser(current_user)
        if r.status_code == 200:
            if user_created:
                return redirect('/verify')
            else:
                error = 'Failed to insert new user to database!'
                return render_template('signup.html', error=error)
        else:
            error = f'Request to initiate verification failed: {r.status_code} status'
            return render_template('signup.html', error=error)
    return render_template('signup.html')

# Verify page attempts to verify based on input code and redirects to success
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    error = None
    if request.method == 'POST':
        code_try = request.form['code']
        r = telnyx_wrappers.SubmitVerificationCode(code_try, current_user.phone_number)
        if r.status_code == 200 and r.json().get('data').get("response_code") == "accepted":
            user_verified = sql_utils.VerifyUser(current_user)
            if user_verified:
                return redirect('/success')
            else:
                error = 'Failed to update database with verified user.'
                return render_template('verify.html', user=current_user.username, error=error)
        else:
            error = 'Incorrect Code. Please try again.'
    return render_template('verify.html', user=current_user.username, error=error)
        

# Main program execution
def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()