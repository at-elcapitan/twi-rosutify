from dataclasses import dataclass

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.text_decorations import markdown_decoration as md

from ..logger import logger
from ..event import event_bus
from ..db import get_session
from .bot import bot
from .filters import FetchedEntityCallback, Action
from ..ai.translate import translate_and_edit

@dataclass
class SendingInformation:
    fetched_entity_id: int
    chat_id: int
    author: str
    link: str


@event_bus.subscribe("send_community")
async def send_tweet_notification(
    info: SendingInformation,
    original_message_text: str
) -> None:
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
        sended_message = await bot.send_message(
            chat_id=info.chat_id,
            text=message,
            parse_mode="MarkdownV2",
            reply_markup=buttons.as_markup()
        )
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

    await event_bus.emit(
        "translate_message",
        text=original_message_text,
        tg_message=sended_message,
        tg_message_text=message,
        fetched_entity_id=info.fetched_entity_id
    )