

import logging
from logging.handlers import RotatingFileHandler

filename = "proxy_reader.log"
logging_format = logging.Formatter(
    "%(levelname)s:[%(filename)s:%(lineno)s]:%(asctime)s: %(message)s")
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_format)
file_handler = RotatingFileHandler(filename, mode='a', maxBytes=5 * 1024 * 1024,
                                   backupCount=2, encoding="utf-8", delay=False)
file_handler.setFormatter(logging_format)

logger.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)
console_handler.setLevel(logging.DEBUG)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
