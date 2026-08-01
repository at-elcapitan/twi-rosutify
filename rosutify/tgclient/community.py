from email.mime import message

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types, F, Router
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .message_sender import SendingInformation
from ..db import get_session, fetched_entity as fetched_entity_db, notify_entity as notify_entity_db, user as user_db
from .filters import FetchedEntityCallback, Action, TGFetchedEntityCallback

router = Router()

@router.callback_query(FetchedEntityCallback.filter(F.action == Action.TAKE))
@get_session
async def show_tasks(callback: CallbackQuery, callback_data: FetchedEntityCallback, session: AsyncSession):
    if not await user_db.is_user_in_database(session, callback.from_user.id):
        await callback.answer("You are not registered in the system. Please, start the bot with /start command", show_alert=True)
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


@router.callback_query(TGFetchedEntityCallback.filter(F.action == Action.TAKE))
@get_session
async def handle_tg_fetched_entity_callback(callback: CallbackQuery, callback_data: TGFetchedEntityCallback, session: AsyncSession):
    if not await user_db.is_user_in_database(session, callback.from_user.id):
        await callback.answer("You are not registered in the system. Please, start the bot with /start command", show_alert=True)
        return

    entity_id = callback_data.entity_id

    await notify_entity_db.set_tg_message_picked(
        session=session,
        tg_message_id=entity_id,
        picked_by_user_id=callback.from_user.id
    )

    await callback.answer("Taken!")

    await callback.message.edit_text(
        text=f"Upper message was taken by [{callback.from_user.full_name}](tg://user?id={callback.from_user.id})",
        parse_mode="MarkdownV2"
    )