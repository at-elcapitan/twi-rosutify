from dataclasses import dataclass

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.text_decorations import markdown_decoration as md

from ..logger import logger
from ..event import event_bus
from ..db import get_session
from .bot import bot
from .filters import FetchedEntityCallback, Action

@dataclass
class SendingInformation:
    fetched_entity_id: int
    chat_id: int
    author: str
    link: str


@event_bus.subscribe("send_community")
@get_session
async def send_tweet_notification(info: SendingInformation) -> None:
    author = md.bold(md.quote(info.author))
    link = md.link("Open on X/Twitter", info.link)
    message = f"New tweet from {author}\n{link}"

    buttons = InlineKeyboardBuilder()
    buttons.button(
        text="Take",
        callback_data=FetchedEntityCallback(
            action=Action.TAKE, 
            entity_id=info.fetched_entity_id
        )
    )

    try:
        await bot.send_message(
            chat_id=info.chat_id,
            text=message,
            parse_mode="MarkdownV2",
            reply_markup=buttons.as_markup()
        )
    except Exception as e:
        logger.error(f"Failed to send message: {e}")