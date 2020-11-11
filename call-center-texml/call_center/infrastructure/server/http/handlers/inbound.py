from aiohttp import web
from call_center.infrastructure.server.http.slack_messages.slack_messages import (
    incoming_call,
    inbound_answered_call,
    inbound_finished_call,
    inbound_missed_call,
)


class IncomingCall:
    def __init__(self):
        self.calls = {}

    async def statuscallback_handler(self, request) -> web.json_response:
        """
        Should handle any incoming webhook events:

        1. What sort of event is it
        2. Grab the ID of the call
        3. Cache the call in a state (did get answered or did not & how many times it has tried)
        4.

        """

        data = await request.post()

        try:
            sid = data["ParentCallSid"]

            if data["CallStatus"] == "initiated":
                try:
                    self.calls[sid]
                except KeyError:
                    self.calls[sid] = (False, 0)
                    body = incoming_call(data["From"])
                    await request.config_dict["slack_client"].slack_post(body)

            elif data["CallStatus"] == "in-progress":
                # Set the call to answered
                self.calls[sid] = (True, 1)
                to = data["To"]
                from_num = data["From"]
                body = inbound_answered_call(to, from_num)
                # Call in progress slack event
                await request.config_dict["slack_client"].slack_post(body)

            elif data["CallStatus"] == "completed":
                # Call Complete slack event
                duration = data["RecordingDuration"]
                if int(duration) > 0:
                    body = inbound_finished_call(
                        data["To"], data["From"], duration, sid
                    )

                    await request.config_dict["slack_client"].slack_post(body)

        except KeyError:
            pass

        return web.json_response({"status": "ok"})

    async def initiate_call_handler(self, request) -> web.FileResponse:
        """
        Return XML file that should dial Telnyx support line and redirect to
        below function.

        """

        return web.FileResponse("call_center/infrastructure/TeXML/inbound.xml")

    async def call_complete_handler(self, request) -> web.FileResponse:
        """
        Handle where call goes next based on if it completed or not.

        1. Grab ID
        2. Check state of call
        3.
            - If it has completed: return answered XML
            - If it did not complete: Check how many times it attempted to call.
            - If once: Try again -> busy.xml
            - If twice: Go to voicemail -> voicemail.xml

        """

        req = await request.post()
        sid = req["CallSid"]
        call = self.calls[sid]

        if not call[0]:
            if call[1] == 0:
                self.calls[sid] = (False, 1)
                return web.FileResponse("call_center/infrastructure/TeXML/busy.xml")
            else:
                self.calls.pop(sid)

                # Missed call slack event (Need to add voicemail url)
                body = inbound_missed_call(req["From"])
                await request.config_dict["slack_client"].slack_post(body)
                return web.FileResponse(
                    "call_center/infrastructure/TeXML/voicemail.xml"
                )
        else:
            self.calls.pop(sid)
            return web.FileResponse("call_center/infrastructure/TeXML/answered.xml")
