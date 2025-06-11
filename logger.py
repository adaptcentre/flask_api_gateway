import os
import logging
from logging.handlers import RotatingFileHandler


def get_logger(logger_name, log_directory="./logs"):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler(os.path.join(log_directory, f"{logger_name}.log"))
    log_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(log_formatter)
    file_handler.setFormatter(log_formatter)

    # add log handler to logger object
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger
