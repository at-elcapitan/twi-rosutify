import os
import sys
import logging
from datetime import datetime

import colorama
from dotenv import load_dotenv

load_dotenv()

LOGLEVEL = os.environ.get('LOGLEVEL')

colorama.init(autoreset=True)
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
            f"{colorama.Style.RESET_ALL}"
        )

        message = record.getMessage()

        return f"{colorama.Fore.LIGHTBLACK_EX}{timestamp}{colorama.Style.RESET_ALL} "\
            f"{level_text} "\
            f"{message}"

output_handler = logging.StreamHandler(sys.stdout)
output_handler.setFormatter(ColoredFormatter())

logger = logging.getLogger("rosutify")
logger.setLevel(
    getattr(logging, LOGLEVEL, logging.INFO)
)
logger.addHandler(output_handler)

aiogram_logger = logging.getLogger("aiogram")
aiogram_logger.setLevel(
    getattr(logging, LOGLEVEL, logging.INFO)
)
aiogram_logger.addHandler(output_handler)

aiogram_event_logger = logging.getLogger("aiogram.event")
aiogram_event_logger.setLevel(
    getattr(logging, LOGLEVEL, logging.INFO)
)
aiogram_event_logger.addHandler(output_handler)