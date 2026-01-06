import sys

from loguru import logger


def setup_logger(log_file):
    logger.remove()
    fmt = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    logger.add(sys.stdout, level="INFO", format=fmt)
    logger.add(
        log_file,
        level="INFO",
        format=fmt,
        rotation="10 MB",
        retention="10 days",
        encoding="utf-8",
    )
