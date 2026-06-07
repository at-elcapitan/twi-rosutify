from email.mime import message

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types, F, Router
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .message_sender import SendingInformation
from ..db import get_session, fetched_entity as fetched_entity_db, user as user_db
from .filters import FetchedEntityCallback, Action

router = Router()

@router.callback_query(FetchedEntityCallback.filter(F.action == Action.TAKE))
@get_session
async def show_tasks(callback: CallbackQuery, callback_data: FetchedEntityCallback, session: AsyncSession):
    if not await user_db.is_user_in_database(session, callback.from_user.id):
        await callback.answer("You are not registered in the system. Please contact the administrator.", show_alert=True)
        return

    entity_id = callback_data.entity_id

    await fetched_entity_db.set_fetched_entity_picked(
        session=session,
        fetched_entity_id=entity_id,
        picked_by_user_id=callback.from_user.id
    )

    await callback.answer("Taken!")

    await callback.message.edit_text(
        text=f"*Taken by* [{callback.from_user.full_name}](tg://user?id={callback.from_user.id})\n\n{callback.message.md_text}",
        parse_mode="MarkdownV2"
    )


@router.message(Command("channel_id"))
async def get_channel_id(message: types.Message):
    await message.reply(f"Channel ID: {message.chat.id}")