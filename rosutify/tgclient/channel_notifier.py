from email.mime import message

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types, F, Router
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiogram
from aiogram.utils.text_decorations import markdown_decoration as md

from .message_sender import SendingInformation
from ..db import get_session, notify_entity as notify_entity_db, user as user_db
from .filters import TGFetchedEntityCallback, Action
from ..logger import logger
from .channel_notifier_ctl import tg_notify_controller
from .bot import bot

router = Router()


@router.message()
@get_session
async def handle_message(message: types.Message, session: AsyncSession):
    chat_ids = tg_notify_controller.get_chat_ids()

    if not message.chat.id in chat_ids:
        logger.debug(
            "Received message from chat_id=%d, but no notify entities are found",
            message.chat.id
        )
        return

    notify_entity_ids = tg_notify_controller.get_notify_entity_ids(message.chat.id)

    if not message.from_user.id in notify_entity_ids:
        logger.debug(
            "Received message from chat_id=%d, but no notify entity is found for tg_id=%d",
            message.chat.id,
            message.from_user.id
        )
        return

    notify_entity = tg_notify_controller.get_notify_entity(
        chat_id=message.chat.id,
        tg_id=message.from_user.id
    )

    if notify_entity is None:
        logger.warning(
            "Notify entity not found for chat_id=%d, tg_id=%d",
            message.chat.id,
            message.from_user.id
        )

        return

    notify_message = await notify_entity_db.create_tg_message(
        session=session,
        tg_message_id=message.message_id,
        text=message.text,
        community_id=notify_entity.community_id,
        tg_notify_entity_id=notify_entity.id
    )

    buttons = InlineKeyboardBuilder()
    buttons.button(
        text="Take",
        callback_data=TGFetchedEntityCallback(
            action=Action.TAKE,
            entity_id=notify_message.id
        )
    )

    await bot.send_message(
        chat_id=message.chat.id,
        text="Message registered",
        parse_mode="HTML",
        reply_markup=buttons.as_markup()
    )