import os

from botify import __version__, __codename__
from logger import logger
import utils

from dotenv import load_dotenv

def main():
    logger.debug("Loading environment")
    load_dotenv()

    tg_api_key = os.environ.get("TG_API_KEY")
    tw_cred_user = os.environ.get("TW_USER")
    tw_cred_pass = os.environ.get("TW_PASSWD")

    if None in [tg_api_key, tw_cred_pass, tw_cred_user]:
        logger.critical("Envirinment variables could not be fetched")
        exit(-1)

    utils.print_info()
    logger.info("Starting up")

if __name__ == "__main__":
    main()