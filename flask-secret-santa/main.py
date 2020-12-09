import telnyx
import os
import random
import phonenumbers
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, make_response

# Run flask app and set telnyx API Key
app = Flask(__name__)

# Homepage redirects to user welcome if someone logged in, otherwise prompts user to login


@app.route('/')
def home():
    return render_template("index.html")

# Submit route to receive the participants list


@app.route('/submit', methods=['POST'])
def submit_participants():
    assignments = {}
    formatted_assignments = []
    # IF a post request comes through, check if user exists with given attributes
    if request.method == 'POST':

        names = request.form.getlist('name')
        numbers = request.form.getlist('number')

        participants = []

        for index, name in enumerate(names):
            participants.append({
                'name': name,
                'phone': ''.join(i for i in numbers[index] if i.isdigit())
            })
        
        assignments = create_assignments(participants)

        for key, value in assignments.items():
            send_santa(value['name'], assignments[value['target']]['name'], value['phone'])
            formatted_assignments.append([value['name'], assignments[value['target']]['name']])

    return render_template("success.html", assignments=formatted_assignments)

# Submit route to receive the participants list


@app.route('/test', methods=['POST'])
def test():
    print(request.form, flush=True)

    return {}, 200

# Assigns each person a santa, people cannot get each other or themselves


def create_assignments(participants):

    assignments = dict()

    # Enter each person and empty target to the dictionary
    for index, participant in enumerate(participants):

        number = phonenumbers.format_number(phonenumbers.parse(
            participant['phone'], 'US'), phonenumbers.PhoneNumberFormat.E164)

        assignments[index] = {
            'name': participant['name'],
            'phone': number,
            'target': ''
        }

    # Initiate queue of participants
    queue = list(range(1, len(participants)))

    # Start with the first participant
    curr = 0

    # While we have people left to assign
    while queue:

        # Choose random target from remaining
        new_target = queue.pop(random.randint(0, len(queue)-1))

        # Assign them to current person
        assignments[curr]['target'] = new_target

        # Make target new current participant
        curr = new_target

    # Catch the last user and assign them the first person
    assignments[curr]['target'] = 0

    # Test values output
    for value in assignments.values():
        name = value.get('name')
        number = value.get('phone')
        target = assignments[value['target']]['name']
        print(f'{name}({number}) -> {target}', flush=True)

    return assignments

# Initiate Telnyx call to show participant sending


def send_santa(name, target, number):
    telnyx_response = telnyx.Message.create(
        from_=os.getenv("TELNYX_NUMBER"),
        to=number,
        text=f'Hey, {name}! Your secret santa target is {target}. Have fun and happy holidays from Telnyx!'
    )
    return telnyx_response


# Main program execution
if __name__ == "__main__":
    load_dotenv()
    telnyx.api_key = os.getenv("TELNYX_API_KEY")
    port = os.getenv("APP_PORT")
    app.run(debug=True, port=port)
