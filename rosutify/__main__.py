import asyncio

from .logger import logger
from .tgcient import bot
from .event import event_bus
from . import utils

async def main():
    utils.print_info()
    logger.info("Starting up")
    await event_bus.emit("test")

    while True:
        pass

if __name__ == "__main__":
    asyncio.run(main())