from call_center.infrastructure.server.http.slack_messages.slack_messages import (
    low_balance,
)


async def balance_check(app):
    balance_details = await app["telnyx_client"].get_balance()
    avail_credit = balance_details["data"]["available_credit"]
    if float(avail_credit) < 80.00:
        body = low_balance(avail_credit)
        await app["slack_client"].slack_post(body)