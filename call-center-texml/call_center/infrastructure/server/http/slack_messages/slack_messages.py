def header_section(event) -> dict:
    """Main header"""
    return {"type": "section", "text": {"type": "mrkdwn", "text": f">*{event}*"}}


def body_section(text) -> dict:
    """
    Body of the message
    """

    return {"type": "section", "text": {"type": "mrkdwn", "text": f"{text}"}}


def menu_section(direction):

    # Add list of tags in slack menu below
    tags = [
        "Failed Calls",
        "Failed SMS"
    ]

    options = []
    for tag in tags:
        tmp = {"text": {"type": "plain_text", "text": tag}, "value": tag}
        options.append(tmp)

    return {
        "type": "section",
        "text": {"type": "mrkdwn", "text": "Please select a tag from the list"},
        "accessory": {
            "action_id": direction,
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Select a Tag"},
            "options": options,
        },
    }


def incoming_call(from_num) -> str:
    blocks = [
        header_section("Incoming Call Ringing"),
        body_section(str(from_num) + " is calling. Let's jump on that!"),
    ]

    return str(
        {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Call Center"},
            "blocks": blocks,
        }
    )


def inbound_missed_call(from_num) -> str:
    blocks = [
        header_section("Missed Call"),
        body_section(
            "Missed call from the number " + str(from_num) + ". Please call back asap!"
        ),
    ]

    return str(
        {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Call Center"},
            "blocks": blocks,
        }
    )


def inbound_answered_call(to_uri, from_num) -> str:
    blocks = [
        header_section("Incoming Call Answered"),
        body_section(
            str(
                to_uri.split("@")[0][4:]
                + " answered the call from "
                + str(from_num)
            )
        ),
    ]

    return str(
        {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Call Center"},
            "blocks": blocks,
        }
    )


def outbound_call_started(agent: str, number: str) -> str:
    blocks = [
        header_section("Outbound Call Ringing"),
        body_section(
            agent + " started a call to " + number + " and is ringing"
        ),
    ]

    return str(
        {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Call Center"},
            "blocks": blocks,
        }
    )


def outbound_answered_call(agent: str, number: str):

    blocks = [
        header_section("Outgoing Call Answered"),
        body_section(agent + " on call with " + number),
    ]

    return str(
        {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Call Center"},
            "blocks": blocks,
        }
    )


def outbound_finished_call(agent: str, number: str, duration: str, session: str):

    blocks = [
        header_section("Outgoing Call Finished"),
        body_section(agent + " finished call to " + number),
        {"type": "divider"},
        body_section("Duration: " + duration + " seconds."),
        {"type": "divider"},
        body_section("Call Session ID: " + session),
        {"type": "divider"},
        menu_section("outbound"),
    ]
    return str(
        {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Call Center"},
            "blocks": blocks,
        }
    )


def inbound_finished_call(to_uri: str, from_number: str, duration: str, sid: str) -> str:
    # Add tags interactive menu
    blocks = [
        header_section("Incoming Call Ended"),
        body_section(
           to_uri.split("@")[0][4:] + " finished call with " + from_number
        ),
        {"type": "divider"},
        body_section("Call Duration: " + str(duration) + " seconds."),
        {"type": "divider"},
        body_section("Call Control ID: " + sid),
        {"type": "divider"},
        menu_section("inbound"),
    ]

    return str(
        {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Call Center"},
            "blocks": blocks,
        }
    )


def low_balance(available_credit):
    blocks = [
        header_section("Low Balance on Call-Center Account"),
        body_section("Please Top Up Account"),
        {"type": "divider"},
        body_section("Available Credit: " + available_credit),
    ]

    return str(
        {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Call Center"},
            "blocks": blocks,
        }
    )