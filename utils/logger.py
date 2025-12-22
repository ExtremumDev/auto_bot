from datetime import datetime

import logging

import os

from pathlib import Path


def setup_logger() -> None:
    os.makedirs('logging', exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        filename=Path(__file__).parent.parent / f"logging/{datetime.today().date()}.log",
        filemode='a+',
        format="%(name)s %(asctime)s %(levelname)s %(message)s",
    )

    logging.getLogger("tg_bot").addHandler(logging.StreamHandler())

def get_bot_logger():
    return logging.getLogger("tgbot")
