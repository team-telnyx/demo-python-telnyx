def answer_texml(gather_url):
    return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Welcome to the Conference Demo!</Say>
    <Gather action="{0}" timeout="20" numDigits="2">
        <Say voice="alice">Please enter the two digit conference ID.</Say>
    </Gather>
    <Say voice="alice">Sorry I didn't get that, please call back and try again</Say>
    <Hangup/>
</Response>""".format(gather_url)


def join_conference_texml(conference_id):
    return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Thank you, connecting you to conference <say-as interpret-as="digits">{0}</say-as></Say>
    <Dial>
        <Conference>{0}</Conference>
    </Dial>
</Response>""".format(conference_id)
