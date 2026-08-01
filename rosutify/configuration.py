import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .logger import logger


@dataclass(frozen=True)
class EnvVar:
    name: str


class CriticalEnvVarLoadException(Exception):
    def __init__(self, name: str):
        super().__init__(
            f"Unable to load required env var {name}"
        )


class ConfigurationEnv:
    def __init__(self, variables: list[EnvVar]):
        self._env: dict[str, str] = {}
        self._load_vars(variables)

    def _load_vars(self, variables: list[EnvVar]):
        for var in variables:
            loaded = os.environ.get(var.name)

            if loaded is None:
                raise CriticalEnvVarLoadException(var.name)
            
            self._env[var.name] = loaded

            logger.debug(
                f"Env var {var.name} is loaded"
            )

    def __getitem__(self, key: str) -> str:
        return self._env[key]

load_dotenv()

ENV_VARIABLES = [
    EnvVar(
        "TG_API_KEY",
    ),
    EnvVar(
        "TW_USER",
    ),
    EnvVar(
        "TW_PASS",
    ),
    EnvVar(
        "DB_PATH",
    ),
    EnvVar(
        "TW_USERS_FETCH",
    ),
    EnvVar(
        "CHAT_ID",
    ),
]

try:
    configuration = ConfigurationEnv(ENV_VARIABLES)
except CriticalEnvVarLoadException as e:
    logger.critical(e)
    exit(-1)