from aiohttp import web
from call_center.infrastructure.server.http.slack_messages.slack_messages import (
    outbound_call_started,
    outbound_answered_call,
    outbound_finished_call,
)


class OutboundCall:
    def __init__(self):
        self.outbound_cached_data = {"outbound_ongoing_calls": 0, "outbound_calls": []}

    async def event_handler(self, request) -> web.json_response:

        data = await request.json()
        connections = request.config_dict["connection_data"]
        event_type = ""
        try:
            event_type = data["event_type"]
        except KeyError:
            pass

        if event_type == "call_initiated":
            payload = data["payload"]

            if payload["direction"] == "outgoing":
                self.outbound_cached_data["outbound_ongoing_calls"] += 1
                # connection = connections[str(payload["connection_id"])]

                to = payload["to"]
                # body = outbound_call_started(connection, to)
                # await request.config_dict["slack_client"].slack_post(body)
                time = data["created_at"]
                # print(connection, to, time)
                # Do things with above data

        elif event_type == "call_answered":
            payload = data["payload"]
            # connection = connections[str(payload["connection_id"])]
            to = payload["to"]
            # body = outbound_answered_call(connection, to)
            # await request.config_dict["slack_client"].slack_post(body)

        elif event_type == "call_hangup":
            payload = data["payload"]
            if (
                payload["hangup_cause"] == "originator_cancel"
                or payload["hangup_cause"] == "normal_clearing"
            ):
                self.outbound_cached_data["outbound_ongoing_calls"] -= 1
                # connection = connections[str(payload["connection_id"])]
                connection = "SIAN TEST"
                to = payload["to"]
                session = payload["call_session_id"]
                start = payload["start_time"][:-1].split("T")[1].split(":")
                finish = payload["end_time"][:-1].split("T")[1].split(":")
                i = 0
                while i < len(start):
                    start[i] = float(start[i])
                    finish[i] = float(finish[i])
                    i += 1
                total = 0
                if start[0] < finish[0]:
                    diff = finish[0] - start[0]
                    diff = diff * 60 * 60
                    total += diff
                if start[1] < finish[1]:
                    diff = finish[1] - start[1]
                    diff = diff * 60
                    total += diff
                elif start[1] > finish[1]:
                    diff = finish[1] - start[1]
                    diff = diff * 60
                    total += diff
                if start[2] < finish[2]:
                    diff = finish[2] - start[2]
                    total += diff
                elif start[2] > finish[2]:
                    diff = finish[2] - start[2]
                    total += diff

                total = str(round(total))

                self.outbound_cached_data["outbound_calls"].append(
                    {
                        "from": payload["from"],
                        "to": payload["to"],
                        "duration": total,
                        "call_id": session,
                        "completed_time": payload["end_time"],
                    }
                )
                body = outbound_finished_call(connection, to, total, session)
                # await request.config_dict["slack_client"].slack_post(body)

        return web.json_response({"status": "OK"})

    async def release_cache(self):
        """
        Release outbound call data
        """
        return self.outbound_cached_data

    async def delete_outbound_data(self):
        """
        Remove cached for day and reset
        """
        self.outbound_cached_data = {"outbound_ongoing_calls": 0, "outbound_calls": []}