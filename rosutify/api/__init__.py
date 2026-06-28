from aiohttp import web

from .healthcheck import healthcheck

app = web.Application()
app.router.add_get("/healthcheck", healthcheck)

runner = web.AppRunner(app)

__all__ = [
    "runner"
]