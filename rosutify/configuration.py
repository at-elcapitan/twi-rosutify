import os
from dataclasses import dataclass

from .logger import logger

@dataclass(frozen=True)
class EnvVar:
    name: str
    required: bool

class CriticalEnvVarLoadException(Exception):
    def __init__(self, name: str):
        super().__init__(
            f"Unable to load required env var {name}"
        )

class ConfigurationEnv:
    def __init__(self, variables: list[EnvVar]):
        self._env: dict[str, str | None] = {}
        self._load_vars(variables)

    def _load_vars(self, variables: list[EnvVar]):
        for var in variables:
            loaded = os.environ.get(var.name)

            if var.required and loaded is None:
                raise CriticalEnvVarLoadException(var.name)
            
            self._env[var.name] = loaded

            logger.debug(
                f"Env var {var.name} is None"
                if loaded is None else
                f"Env var {var.name} is loaded"
            )

    def __getitem__(self, key: str) -> str | None:
        return self._env[key]