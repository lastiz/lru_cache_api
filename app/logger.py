import enum
import logging
from functools import cache


class LogLevel(enum.StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@cache
def get_logger(name: str, level: LogLevel, log_format: str, logs_path: str) -> logging.Logger:

    logger = logging.getLogger(name)
    formatter = logging.Formatter(log_format)
    logger.setLevel(level)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(f"{logs_path}/{name}.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
