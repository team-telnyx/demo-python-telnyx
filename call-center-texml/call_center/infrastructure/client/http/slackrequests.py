"""
Requests for pushing events to Slack

"""


class SlackClient:

    headers = {"Content-Type": "application/json"}

    def __init__(self, session, url):
        self.session = session
        self.url = url

    async def slack_post(self, body):
        async with self.session.post(
            headers=self.headers, url=self.url, data=body
        ) as response:
            if response.status == 200:
                return
            else:
                print(response)