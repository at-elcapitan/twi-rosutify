from dataclasses import dataclass

import aiogram
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types, F, Router
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.text_decorations import markdown_decoration as md

from ..db import notify_entity as notify_entity_db, fetched_entity as fetched_entity_db
from ..twclient.fetch_account import TwiAccountTweets
from ..logger import logger
from ..event import event_bus
from ..db import get_session
from .bot import bot
from .message_sender import SendingInformation


@event_bus.subscribe("new_tweets")
@get_session
async def on_new_tweets(account_tweets: TwiAccountTweets, session: AsyncSession):
    logger.info(
        "New tweets for user=%s count=%d",
        account_tweets.username,
        len(account_tweets.tweets)
    )

    communities = await notify_entity_db.get_communities_for_notify_entity(
        session=session,
        notify_entity_id=account_tweets.internal_id
    )

    for tweet in account_tweets.tweets:
        short_text = f"{tweet.text[:280]}{'...' if len(tweet.text) > 280 else ''}"
        
        for community in communities:
            fetched_entity = await fetched_entity_db.create_fetched_entity(
                session=session,
                text=tweet.text,
                community_id=community.id,
                notify_entity_id=account_tweets.internal_id,
                twi_id=int(tweet.id)
            )

            await event_bus.emit(
                "send_community",
                SendingInformation(
                    chat_id=community.connected_channel,
                    author=account_tweets.username,
                    link=f"https://twitter.com/{account_tweets.username}/status/{tweet.id}",
                    fetched_entity_id=fetched_entity.id
                )
            )