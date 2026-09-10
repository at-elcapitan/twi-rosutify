from email.mime import message

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types, F, Router
from aiogram.types import (
    CallbackQuery, 
    ReplyKeyboardMarkup,
    InputRichMessage
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .message_sender import SendingInformation
from ..db import (
    get_session, 
    fetched_entity as fetched_entity_db, 
    notify_entity as notify_entity_db, 
    user as user_db,
    community as community_db
)
from .filters import FetchedEntityCallback, Action, TGFetchedEntityCallback
from .bot import bot

router = Router()


@router.callback_query(TGFetchedEntityCallback.filter(F.action == Action.TAKE))
@get_session
async def handle_tg_fetched_entity_callback(callback: CallbackQuery, callback_data: TGFetchedEntityCallback, session: AsyncSession):
    if not await user_db.is_user_in_database(session, callback.from_user.id):
        await callback.answer("You are not registered in the system. Please, start the bot with /start command", show_alert=True)
        return

    entity_id = callback_data.entity_id

    if await fetched_entity_db.is_fetched_entity_picked(session, entity_id):
        await callback.answer("This message has already been taken by someone else.", show_alert=True)
        return

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


@router.message(Command("statistics"))
@get_session
async def show_community_message_statistics(message: types.Message, session: AsyncSession):
    if not await user_db.is_user_in_database(session, message.from_user.id):
        await message.reply("You are not registered in the system. Please, start the bot with /start command")
        return

    chat_id = message.chat.id

    if not await community_db.get_community_exists_by_channel_id(session, chat_id):
        await message.reply("This command can only be used in community chats")
        return

    stats = await fetched_entity_db.get_community_statistics(session, chat_id)
    total_taken = await fetched_entity_db.get_community_count_taken_messages(session, chat_id)
    total_untaken = await fetched_entity_db.get_community_count_untaken_messages(session, chat_id)

    md_text = f"**Community Statistics**\n\n"\
              f"| User | Taken Messages |\n"\
              f"|------|------|\n"

    for user_id, count in stats:
        user = await user_db.get_user_by_id(session, user_id)

        if user:
            md_text += f"| [{user.username}](tg://user?id={user_id}) | {count} |\n"
        else:
            md_text += f"| [Unknown User](tg://user?id={user_id}) | {count} |\n"

    md_text += f"**Total Taken Messages:** {total_taken}\n\n"
    md_text += f"**Total Untaken Messages:** {total_untaken}"

    rich_message = InputRichMessage(
        markdown=md_text
    )

    await message.reply_rich(rich_message)


""" @router.message(Command("get_untaken"))
@get_session
async def get_untaken_messages(message: types.Message, session: AsyncSession):
 """