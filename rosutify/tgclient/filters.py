from aiogram.filters.callback_data import CallbackData
from enum import StrEnum

class Action(StrEnum):
    FETCH = "f"
    TAKE = "t"

class FetchedEntityCallback(CallbackData, prefix="FE"):
    action: Action
    entity_id: int