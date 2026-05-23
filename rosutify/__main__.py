import asyncio

from .logger import logger
from .tgcient import dp, bot
from . import utils, db

async def main():
    logger.debug("Initializing database")
    await db.init_db()

    utils.print_info()
    logger.info("Service ready")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())