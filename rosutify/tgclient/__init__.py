import aiogram

from ..configuration import configuration
from ..event import event_bus
from . import admin, twihandler, community, channel_notifier, channel_notifier_ctl
from .bot import bot

dp = aiogram.Dispatcher()
dp.include_router(admin.router)
dp.include_router(community.router)
dp.include_router(channel_notifier.router)

async def init(session):
    await channel_notifier_ctl.tg_notify_controller.load_controller(session)

__all__ = [
    "twihandler",
    "bot",
    "init"
]