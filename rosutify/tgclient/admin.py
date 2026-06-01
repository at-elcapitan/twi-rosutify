from aiogram import types, F, Router
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session, user as user_db

router = Router()

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