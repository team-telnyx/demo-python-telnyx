from aiohttp import web


async def health_check(request):
    """Health check handler."""
    return web.json_response({"status": "OK"})