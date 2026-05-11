import aiogram

from ..logger import logger
from ..event import event_bus

@event_bus.subscribe("test")
async def test_event():
    logger.debug("event test")