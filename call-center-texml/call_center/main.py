import sys
import os
import argparse
import asyncio
import signal
import aiohttp
from aiohttp import web
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from call_center.infrastructure.server import http
from call_center.infrastructure.client.http.telnyxrequests import TelnyxAccountClient
from call_center.infrastructure.client.http.slackrequests import SlackClient
from call_center.infrastructure.scheduled_jobs.connection_data import get_connections
from call_center.infrastructure.server.http.handlers.inbound import IncomingCall
from call_center.infrastructure.server.http.handlers.outbound import OutboundCall
from call_center.infrastructure.scheduled_jobs.balance_status import balance_check


async def startup_handler(app):
    # Load .env variables, override os env variables
    load_dotenv(override=True)

    # Client Session for app, save to app
    app["PERSISSTENT_SESSION"] = aiohttp.ClientSession()

    # Replace the with connections api
    app["telnyx_client"] = TelnyxAccountClient(
        app["PERSISSTENT_SESSION"],
        os.getenv("API_KEY")
    )

    app["slack_client"] = SlackClient(
        app["PERSISSTENT_SESSION"],
        os.getenv("SLACK_URL"),
    )

    app["ngrok_url"] = os.getenv("NGROK_URL")

    app["outbound_id"] = os.getenv("OUTBOUND_PROFILE_ID")

    # Call on connection data on startup
    await get_connections(app)
    await balance_check(app)

    # Define required cleanup
    async def cleanup(app):  # pylint: disable=unused-argument
        """Perform required cleanup on shutdown"""
        await app["PERSISSTENT_SESSION"].close()

    app.on_shutdown.append(cleanup)


def main():
    app = web.Application()
    app["incoming_call"] = IncomingCall()
    app["outbound_call"] = OutboundCall()

    http.configure_app(app)
    app.on_startup.append(startup_handler)
    # Start the HTTP server.
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, loop.stop)
    scheduler = AsyncIOScheduler({"apscheduler.timezone": "UTC"}, daemon=True)

    scheduler.add_job(get_connections, "interval", [app], hours=3)

    scheduler.add_job(balance_check, "interval", [app], days=1)

    if os.getenv("PROD") == "True":
        scheduler.start()

    web.run_app(app)


if __name__ == "__main__":
    sys.exit(main())