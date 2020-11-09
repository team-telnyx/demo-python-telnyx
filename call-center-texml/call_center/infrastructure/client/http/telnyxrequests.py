

class TelnyxAccountClient:

    def __init__(self, session, api_key):
        self.session = session
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + api_key
        }

    async def get_connections(self):
        url = "https://api.telnyx.com/v2/credential_connections"
        async with self.session.get(headers=self.headers, url=url) as response:
            if response.status == 200:
                r_json = await response.json()
                return r_json
            else:
                print(response)

    async def get_balance(self):
        url = "https://api.telnyx.com/v2/balance"
        async with self.session.get(headers=self.headers, url=url) as response:
            if response.status == 200:
                r_json = await response.json()
                return r_json
            else:
                print(response)

