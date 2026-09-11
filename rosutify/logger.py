import os
import sys
import logging
from datetime import datetime
import traceback
from aiogram.exceptions import TelegramNetworkError, TelegramServerError

from alembic.util import msg
import colorama
from dotenv import load_dotenv

load_dotenv()

LOGLEVEL = os.environ.get('LOGLEVEL')
TRACEBACK_LOG = os.environ.get('TRACEBACK_LOG', 'rina.log')

colorama.init(autoreset=True)

NETWORK_EXCEPTIONS = (
    TelegramNetworkError,
    TelegramServerError
)

class ApplicationStatus:
    def __init__(self):
        self._ok = True
        self._network_exceptions_counter = 0
        self._unknown_exceptions_counter = 0
        self._last_network_exception_time = None

    def _handle_network_exception(self):
        if datetime.now().timestamp() - (self._last_network_exception_time or 0) > 60:
            self._network_exceptions_counter = 1
            self._last_network_exception_time = datetime.now().timestamp()
            return

        self._network_exceptions_counter += 1
        self._last_network_exception_time = datetime.now().timestamp()

        if self._network_exceptions_counter >= 5:
            self._ok = False

    def _handle_unknown_exception(self):
        if self._unknown_exceptions_counter >= 5:
            self._ok = False

        self._unknown_exceptions_counter += 1

    def _check_exception(self, exc_type, exc_value, exc_traceback):
        with open(TRACEBACK_LOG, "a") as f:
            formatted_tb = traceback.format_tb(exc_traceback)
            splitted_tb = "\t".join(formatted_tb)

            f.write(f"Exception occurred at {datetime.now().isoformat()}:\n")
            f.write(f"\t{exc_type.__name__}: {str(exc_value)}\n")
            f.write(f"\t{splitted_tb}\n\n")
        
        if exc_type is None:
            self._handle_unknown_exception()
            return

        if issubclass(exc_type, NETWORK_EXCEPTIONS):
            self._handle_network_exception()
        else:
            self._ok = False

    def exception_handler(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        self._check_exception(exc_type, exc_value, exc_traceback)

    def async_exception_handler(self, loop, context):
        exc = context.get("exception")
        if exc is None:
            self._handle_unknown_exception()
            return

        exc_type = type(exc)
        exc_value = exc
        exc_traceback = exc.__traceback__

        self._check_exception(exc_type, exc_value, exc_traceback)

    @property
    def ok(self):
        return self._ok


application_status = ApplicationStatus()


class LoggingHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def emit(self, record):
        if record.exc_info and record.levelno >= logging.ERROR:
            exc_type, exc_value, exc_traceback = record.exc_info

            if exc_type is not None:
                application_status.exception_handler(exc_type, exc_value, exc_traceback)

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