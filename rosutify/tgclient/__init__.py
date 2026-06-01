import aiogram

from ..configuration import configuration
from ..event import event_bus
from . import admin, twihandler, community
from .bot import bot

dp = aiogram.Dispatcher()
dp.include_router(admin.router)
dp.include_router(community.router)


__all__ = [
    "twihandler",
    "bot"
]