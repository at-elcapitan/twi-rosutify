from aiohttp import web
from ..tgclient import bot

async def healthcheck(request: web.Request) -> web.Response:
    try:
        await bot.get_me()
    except Exception as e:
        return web.json_response({"status": "error"}, status=500)

    return web.json_response({"status": "ok"})