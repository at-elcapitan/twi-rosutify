from aiogram import types, F, Router
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from .bot import bot
from ..db import get_session, user as user_db, community as community_db
from ..logger import logger

router = Router()


class WaitingForwardedMessage(StatesGroup):
    waiting = State()


class NotifyAllCommunitiesState(StatesGroup):
    waiting = State()


@router.message(CommandStart())
@get_session
async def check_initialized(message: types.Message, session: AsyncSession):
    is_initialized = await user_db.check_admin_inited(session)

    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Account", callback_data="b:account")
    builder.button(text="👥 Communities", callback_data="b:communities")
    builder.button(text="⚙️ Settings", callback_data="b:settings")

    if not is_initialized:
        await message.reply("Setting up admin user...")

        await user_db.create_user(session, user_id=message.from_user.id, is_superuser=True)

        builder.adjust(2)
        builder.button(text="⚙️ Management", callback_data="b:management")

        await message.reply(
            "Superuser created. Use /admin for managing the bot or buttons below.",
            reply_markup=builder.as_markup()
        )
        return
    
    user = await user_db.get_user_by_id(session, message.from_user.id)

    if user is None:
        await message.reply("Initializing account, please wait...")

        await user_db.create_user(session, user_id=message.from_user.id)

        await message.reply(
            "Account initialized. Сontact community admins for adding you to communities.",
            reply_markup=builder.as_markup()
        )
        return

    if user.is_superuser:
        builder.adjust(2)
        builder.button(text="⚙️ Management", callback_data="b:management")

    await message.reply(f"Welcome back, {message.from_user.full_name}!", reply_markup=builder.as_markup())


@router.message(Command("get_id"))
async def get_user_id(message: types.Message, state: FSMContext):
    await message.reply("Please forward the message")
    await state.set_state(WaitingForwardedMessage.waiting)


@router.message(StateFilter(WaitingForwardedMessage.waiting))
async def send_user_id(message: types.Message, state: FSMContext):
    if not message.forward_from:
        await message.reply("User ID could not be extracted")
        await state.clear()
        return

    await message.reply(f"User ID: {message.forward_from.id}")
    await state.clear()


@router.message(Command("chat_id"))
async def get_chat_id(message: types.Message):
    await message.reply(f"Chat ID: {message.chat.id}")


@router.message(Command("notify_all_communities"))
@get_session
async def notify_all_communities_with_message(message: types.Message, state: FSMContext, session: AsyncSession):
    if not await user_db.is_user_in_database(session, message.from_user.id):
        await message.reply("You are not registered in the system. Please, start the bot with /start command")
        return

    if not await user_db.check_user_admin(session, message.from_user.id):
        await message.reply("Access denied")
        return

    await message.reply("Please send the message to notify all communities")
    await state.set_state(NotifyAllCommunitiesState.waiting)


@router.message(StateFilter(NotifyAllCommunitiesState.waiting))
@get_session
async def send_notification(message: types.Message, state: FSMContext, session: AsyncSession):
    communities = await community_db.get_all_community_channel_ids(session)

    logger.info(f"Sending notification to {len(communities)} communities")

    for community_id in communities:
        try:
            await bot.send_message(
                chat_id=community_id,
                text=message.text,
                parse_mode="HTML"
            )
        except Exception as e:
            await message.reply(f"Failed to send message to community {community_id}: {e}")