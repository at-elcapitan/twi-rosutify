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
from ..logger import logger

router = Router()

@router.message()
async def handle_message(message: types.Message):
    pass