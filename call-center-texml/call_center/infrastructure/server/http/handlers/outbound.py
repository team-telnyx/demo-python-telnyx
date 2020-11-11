from aiohttp import web
from datetime import datetime
from call_center.infrastructure.server.http.slack_messages.slack_messages import (
    outbound_call_started,
    outbound_answered_call,
    outbound_finished_call,
)


class OutboundCall:
    def __init__(self):
        pass

    async def event_handler(self, request) -> web.json_response:

        data = await request.json()
        connections = request.config_dict["connections"]
        event_type = ""
        try:
            event_type = data["event_type"]
        except KeyError:
            pass

        if event_type == "call_initiated":
            payload = data["payload"]

            if payload["direction"] == "outgoing":
                connection = connections[str(payload["connection_id"])]

                to = payload["to"]
                body = outbound_call_started(connection, to)
                await request.config_dict["slack_client"].slack_post(body)

        elif event_type == "call_answered":
            payload = data["payload"]
            connection = connections[str(payload["connection_id"])]
            to = payload["to"]
            body = outbound_answered_call(connection, to)
            await request.config_dict["slack_client"].slack_post(body)

        elif event_type == "call_hangup":
            payload = data["payload"]
            if (
                payload["hangup_cause"] == "originator_cancel"
                or payload["hangup_cause"] == "normal_clearing"
            ):
                connection = connections[str(payload["connection_id"])]
                to = payload["to"]
                session = payload["call_session_id"]
                start = payload["start_time"][:-1].split("T")[1].split(".")[0]
                finish = payload["end_time"][:-1].split("T")[1].split(".")[0]
                FMT = "%H:%M:%S"
                datetime_start = datetime.strptime(start, FMT)
                datetime_finish = datetime.strptime(finish, FMT)
                diff = datetime_finish - datetime_start
                secs = str(diff.seconds)

                body = outbound_finished_call(connection, to, secs, session)
                await request.config_dict["slack_client"].slack_post(body)

        return web.json_response({"status": "OK"})