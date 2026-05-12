import asyncio

from .logger import logger
from .tgcient import dp, bot
from .event import event_bus
from . import utils

async def main():
    utils.print_info()
    logger.info("Starting up")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())