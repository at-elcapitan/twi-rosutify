from dotenv import load_dotenv

from .configuration import ConfigurationEnv, CriticalEnvVarLoadException
from .static import ENV_VARIABLES
from .logger import logger
from . import utils

def main():
    load_dotenv()

    try:
        configuration = ConfigurationEnv(ENV_VARIABLES)
    except CriticalEnvVarLoadException as e:
        logger.critical(e)
        exit(-1)

    utils.print_info()
    logger.info("Starting up")


if __name__ == "__main__":
    main()