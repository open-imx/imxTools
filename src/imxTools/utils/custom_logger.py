import sys

from loguru import logger


def log_filter(record):
    return record["level"].name in ["SUCCESS", "ERROR"]


logger.remove(0)
logger.add(sys.stdout, level="DEBUG")  # , filter=log_filter)
