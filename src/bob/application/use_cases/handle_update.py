import logging
from dataclasses import dataclass

import pendulum
from injector import inject

from bob.application import ports, repos

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class HandleTextMessage:
    telegram_uploader: ports.TelegramUploader

    async def __call__(self) -> None:
        pass
