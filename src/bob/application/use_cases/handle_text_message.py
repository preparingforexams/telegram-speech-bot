import logging
from dataclasses import dataclass

from injector import inject

from bob.application import ports
from bob.domain.model import TextMessage

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class HandleTextMessage:
    telegram_uploader: ports.TelegramUploader

    async def __call__(self, message: TextMessage) -> None:
        _LOG.info("Handling text message %d", message.id)
        # TODO: implement
