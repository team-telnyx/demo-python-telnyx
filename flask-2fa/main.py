import telnyx
import requests
import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, make_response

# Load environment
load_dotenv()

# External .py files for the project
import sql_utils
from user import User

# Remove this once Python SDK is working correctly
import telnyx_wrappers

# Run flask app and set telnyx API Key
app = Flask(__name__)
telnyx.api_key = os.getenv("API_KEY")

# Homepage redirects to user welcome if someone logged in, otherwise prompts user to login
@app.route('/')
def home():
    return redirect('/signup') 

# Success page simply welcomes user
@app.route('/success')
def welcome():
    return render_template('welcome.html', user=request.cookies.get('username'))

# Login page for users that checks against user database
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    # IF a post request comes through, check if user exists with given attributes
    if request.method == 'POST':
        user = User(request.form['username'], request.form['password'])
        user_exists = sql_utils.LoginUser(user)

        # Set current user if they logged in correctly
        if user_exists:
            resp = make_response(redirect('/success'))
            resp.set_cookie('username', user.username)

            return resp
        else:
            error = "User does not exist or incorrect password."

    # Default page for GET request
    return render_template('login.html', error=error)

# Signup page for users that initiates a 2FA for given phone number and redirects to verify page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None

    # If a post requests comes through, initiate new user
    if request.method == 'POST':

        # Create new user object
        current_user = User(request.form['username'], request.form['password'], request.form['phone_number'])
        
        # Initiate the verification
        r = telnyx_wrappers.CreateVerification(current_user.phone_number)

        # If username available insert the user, otherwise throw an error
        if sql_utils.CheckUsername(current_user):
            user_created = sql_utils.InsertUser(current_user)
        else:
            error = f'Username {current_user.username} already in use, please try another'
            return render_template('signup.html', error=error)
        
        # If the verify request and insert call went through, continue
        if r.status_code == 200:
            if user_created:
                resp = make_response(redirect('/verify'))
                resp.set_cookie('username', current_user.username)
                resp.set_cookie('phone', current_user.phone_number)
                return resp
            else:
                error = 'Failed to insert new user to database!'
                return render_template('signup.html', error=error)
        else:
            error = f'Request to initiate verification failed: {r.status_code} status'
    
    # Default for GET request to show page
    return render_template('signup.html', error=error)

# Verify page attempts to verify based on input code and redirects to success
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    error = None

    # If a post request comes through, initiate verification check
    if request.method == 'POST':

        # Retrieve code and submit it to Telnyx
        code_try = request.form['code']
        r = telnyx_wrappers.SubmitVerificationCode(code_try, request.cookies.get('phone'))
        
        # If the code is accepted, verify the user in the database
        if r.status_code == 200 and r.json().get('data').get("response_code") == "accepted":
            user_verified = sql_utils.VerifyUser(request.cookies.get('username'))
            if user_verified:
                resp = make_response(redirect('/success'))
                resp.set_cookie('username', request.cookies.get('username'))
                return resp
            else:
                error = 'Failed to update database with verified user.'
                return render_template('verify.html', user=request.cookies.get('username'), error=error)
        else:
            error = 'Incorrect Code. Please try again.'
    
    # Default for GET request to show page
    return render_template('verify.html', user=request.cookies.get('username'), error=error)
        

# Main program execution
def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()