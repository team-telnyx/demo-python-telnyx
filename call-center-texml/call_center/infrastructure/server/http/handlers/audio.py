from aiohttp import web


async def hello_handler(request: web.Request) -> web.FileResponse:
    """
    Return hello audio
    """
    return web.FileResponse("call_center/infrastructure/audio/greeting.mp3")


async def busy_handler(request: web.Request) -> web.FileResponse:
    """
    Return Busy audio

    """
    return web.FileResponse("call_center/infrastructure/audio/busy_try_again.mp3")


async def voicemail_handler(request: web.Request) -> web.FileResponse:
    """
    Return voicemail audio

    """
    return web.FileResponse("call_center/infrastructure/audio/voicemail.mp3")
