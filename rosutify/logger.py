import os
import sys
import logging
from datetime import datetime

import colorama
from dotenv import load_dotenv

load_dotenv()

LOGLEVEL = os.environ.get('LOGLEVEL')

colorama.init(autoreset=True)

class ApplicationStatus:
    def __init__(self):
        self._ok = True

    def exception_handler(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        self._ok = False

        logger.critical(
            "Uncaught exception handled",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    async def async_exception_handler(self, context):
        self._ok = False

        logger.critical(
            f"Uncaught exception handled",
            exc_info=context.get("exception")
        )

    @property
    def ok(self) -> bool:
        return self._ok

    @ok.setter
    def ok(self, value: bool):
        self._ok = value


application_status = ApplicationStatus()


class LoggingHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            application_status.ok = False

        super().emit(record)
            

class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": colorama.Fore.CYAN,
        "INFO": colorama.Fore.GREEN,
        "WARNING": colorama.Fore.YELLOW,
        "ERROR": colorama.Fore.RED,
        "CRITICAL": colorama.Fore.MAGENTA,
    }

    LEVEL_NAMES = {
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "WARNING": "WARN",
        "ERROR": "ERROR",
        "CRITICAL": "CRIT",
    }

    def format(self, record):
        dt = datetime.fromtimestamp(record.created)

        timestamp = (
            f"{dt:%d-%m-%Y} "
            f"{dt:%H:%M:%S}."
            f"{int(record.msecs):03d}"
        )

        level = record.levelname
        color = self.COLORS.get(level, colorama.Fore.WHITE)

        pretty_level = self.LEVEL_NAMES.get(level, level)

        level_text = (
            f"{color}"
            f"{pretty_level}"
            f" [{record.name}]"
            f"{colorama.Style.RESET_ALL}"
        )

        message = record.getMessage()

        return f"{colorama.Fore.LIGHTBLACK_EX}{timestamp}{colorama.Style.RESET_ALL} "\
            f"{level_text} "\
            f"{message}"

output_handler = LoggingHandler(sys.stdout)
output_handler.setFormatter(ColoredFormatter())

root_logger = logging.getLogger()
root_logger.setLevel(
    getattr(logging, LOGLEVEL, logging.INFO)
)
root_logger.addHandler(output_handler)

logger = logging.getLogger("rosutify")