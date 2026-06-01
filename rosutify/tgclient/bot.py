import aiogram

from ..configuration import configuration

bot = aiogram.Bot(token=configuration["TG_API_KEY"])