from typing import Callable
from loguru import logger

from loaded_env import get_variables

from functools import wraps

import os
import sys


def getLogger(name: str, *args, **kwargs):
    os.makedirs("logs", exist_ok=True)
    logger.remove()

    log_format = f"<green>{{time:{get_variables().LOG_DATETIME_FORMAT}}}</green> | {get_variables().LOG_MESSAGE_FORMAT}"
    logger.add(
        f"logs/{name}.log",
        format=log_format,
        rotation="1 MB",
        retention=7,
        compression="gz",
        encoding="utf-8",
    )
    if get_variables().LOG_TO_CONSOLE:
        logger.add(
            sys.stdout,
            format=log_format
        )

    return logger.bind(name=name)

GLOBAL_LOGGER = getLogger("enquiry_automation_service")
