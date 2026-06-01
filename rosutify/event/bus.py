import asyncio
import inspect
import logging
from collections import defaultdict
from collections.abc import Callable, Awaitable
from typing import Any

Handler = Callable[..., Awaitable[Any]]

class Bus:
    def __init__(self, logger: logging.Logger) -> None:
        self._handlers = defaultdict(list[Handler])
        self._logger = logger

    async def emit(self, signal_name: str, *args, **kwargs) -> None:
        tasks: list[Awaitable[Any]] = []

        for handler in self._handlers.get(signal_name, []):
            res = handler(*args, **kwargs)

            if inspect.isawaitable(res):
                tasks.append(res)

        await asyncio.gather(*tasks)

    def subscribe(self, signal_name: str):
        def dec(method: Handler) -> Handler:
            self._handlers[signal_name].append(method)
            return method
        
        return dec