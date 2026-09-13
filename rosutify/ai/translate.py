import os

from google import genai
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types.message import Message

from .gemini import get_gemini_async_client
from ..db import get_session, fetched_entity
from ..logger import logger
from ..event import event_bus

LANGUAGE = os.environ.get("TRANSLATION_LANG", "english")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")

@event_bus.subscribe("translate_message")
@get_session
@get_gemini_async_client
async def translate_and_edit(
    text: str,
    tg_message: Message,
    tg_message_text: str,
    fetched_entity_id: int,
    session: AsyncSession,
    gemini_client: genai.client.AsyncClient
):
    chat = gemini_client.chats.create(
        model=GEMINI_MODEL
    )
    
    model_response = await chat.send_message(
        message=f"Translate text to {LANGUAGE}. Respond only with translation. \"{text}\""
    )
    translated_text = model_response.text

    logger.info(f"Translated text for {tg_message.message_id}")

    await fetched_entity.set_translation_for_entity(
        session=session,
        fetched_entity_id=fetched_entity_id,
        translated_text=translated_text
    )

    final_text = f"{tg_message_text}\n\n```Translation\n{translated_text}```"

    await tg_message.edit_text(
        text=final_text,
        parse_mode="MarkdownV2",
        reply_markup=tg_message.reply_markup
    )