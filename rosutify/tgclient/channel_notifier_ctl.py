from dataclasses import dataclass

from ..db import notify_entity as notify_entity_db
from ..db.scheme import TelegramNotifyEntity
from ..logger import logger

class TGNotifyController:
    def __init__(self):
        self._notify_entities: dict[
            int, 
            dict[int, TelegramNotifyEntity]
        ] = {}

    async def load_controller(self, session):
        notify_entities = await notify_entity_db.get_telegram_notify_entities(session)

        for entity in notify_entities:
            if entity.tg_channel_id not in self._notify_entities.keys():
                self._notify_entities[entity.tg_channel_id] = {}

            self._notify_entities[entity.tg_channel_id][entity.tg_id] = entity

        logger.debug(
            "Loaded %d Telegram notify entities",
            len(self._notify_entities)
        )

    def get_chat_ids(self) -> list[int]:
        return list(self._notify_entities.keys())

    def get_notify_entity_ids(self, chat_id: int) -> list[int]:
        if chat_id not in self._notify_entities.keys():
            return []

        return list(self._notify_entities[chat_id].keys())

    def get_notify_entity(self, chat_id: int, tg_id: int) -> TelegramNotifyEntity | None:
        if chat_id not in self._notify_entities.keys():
            return None

        if tg_id not in self._notify_entities[chat_id].keys():
            return None

        return self._notify_entities[chat_id][tg_id]


tg_notify_controller = TGNotifyController()