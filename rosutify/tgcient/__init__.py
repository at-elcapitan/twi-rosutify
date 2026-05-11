import aiogram

from ..configuration import configuration
from . import handlers

bot = aiogram.Bot(configuration["TG_API_KEY"])

__all__ = [
    "handlers"
]