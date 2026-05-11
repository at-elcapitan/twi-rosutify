import asyncio
import logging
from collections import defaultdict
from collections.abc import Callable, Awaitable
from typing import Any

Handler = Callable[..., Awaitable[Any]]

class Bus:
    def __init__(self, logger: logging.Logger) -> None:
        self._handlers = defaultdict(list[Handler])
        self._logger = logger

    def emit(self, signal_name: str, *args, **kwargs) -> None:
        for handler in self._handlers.get(signal_name, []):
            self._logger.debug(
                "emit signal=%s handler=%s",
                signal_name,
                getattr(handler, "__qualname__", handler.__name__)
            )

            asyncio.create_task(handler(*args, **kwargs))

    def subscribe(self, signal_name: str):
        def dec(method: Handler) -> Handler:
            self._handlers[signal_name].append(method)
            return method
        return dec