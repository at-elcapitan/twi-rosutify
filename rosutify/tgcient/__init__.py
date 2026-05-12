import aiogram

from ..configuration import configuration
from ..event import event_bus
from . import twihandler

bot = aiogram.Bot(token=configuration["TG_API_KEY"])
dp = aiogram.Dispatcher()

@dp.message(aiogram.filters.Command("ping"))
async def ping(message: aiogram.types.Message):
    await message.reply("pong")
    await event_bus.emit("test")

__all__ = [
    "twihandler"
]