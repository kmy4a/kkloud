from logging import Formatter
from logging import getLogger
from logging.handlers import RotatingFileHandler
import os


LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)


_formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
_handler = RotatingFileHandler(f"{LOG_DIR}/operations.log", maxBytes=1024*1024*5, backupCount=5)
_handler.setFormatter(_formatter)
logger = getLogger(__name__)
logger.setLevel("INFO")
logger.addHandler(_handler)
