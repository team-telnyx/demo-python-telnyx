"""
Setup functions for HTTP server.
"""
from aiohttp import web
from call_center.infrastructure.server.http.handlers import audio


HEALTH = "/health"
STATUSCALLBACK = "/TeXML/events"
TEXMLINBOUND = "/TeXML/inbound"
TEXMLCOMPLETED = "/TeXML/completed"
OUTBOUNDEVENT = "/outbound/event"


def _setup_routes(app):

    incoming_call = app["incoming_call"]
    outbound_call = app["outbound_call"]

    app.add_routes(
        [
            web.post(STATUSCALLBACK, incoming_call.statuscallback_handler),
            web.get(TEXMLINBOUND, incoming_call.initiate_call_handler),
            web.post(TEXMLCOMPLETED, incoming_call.call_complete_handler),
        ]
    )

    app.add_routes(
        [
            web.post(OUTBOUNDEVENT, outbound_call.event_handler),
        ]
    )

    # Add get routes for audio files
    app.router.add_get("/TeXML/support_greeting", audio.hello_handler)
    app.router.add_get("/TeXML/support_busy", audio.busy_handler)
    app.router.add_get("/TeXML/support_voicemail", audio.voicemail_handler)
    app.router.add_get("/TeXML/music", audio.music_handler)
    app.router.add_get("/TeXML/ringback", audio.rinback_handler)


def configure_app(app):
    """Configure the web.Application."""

    _setup_routes(app)
