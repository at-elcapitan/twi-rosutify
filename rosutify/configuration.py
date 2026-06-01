import os
from dataclasses import dataclass

from dotenv import load_dotenv

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

load_dotenv()

ENV_VARIABLES = [
    EnvVar(
        "TG_API_KEY",
        required=True
    ),
    EnvVar(
        "TW_USER",
        required=True
    ),
    EnvVar(
        "TW_PASS",
        required=True
    ),
    EnvVar(
        "DB_PATH",
        required=True
    ),
    EnvVar(
        "TW_USER_FETCH",
        required=True
    ),
    EnvVar(
        "CHAT_ID",
        required=True
    ),
]

try:
    configuration = ConfigurationEnv(ENV_VARIABLES)
except CriticalEnvVarLoadException as e:
    logger.critical(e)
    exit(-1)