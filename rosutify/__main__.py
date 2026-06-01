from datetime import datetime, timedelta
import asyncio

from rosutify.twclient.fetch_account import TwiAccountLazy
from sqlalchemy.ext.asyncio import AsyncSession
from rosutify import logger

from .db import get_session, community as community_db, notify_entity as notify_entity_db
from .configuration import configuration
from .scheduler import scheduler
from .tgclient import dp, bot
from .twclient import client
from .logger import logger
from . import utils, db


@db.get_session
async def on_startup(session: AsyncSession):
    logger.debug("Initializing database")
    await db.init_db()

    logger.debug("Starting scheduler")
    scheduler.start()

    await client.load_client(
        username=configuration["TW_USER"],
        email=None,
        password=configuration["TW_PASS"],
        cookies_path="cookies.json"
    )

    await client.add_account(
        TwiAccountLazy(
            twi_username=configuration["TW_USER_FETCH"],
            twi_id=None
        )
    )

    # for 0.0.1 only - create initial community and notify entity if not exist
    if await community_db.get_community_by_channel_id(session, configuration["CHAT_ID"]) is None:
        community = await community_db.create_community(
            session=session,
            name="Initial community",
            connected_channel=configuration["CHAT_ID"],
        )

        notify_entity_id = await notify_entity_db.get_notify_entity_by_username(
            session=session,
            twi_username=configuration["TW_USER_FETCH"]
        )

        await community_db.add_notify_entity(
            session=session,
            community_id=community.id,
            notify_entity_id=notify_entity_id.id
        )

    logger.info("Twitter client ready")

    scheduler.add_job(client.load_tweets, "interval", minutes=5)
    scheduler.add_job(client.load_tweets, "date", run_date=datetime.now() + timedelta(seconds=10))
    logger.debug("Scheduled initial fetch job")

    logger.info("Scheduler ready")


async def on_shutdown():
    logger.info("Shutting down scheduler")
    scheduler.shutdown(wait=False)


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    utils.print_info()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())